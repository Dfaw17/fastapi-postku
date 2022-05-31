from fastapi import APIRouter, Response, Depends, Form, status
from sqlalchemy.orm import Session
from apps import database, models, pengaturan
from pydantic import BaseModel
import time

get_db = database.get_db
router = APIRouter(tags=['PAJAK SERVICE'])


class CreatePajak(BaseModel):
    name: str
    nominal: int
    type_pajak: int
    toko_id: int

    class Config:
        orm_mode = True


class EditPajak(BaseModel):
    name: str
    nominal: int
    type_pajak: int
    pajak_id: int

    class Config:
        orm_mode = True


class PajakID(BaseModel):
    pajak_id: int

    class Config:
        orm_mode = True


@router.post('/pajak')
async def create_pajak(
        response: Response,
        req: CreatePajak,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data_toko = db.query(models.Toko).filter(models.Toko.id == req.toko_id).first()
        createdAt = int(round(time.time() * 1000))

        new_pajak = models.Pajak(name=req.name, nominal=req.nominal, type_pajak=req.type_pajak, createdAt=createdAt,
                                 is_deleted=0)
        data_toko.pajak.append(new_pajak)

        db.add(new_pajak)
        db.commit()
        db.refresh(new_pajak)
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created pajak"
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        new_pajak = None
    return {
        "status_code": status_code,
        "msg": msg,
        "data": new_pajak
    }


@router.put('/pajak')
async def edit_pajak(
        response: Response,
        req: EditPajak,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Pajak).filter(models.Pajak.id == req.pajak_id)
        data.update({
            "name": req.name,
            "nominal": req.nominal,
            "type_pajak": req.type_pajak,
        })
        db.commit()
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success edit pajak"
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


@router.patch('/pajak')
async def delete_pajak(response: Response,
                       req: PajakID,
                       db: Session = Depends(get_db),
                       token: str = Depends(pengaturan.oauth2_scheme),
                       ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Pajak).filter(models.Pajak.id == req.pajak_id)

        data.update({
            "is_deleted": 1,
        })
        db.commit()
        msg = "Success delete pajak"
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.get('/pajak/{id}')
async def detail_pajak(id: int,
                       response: Response,
                       db: Session = Depends(get_db),
                       token: str = Depends(pengaturan.oauth2_scheme)):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Pajak).filter(models.Pajak.id == id).first()
        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success get detail pajak"
    except:
        data = None
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data
    }
