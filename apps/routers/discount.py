from fastapi import APIRouter, Response, Depends, Form, status
from sqlalchemy.orm import Session
from apps import database, models, pengaturan
from pydantic import BaseModel
import time

get_db = database.get_db
router = APIRouter(tags=['DISCOUNT SERVICE'])


class CreateDiscount(BaseModel):
    name: str
    nominal: int
    type_disc: int
    toko_id: int

    class Config:
        orm_mode = True


class EditDiscount(BaseModel):
    name: str
    nominal: int
    type_disc: int
    disc_id: int

    class Config:
        orm_mode = True


class DiscountID(BaseModel):
    disc_id: int

    class Config:
        orm_mode = True


@router.post('/discount')
async def create_discount(
        response: Response,
        req: CreateDiscount,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data_toko = db.query(models.Toko).filter(models.Toko.id == req.toko_id).first()
        createdAt = int(round(time.time() * 1000))

        new_disc = models.Discount(name=req.name, nominal=req.nominal, type_disc=req.type_disc, createdAt=createdAt,
                                   is_deleted=0)
        data_toko.discount.append(new_disc)

        db.add(new_disc)
        db.commit()
        db.refresh(new_disc)
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created discount"
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        new_disc = None
    return {
        "status_code": status_code,
        "msg": msg,
        "data": new_disc
    }


@router.put('/discount')
async def edit_discount(
        response: Response,
        req: EditDiscount,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Discount).filter(models.Discount.id == req.disc_id)
        data.update({
            "name": req.name,
            "nominal": req.nominal,
            "type_disc": req.type_disc,
        })
        db.commit()
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success edit discount"
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


@router.patch('/discount')
async def delete_discount(response: Response,
                          req: DiscountID,
                          db: Session = Depends(get_db),
                          token: str = Depends(pengaturan.oauth2_scheme),
                          ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Discount).filter(models.Discount.id == req.disc_id)

        data.update({
            "is_deleted": 1,
        })
        db.commit()
        msg = "Success delete discount"
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.get('/discount/{id}')
async def detail_discount(id: int,
                             response: Response,
                             db: Session = Depends(get_db),
                             token: str = Depends(pengaturan.oauth2_scheme)):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Discount).filter(models.Discount.id == id).first()
        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success get detail discount"
    except:
        data = None
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data
    }
