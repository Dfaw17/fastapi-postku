from datetime import datetime
from typing import Optional, List
import boto3
import sqlalchemy
from fastapi import APIRouter, Response, Depends, Form, status, UploadFile, File
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from apps import database, models, pengaturan
from pydantic import BaseModel
import time
from apps.database import engine

get_db = database.get_db
router = APIRouter(tags=['TRANSACTION SERVICE'])


class CreateCart(BaseModel):
    account_id: int
    toko_id: int
    disc_id: Optional[int]
    pajak_id: Optional[int]
    ordertype_id: Optional[int]
    labelorder_id: Optional[int]
    table_id: Optional[int]
    customer_id: Optional[int]
    servicefee_id: List[Optional[int]]
    cart_item_menu_id: List[int]
    cart_item_qty: List[int]
    cart_item_disc_id: List[Optional[int]]

    class Config:
        orm_mode = True


class DeleteCart(BaseModel):
    cart_id: int

    class Config:
        orm_mode = True


class CreateTrx(BaseModel):
    cart_id: int
    payment_id: int
    uang_bayar: int
    uang_kembalian: int


@router.get('/transaction')
async def get_list_transaction(start_date: int,
                               end_date: int,
                               toko_id: int,
                               db: Session = Depends(get_db),
                               token: str = Depends(pengaturan.oauth2_scheme),
                               ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Transaction).filter(models.Transaction.toko_id == toko_id).filter(
            models.Transaction.createdAt.between(start_date, end_date)).all()
        msg = "Success get transaction list"
        status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data,
    }


@router.get('/transaction/{id}')
async def get_transaction_detail(id: str,
                                 response: Response,
                                 db: Session = Depends(get_db),
                                 token: str = Depends(pengaturan.oauth2_scheme)):
    try:
        pengaturan.verify_token(token)
        trx = db.query(models.Transaction).filter(models.Transaction.reff_code == id).first()
        data = db.query(models.Cart).filter(models.Cart.id == trx.cart_id).first()

        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success get detail transaction"
        resp = {
            "transaction": trx,
            "cart": data,
            "items": db.query(models.CartItem).filter(models.CartItem.cart_id == trx.cart_id).all(),
            "kasir": db.query(models.Account).filter(models.Account.id == data.account_id).first(),
            "toko": db.query(models.Toko).filter(models.Toko.id == data.toko_id).first(),
            "discount_cart": db.query(models.Discount).filter(models.Discount.id == data.disc_id).first(),
            "pajak": db.query(models.Pajak).filter(models.Pajak.id == data.pajak_id).first(),
            "ordet_type": db.query(models.OrderType).filter(models.OrderType.id == data.ordertype_id).first(),
            "label_order": db.query(models.LabelOrder).filter(models.LabelOrder.id == data.labelorder_id).first(),
            "meja": db.query(models.Table).filter(models.Table.id == data.table_id).first(),
            "customer": db.query(models.Customer).filter(models.Customer.id == data.customer_id).first(),
            "service_fee": data.servicefee.all(),
        }
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        resp = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": resp,
    }


@router.post('/transaction')
async def create_transaction(
        response: Response,
        req: CreateTrx,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        # =========================================== CREATE TRX ===========================================
        createdAt = int(round(time.time() * 1000))
        now = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        ModelsCart = db.query(models.Cart).filter(models.Cart.id == req.cart_id)
        ModelsCartItem = db.query(models.CartItem).filter(models.CartItem.cart_id == req.cart_id)
        ModelsPayment = db.query(models.Payment).filter(models.Payment.id == req.payment_id)
        ModelsToko = db.query(models.Toko).filter(models.Toko.id == ModelsCart.first().toko_id)
        ModelsAccount = db.query(models.Account).filter(models.Account.id == ModelsCart.first().account_id)
        ModeTable = db.query(models.Table).filter(models.Table.id == ModelsCart.first().table_id)
        ModelsCartItems = db.query(models.CartItem).filter(models.CartItem.cart_id == req.cart_id)

        new_trx = models.Transaction(
            reff_code=ModelsCart.first().cart_code,
            sub_total_price=ModelsCart.first().sub_total_price,
            total_pajak=ModelsCart.first().total_pajak,
            grand_total_price=ModelsCart.first().grand_total_price,
            uang_bayar=req.uang_bayar,
            uang_kembalian=req.uang_kembalian,
            createdAt=createdAt,
            is_cancel=0,
            is_settlement=0,
        )
        payment = ModelsPayment.first()
        payment.transaction.append(new_trx)

        cart = ModelsCart.first()
        cart.transaction.append(new_trx)

        toko = ModelsToko.first()
        toko.transaction.append(new_trx)

        kasir = ModelsAccount.first()
        kasir.transaction.append(new_trx)

        db.add(new_trx)
        db.commit()
        db.refresh(new_trx)

        # ================================ UPDATE CART, TABLE, CART ITEM ================================
        ModelsCartItem.update({
            "ordered": 1,
        })
        ModelsCart.update({
            "ordered": 1,
        })
        ModeTable.update({
            "is_booked": 0,
        })
        db.commit()

        # ================================ STOCK, HISTORY_STOCK ================================
        items = len(ModelsCart.first().cartitem)
        for i in range(items):
            menu_id = ModelsCartItems.all()[i].menu_id
            ModelsMenu = db.query(models.Menu).filter(models.Menu.id == menu_id)
            qty = ModelsCartItems.all()[i].qty
            stock = ModelsMenu.first().current_stock

            if stock is None:
                pass
            else:
                # ================================ UPDATE STOCK MENU ================================
                current_stock = int(stock) - int(qty)
                ModelsMenu.update({
                    "current_stock": current_stock,
                })
                db.commit()

                # ================================ UPDATE HISTORY STOCK ================================
                new_menu_stock = models.HistoryStockMenu(
                    adjustment_stock=qty,
                    type=4,
                    note=f'Penjualan item pada tanggal {now} ',
                    menu_id=menu_id,
                    createdAt=createdAt
                )
                db.add(new_menu_stock)
                db.commit()
                db.refresh(new_menu_stock)

        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created transaction"
        data_response = {
            "kasir": ModelsCart.first().account.name,
            "toko": ModelsCart.first().toko.name,
            "tipe_pembayaran": ModelsPayment.first().paymnet,
            "grand_total": ModelsCart.first().grand_total_price,
            "uang_bayar": req.uang_bayar,
            "uang_kembalian": req.uang_kembalian,
        }
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data_response = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data_response,
    }


@router.post('/cart')
async def create_cart(
        response: Response,
        req: CreateCart,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        # =========================================== CREATE CART ===========================================
        createdAt = int(round(time.time() * 1000))
        cart_code = "PKU-" + datetime.today().strftime('%Y%m%d%H%M%S')
        ModelsCustomer = db.query(models.Customer).filter(models.Customer.id == req.customer_id)
        ModelsOrderType = db.query(models.OrderType).filter(models.OrderType.id == req.ordertype_id)
        ModelsLabelOrder = db.query(models.LabelOrder).filter(models.LabelOrder.id == req.labelorder_id)
        ModelsTable = db.query(models.Table).filter(models.Table.id == req.table_id)
        ModelsDiscount = db.query(models.Discount).filter(models.Discount.id == req.disc_id)
        ModelsPajak = db.query(models.Pajak).filter(models.Pajak.id == req.pajak_id)
        ModelsToko = db.query(models.Toko).filter(models.Toko.id == req.toko_id)
        ModelsAccount = db.query(models.Account).filter(models.Account.id == req.account_id)

        new_cart = models.Cart(
            cart_code=cart_code,
            createdAt=createdAt,
            is_canceled=0,
            ordered=0,
        )
        for i in range(len(req.servicefee_id)):
            data_servicefee = db.query(models.ServiceFee).filter(models.ServiceFee.id == req.servicefee_id[i]).first()
            new_cart.servicefee.append(data_servicefee)

        if req.customer_id is None:
            pass
        else:
            data_customer = ModelsCustomer.first()
            data_customer.cart.append(new_cart)

        if req.ordertype_id is None:
            pass
        else:
            data_ordertype = ModelsOrderType.first()
            data_ordertype.cart.append(new_cart)

        if req.labelorder_id is None:
            pass
        else:
            data_labelorder = ModelsLabelOrder.first()
            data_labelorder.cart.append(new_cart)

        if req.table_id is None:
            pass
        else:
            data_table = ModelsTable.first()
            data_table.cart.append(new_cart)

            ModelsTable.update({
                "is_booked": 1,
            })
            db.commit()

        if req.disc_id is None:
            pass
        else:
            data_disc = ModelsDiscount.first()
            data_disc.cart.append(new_cart)

        if req.pajak_id is None:
            pass
        else:
            data_pajak = ModelsPajak.first()
            data_pajak.cart.append(new_cart)

        data_toko = ModelsToko.first()
        data_toko.cart.append(new_cart)
        data_account = ModelsAccount.first()
        data_account.cart.append(new_cart)

        db.add(new_cart)
        db.commit()
        db.refresh(new_cart)
        # =========================================== CREATE CART ITEM ===========================================
        for i in range(len(req.cart_item_menu_id)):
            data_menu = db.query(models.Menu).filter(models.Menu.id == req.cart_item_menu_id[i]).first()
            data_disc_cart_item = db.query(models.Discount).filter(
                models.Discount.id == req.cart_item_disc_id[i]).first()

            cart_id = new_cart.id
            qty = req.cart_item_qty[i]
            price = data_menu.harga_jual * req.cart_item_qty[i]
            hpp = data_menu.harga_asli

            # CHECK DISC PER-ITEM
            if data_disc_cart_item is None:
                total_disc = 0
            else:
                # CHECK DISC TYPE
                if data_disc_cart_item.type_disc == 1:
                    # CHECK PRICE & DISC NOMINAL
                    if price <= data_disc_cart_item.nominal:
                        total_disc = price
                    else:
                        total_disc = price - data_disc_cart_item.nominal
                else:
                    if price <= data_disc_cart_item.nominal:
                        total_disc = price
                    else:
                        total_disc = price * data_disc_cart_item.nominal / 100

            grand_total_price = price - total_disc
            menu_kat_id = data_menu.kategori_id

            new_cart_item = models.CartItem(
                cart_id=cart_id,
                qty=qty,
                ordered=0,
                price=price,
                hpp=hpp,
                total_disc=total_disc,
                grand_total_price=grand_total_price,
                is_cancel=0,
                menu_kat_id=menu_kat_id,
                createdAt=createdAt
            )
            if data_disc_cart_item is None:
                pass
            else:
                data_disc_cart_item.cartitem.append(new_cart_item)
            data_menu.cartitem.append(new_cart_item)
            data_toko.cartitem.append(new_cart_item)
            db.add(new_cart_item)
            db.commit()
            db.refresh(new_cart_item)

        # =========================================== UPDATE CART ===========================================
        total_price_item = db.query(func.sum(models.CartItem.grand_total_price)).filter(
            models.CartItem.cart_id == new_cart.id).scalar()

        if req.disc_id is None:
            total_disc = 0
        else:
            data_disc = ModelsDiscount.first()
            if data_disc.type_disc == 1:
                total_disc = total_price_item - data_disc.nominal
            else:
                total_disc = total_price_item * data_disc.nominal / 100

        sub_total_price = total_price_item - total_disc

        if req.pajak_id is None:
            total_pajak = 0
        else:
            data_pajak = ModelsPajak.first()
            if data_pajak.type_pajak == 1:
                total_pajak = sub_total_price - data_pajak.nominal
            else:
                total_pajak = sub_total_price * data_pajak.nominal / 100

        if len(req.servicefee_id) == 0:
            total_service_fee = 0
        else:
            total_service_fee = db.query(func.sum(models.ServiceFee.nominal)).filter(
                models.ServiceFee.id.in_(req.servicefee_id)).scalar()

        grand_total_price = int(sub_total_price) + int(total_pajak) + int(total_service_fee)
        total_item = len(req.cart_item_menu_id)

        cart_update = db.query(models.Cart).filter(models.Cart.id == new_cart.id)
        cart_update.update({
            "total_price_item": total_price_item,
            "total_disc": total_disc,
            "sub_total_price": sub_total_price,
            "total_pajak": total_pajak,
            "total_service_fee": total_service_fee,
            "grand_total_price": grand_total_price,
            "total_item": total_item,
        })
        db.commit()

        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created cart"
        data_response = {
            "cart": cart_update.first(),
            "items": db.query(models.CartItem).filter(models.CartItem.cart_id == new_cart.id).all(),
            "kasir": db.query(models.Account).filter(models.Account.id == req.account_id).first(),
            "toko": db.query(models.Toko).filter(models.Toko.id == req.toko_id).first(),
            "discount_cart": db.query(models.Discount).filter(models.Discount.id == req.disc_id).first(),
            "pajak": db.query(models.Pajak).filter(models.Pajak.id == req.pajak_id).first(),
            "ordet_type": db.query(models.OrderType).filter(models.OrderType.id == req.ordertype_id).first(),
            "label_order": db.query(models.LabelOrder).filter(models.LabelOrder.id == req.labelorder_id).first(),
            "meja": db.query(models.Table).filter(models.Table.id == req.table_id).first(),
            "customer": db.query(models.Customer).filter(models.Customer.id == req.table_id).first(),
            "service_fee": db.query(models.ServiceFee).filter(
                models.ServiceFee.id.in_(req.servicefee_id)).all(),
        }
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data_response = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data_response,
    }


@router.delete('/cart')
async def delete_cart(
        response: Response,
        req: DeleteCart,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        cart = db.query(models.Cart).filter(models.Cart.id == req.cart_id).first()
        cart_items = cart.cartitem

        for i in cart_items:
            db.delete(i)
            db.commit()

        db.delete(cart)
        db.commit()

        query = db.execute(f'SELECT * FROM cart_servicefee WHERE cart_id = {req.cart_id}')
        for i in query:
            query_delete = text(f'DELETE FROM cart_servicefee WHERE id = {i.id}')
            db.execute(query_delete)

        sql_query = sqlalchemy.text(f"DELETE FROM cart_servicefee WHERE cart_id = {req.cart_id}")
        result = engine.execute(sql_query)

        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success deleted cart"
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.get('/cart/toko')
async def get_cart_list(toko_id: int,
                        response: Response,
                        db: Session = Depends(get_db),
                        token: str = Depends(pengaturan.oauth2_scheme)):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Cart).filter(models.Cart.toko_id == toko_id).filter(models.Cart.ordered == 0).all()

        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success deleted cart"
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data,
    }


@router.get('/cart/{id}')
async def get_cart_detail(id: int,
                          response: Response,
                          db: Session = Depends(get_db),
                          token: str = Depends(pengaturan.oauth2_scheme)):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Cart).filter(models.Cart.id == id).first()

        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success deleted cart"
        resp = {
            "cart": data,
            "items": db.query(models.CartItem).filter(models.CartItem.cart_id == id).all(),
            "kasir": db.query(models.Account).filter(models.Account.id == data.account_id).first(),
            "toko": db.query(models.Toko).filter(models.Toko.id == data.toko_id).first(),
            "discount_cart": db.query(models.Discount).filter(models.Discount.id == data.disc_id).first(),
            "pajak": db.query(models.Pajak).filter(models.Pajak.id == data.pajak_id).first(),
            "ordet_type": db.query(models.OrderType).filter(models.OrderType.id == data.ordertype_id).first(),
            "label_order": db.query(models.LabelOrder).filter(models.LabelOrder.id == data.labelorder_id).first(),
            "meja": db.query(models.Table).filter(models.Table.id == data.table_id).first(),
            "customer": db.query(models.Customer).filter(models.Customer.id == data.customer_id).first(),
            "service_fee": data.servicefee.all(),
        }
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        resp = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": resp,
    }
