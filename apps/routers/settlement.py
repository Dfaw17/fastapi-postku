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
router = APIRouter(tags=['SETTLEMENT SERVICE'])


class CreateSettlement(BaseModel):
    grand_total_settlement: float
    toko_id: int

    class Config:
        orm_mode = True


@router.get('/checksettlement')
async def check_settlement(toko_id: int,
                           db: Session = Depends(get_db),
                           token: str = Depends(pengaturan.oauth2_scheme),
                           ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Transaction).filter(models.Transaction.toko_id == toko_id).filter(
            models.Transaction.is_settlement == 0).all()

        grand_total_settlement = db.query(func.sum(models.Transaction.grand_total_price)).filter(
            models.Transaction.toko_id == toko_id).filter(
            models.Transaction.is_settlement == 0).scalar()
        msg = "Success get settlement toko"
        status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data = None
        grand_total_settlement = None

    return {
        "status_code": status_code,
        "msg": msg,
        "grand_total_settlement": grand_total_settlement,
        "data": data,
    }


@router.post('/settlement')
async def toko_request_settlement(req: CreateSettlement,
                                  token: str = Depends(pengaturan.oauth2_scheme),
                                  db: Session = Depends(get_db),
                                  ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Transaction).filter(models.Transaction.toko_id == req.toko_id).filter(
            models.Transaction.is_settlement == 0)
        createdAt = int(round(time.time() * 1000))
        settlement_code = "STL-" + datetime.today().strftime('%Y%m%d%H%M%S')

        new_settlement = models.Settlement(name=settlement_code, status_settelement=1,
                                           grand_total_settlement=req.grand_total_settlement, toko_id=req.toko_id,
                                           createdAt=createdAt)
        for i in range(len(data.all())):
            data.all()[i].settlement.append(new_settlement)

        db.add(new_settlement)
        db.commit()
        db.refresh(new_settlement)

        # ================================ UPDATE CART, TABLE, CART ITEM ================================
        data.update({
            "is_settlement": 1,
        })
        db.commit()

        msg = "Success request settlement"
        status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg
    }


@router.get('/settlement')
async def get_list_settlement(toko_id: int,
                              status_settelement: int,
                              db: Session = Depends(get_db),
                              token: str = Depends(pengaturan.oauth2_scheme),
                              ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Settlement).filter(models.Settlement.toko_id == toko_id).filter(
            models.Settlement.status_settelement == status_settelement).all()

        msg = "Success get settlement list"
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


@router.get('/settlement/{id}')
async def get_detail_settlement(id: int,
                                db: Session = Depends(get_db),
                                token: str = Depends(pengaturan.oauth2_scheme),
                                ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Settlement).filter(models.Settlement.id == id).first()
        trx = data.transaction.all()
        msg = "Success get settlement detail"
        status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data = None
        trx = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data,
        "list_transaksi": trx,
    }


@router.put('/settlement')
async def menu_edit(response: Response,
                    db: Session = Depends(get_db),
                    token: str = Depends(pengaturan.oauth2_scheme),
                    settlement_id: str = Form(...),
                    photo_bukti: UploadFile = File(None),
                    ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Settlement).filter(models.Settlement.id == settlement_id)

        s3 = boto3.resource('s3', aws_access_key_id=pengaturan.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=pengaturan.AWS_SECRET_ACCESS_KEY)
        bucket = s3.Bucket(pengaturan.S3_BUCKET_NAME)
        if photo_bukti is not None:
            bucket.upload_fileobj(photo_bukti.file, photo_bukti.filename,
                                  ExtraArgs={"ACL": "public-read", "ContentType": photo_bukti.content_type})
            photo_bukti_url = f"https://{pengaturan.S3_BUCKET_NAME}.s3.amazonaws.com/{photo_bukti.filename}"
            photo_bukti = photo_bukti.filename
        else:
            photo_bukti_url = data.first().photo_bukti_url
            photo_bukti = data.first().photo_bukti

        data.update({
            "photo_bukti_url": photo_bukti_url,
            "photo_bukti": photo_bukti,
            "status_settelement": 2,
        })

        db.commit()
        msg = "Success accept settlement toko"
        status_code = response.status_code = status.HTTP_200_OK
        data_resp = data.first()
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data_resp = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data_resp,
    }


@router.get('/admin/settlement')
async def get_list_settlement(db: Session = Depends(get_db),
                              token: str = Depends(pengaturan.oauth2_scheme),
                              ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Settlement).filter(models.Settlement.status_settelement == 1).all()

        msg = "Success get settlement list"
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
