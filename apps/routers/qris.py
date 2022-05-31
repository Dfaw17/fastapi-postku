from datetime import datetime
from typing import Optional, List, Dict
import boto3
import sqlalchemy
from fastapi import APIRouter, Response, Depends, Form, status, UploadFile, File
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from xendit import Xendit, QRCodeType

from apps import database, models, pengaturan
from pydantic import BaseModel
import time
from apps.database import engine

get_db = database.get_db
router = APIRouter(tags=['QRIS SERVICE'])

xnd_prod = "xnd_production_nfjAk6kENINyOobuWaOujS3aqfT4LwqW8rzAsvwBOSqD28tjJGYTsQRTqZakEPT"
xnd_dev = "xnd_development_27A0zquDKjORXcsXvv3XEnX00BBlwVlR97ZFQIfbA8TPNrZDa4VFaSzIDBUeem"
url_callback = "http://2d20-103-138-49-17.ap.ngrok.io/callback/qris"


# url_callback = "http://13.213.192.212:8000/api/qris/callback"


class CreateQris(BaseModel):
    cart_id: int


class external_id(BaseModel):
    external_id: str


class CreateCallback(BaseModel):
    event: str
    amount: int
    status: str
    qr_code: external_id


@router.get('/qris')
async def qris_callback_apps(
        response: Response,
        req: CreateQris,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        # =========================================== CREATE QRISS ===========================================
        ModelsCart = db.query(models.Cart).filter(models.Cart.id == req.cart_id)
        external_id = ModelsCart.first().cart_code
        ammount = ModelsCart.first().grand_total_price

        check_qris = db.query(models.CallbackXendit).filter(models.CallbackXendit.external_id == external_id).filter(
            models.CallbackXendit.ammount == ammount).first()

        if check_qris is None:
            status_code = response.status_code = status.HTTP_400_BAD_REQUEST
            msg = "Qris belum dibayar"
        else:
            status_code = response.status_code = status.HTTP_200_OK
            msg = "Qris berhasil dibayar"
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.post('/qris')
async def create_qris(
        response: Response,
        req: CreateQris,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        # =========================================== CREATE QRISS ===========================================
        ModelsCart = db.query(models.Cart).filter(models.Cart.id == req.cart_id)
        external_id = ModelsCart.first().cart_code
        ammount = ModelsCart.first().grand_total_price
        api_key = xnd_dev
        xendit_instance = Xendit(api_key=api_key)
        QRCode = xendit_instance.QRCode

        qriss = QRCode.create(
            external_id=external_id,
            type=QRCodeType.DYNAMIC,
            callback_url=url_callback,
            amount=ammount,
        )
        datas = {
            "id": qriss.id,
            "external_id": qriss.external_id,
            "amount": qriss.amount,
            "description": "",
            "qr_string": qriss.qr_string,
            "callback_url": qriss.callback_url,
            "type": qriss.type,
            "status": qriss.status,
            "created": qriss.created,
            "updated": qriss.updated,
            "metadata": None
        }

        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created qris"
        data_response = datas
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data_response = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data_response,
    }


@router.post('/callback/qris')
async def qris_callback_server(
        response: Response,
        req: CreateCallback,
        db: Session = Depends(get_db),
):
    try:
        # =========================================== CREATE QRISS ===========================================
        createdAt = int(round(time.time() * 1000))
        new_callback = models.CallbackXendit(
            event=req.event,
            external_id=req.qr_code.external_id,
            ammount=req.amount,
            status=req.status,
            createdAt=createdAt,
        )
        db.add(new_callback)
        db.commit()
        db.refresh(new_callback)

        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created callback qris"

        data_response = req
    except:
        msg = "Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data_response = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data_response,
    }


@router.get('/callback/qris')
async def check_server():
    return {
        "msg": "service callback xendit ready",
    }
