from fastapi import APIRouter, Response, Depends, Form, status
from sqlalchemy.orm import Session
from apps import database, models, pengaturan
from pydantic import BaseModel
import time

get_db = database.get_db
router = APIRouter(tags=['ORDER LABEL SERVICE'])


class CreateOrderLabel(BaseModel):
    name: str
    desc: str
    toko_id: int

    class Config:
        orm_mode = True


class EditOrderLabel(BaseModel):
    name: str
    desc: str
    label_order_id: int

    class Config:
        orm_mode = True


class OrderLabelID(BaseModel):
    label_order_id: int

    class Config:
        orm_mode = True


@router.post('/labelorder')
async def create_order_label(
        response: Response,
        req: CreateOrderLabel,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data_toko = db.query(models.Toko).filter(models.Toko.id == req.toko_id).first()
        createdAt = int(round(time.time() * 1000))

        new_order_label = models.LabelOrder(name=req.name, desc=req.desc, createdAt=createdAt, is_deleted=0)
        data_toko.labelorder.append(new_order_label)

        db.add(new_order_label)
        db.commit()
        db.refresh(new_order_label)
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created label order"
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        new_order_label = None
    return {
        "status_code": status_code,
        "msg": msg,
        "data": new_order_label
    }


@router.put('/labelorder')
async def edit_order_label(
        response: Response,
        req: EditOrderLabel,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.LabelOrder).filter(models.LabelOrder.id == req.label_order_id)
        data.update({
            "name": req.name,
            "desc": req.desc,
        })
        db.commit()
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success edit label order"
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


@router.patch('/labelorder')
async def delete_order_label(response: Response,
                             req: OrderLabelID,
                             db: Session = Depends(get_db),
                             token: str = Depends(pengaturan.oauth2_scheme),
                             ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.LabelOrder).filter(models.LabelOrder.id == req.label_order_id)

        data.update({
            "is_deleted": 1,
        })
        db.commit()
        msg = "Success delete order label"
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.get('/labelorder/{id}')
async def detail_order_label(id: int,
                             response: Response,
                             db: Session = Depends(get_db),
                             token: str = Depends(pengaturan.oauth2_scheme)):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.LabelOrder).filter(models.LabelOrder.id == id).first()
        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success get detail order label"
    except:
        data = None
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data
    }
