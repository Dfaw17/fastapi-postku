import boto3
from fastapi import APIRouter, Response, Depends, Form, status, UploadFile, File
from sqlalchemy.orm import Session
from apps import database, models, pengaturan
from pydantic import BaseModel
import time

get_db = database.get_db
router = APIRouter(tags=['KRITIK SARAN SERVICE'])


class CreateKritikSaran(BaseModel):
    label: str
    body: str
    account_id: int

    class Config:
        orm_mode = True


@router.post('/kritiksaran')
async def create_order_label(
        response: Response,
        req: CreateKritikSaran,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data_account = db.query(models.Account).filter(models.Account.id == req.account_id).first()
        createdAt = int(round(time.time() * 1000))
        new_ks = models.KritikSaran(label=req.label, body=req.body, createdAt=createdAt)
        data_account.kritiksaran.append(new_ks)

        db.add(new_ks)
        db.commit()
        db.refresh(new_ks)
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created kritik saran"
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        new_ks = None
    return {
        "status_code": status_code,
        "msg": msg,
        "data": new_ks
    }


@router.get('/kritiksaran')
async def get_kritik_saran(response: Response,
                           start_date: int,
                           end_date: int,
                           db: Session = Depends(get_db),
                           token: str = Depends(pengaturan.oauth2_scheme),
                           ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.KritikSaran).filter(models.KritikSaran.createdAt.between(start_date, end_date)).all()
        msg = "Success get kritik saran"
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
