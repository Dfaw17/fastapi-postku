from fastapi import APIRouter, Response, Depends, Form, status
from sqlalchemy.orm import Session
from apps import database, models, pengaturan
from pydantic import BaseModel
import time

get_db = database.get_db
router = APIRouter(tags=['SERVICEFEE SERVICE'])


class CreateServiceFee(BaseModel):
    name: str
    nominal: int
    toko_id: int

    class Config:
        orm_mode = True


class ServiceFeeEdit(BaseModel):
    name: str
    nominal: int
    servicefee_id: int

    class Config:
        orm_mode = True


class ServiceFeeID(BaseModel):
    servicefee_id: int

    class Config:
        orm_mode = True


@router.post('/servicefee')
async def create_service_fee(
        response: Response,
        req: CreateServiceFee,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data_toko = db.query(models.Toko).filter(models.Toko.id == req.toko_id).first()
        createdAt = int(round(time.time() * 1000))

        new_sf = models.ServiceFee(name=req.name, nominal=req.nominal, createdAt=createdAt, is_deleted=0)
        data_toko.servicefee.append(new_sf)

        db.add(new_sf)
        db.commit()
        db.refresh(new_sf)
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created service fee"
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        new_sf = None
    return {
        "status_code": status_code,
        "msg": msg,
        "data": new_sf
    }


@router.put('/servicefee')
async def edit_service_fee(
        response: Response,
        req: ServiceFeeEdit,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.ServiceFee).filter(models.ServiceFee.id == req.servicefee_id)
        data.update({
            "name": req.name,
            "nominal": req.nominal
        })
        db.commit()
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success edit service fee"
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


@router.patch('/servicefee')
async def delete_service_fee(response: Response,
                             req: ServiceFeeID,
                             db: Session = Depends(get_db),
                             token: str = Depends(pengaturan.oauth2_scheme),
                             ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.ServiceFee).filter(models.ServiceFee.id == req.servicefee_id)

        data.update({
            "is_deleted": 1,
        })
        db.commit()
        msg = "Success delete service fee"
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.get('/servicefee/{id}')
async def detail_service_fee(id: int,
                       response: Response,
                       db: Session = Depends(get_db),
                       token: str = Depends(pengaturan.oauth2_scheme)):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.ServiceFee).filter(models.ServiceFee.id == id).first()
        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success get detail service fee"
    except:
        data = None
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data
    }
