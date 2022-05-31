import boto3
from fastapi import APIRouter, Response, Depends, Form, status, UploadFile, File
from sqlalchemy.orm import Session
from apps import database, models, pengaturan
from pydantic import BaseModel
import time

get_db = database.get_db
router = APIRouter(tags=['PAYMENT SERVICE'])


class CreatePayment(BaseModel):
    paymnet: str

    class Config:
        orm_mode = True


@router.post('/payment')
async def create_payment(
        response: Response,
        req: CreatePayment,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        createdAt = int(round(time.time() * 1000))

        new_payment = models.Payment(paymnet=req.paymnet, createdAt=createdAt)

        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created payment"
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        new_payment = None
    return {
        "status_code": status_code,
        "msg": msg,
        "data": new_payment
    }


@router.get('/payment')
async def get_payment(
        response: Response,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)

        data = db.query(models.Payment).all()

        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created payment"
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data = None
    return {
        "status_code": status_code,
        "msg": msg,
        "data": data
    }
