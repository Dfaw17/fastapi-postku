from fastapi import APIRouter, Response, Depends, Form, status
from sqlalchemy.orm import Session
from apps import database, models, pengaturan
from pydantic import BaseModel
import time

get_db = database.get_db
router = APIRouter(tags=['ORDER TYPE SERVICE'])


class CreateOrderType(BaseModel):
    name: str
    desc: str
    toko_id: int

    class Config:
        orm_mode = True


class EditOrderType(BaseModel):
    name: str
    desc: str
    id_order_type: int

    class Config:
        orm_mode = True


class OrderTypeID(BaseModel):
    id_order_type: int

    class Config:
        orm_mode = True


@router.post('/ordertype')
async def create_order_type(
        response: Response,
        req: CreateOrderType,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data_toko = db.query(models.Toko).filter(models.Toko.id == req.toko_id).first()
        createdAt = int(round(time.time() * 1000))

        new_order_type = models.OrderType(name=req.name, desc=req.desc, createdAt=createdAt, is_deleted=0)
        data_toko.ordertype.append(new_order_type)

        db.add(new_order_type)
        db.commit()
        db.refresh(new_order_type)
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created type order"
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        new_order_type = None
    return {
        "status_code": status_code,
        "msg": msg,
        "data": new_order_type
    }


@router.put('/ordertype')
async def edit_order_type(
        response: Response,
        req: EditOrderType,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.OrderType).filter(models.OrderType.id == req.id_order_type)
        data.update({
            "name": req.name,
            "desc": req.desc,
        })
        db.commit()
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success edit order type"
        data = req
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data = None
    return {
        "status_code": status_code,
        "msg": msg,
        "data": data
    }


@router.patch('/ordertype')
async def delete_order_type(response: Response,
                            req: OrderTypeID,
                            db: Session = Depends(get_db),
                            token: str = Depends(pengaturan.oauth2_scheme),
                            ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.OrderType).filter(models.OrderType.id == req.id_order_type)

        data.update({
            "is_deleted": 1,
        })
        db.commit()
        msg = "Success delete order type"
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.get('/ordertype/{id}')
async def detail_order_type(id: int,
                       response: Response,
                       db: Session = Depends(get_db),
                       token: str = Depends(pengaturan.oauth2_scheme)):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.OrderType).filter(models.OrderType.id == id).first()
        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success get detail order type"
    except:
        data = None
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data
    }
