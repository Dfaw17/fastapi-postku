import time
from typing import Optional
import boto3
from fastapi import APIRouter, Response, Depends, Form, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from apps import database, models
from apps import pengaturan

get_db = database.get_db
router = APIRouter(tags=['CHANNEL TOPUP SERVICE'])


@router.post('/channeltopup')
async def create_channel_topup(response: Response,
                               db: Session = Depends(get_db),
                               token: str = Depends(pengaturan.oauth2_scheme),
                               jenis_pembayaran: str = Form(...),
                               nama: str = Form(...),
                               nomer: str = Form(...),
                               photo_logo: UploadFile = File(None),
                               ):
    try:
        pengaturan.verify_token(token)
        createdAt = int(round(time.time() * 1000))
        s3 = boto3.resource('s3', aws_access_key_id=pengaturan.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=pengaturan.AWS_SECRET_ACCESS_KEY)
        bucket = s3.Bucket(pengaturan.S3_BUCKET_NAME)
        if photo_logo is not None:
            bucket.upload_fileobj(photo_logo.file, photo_logo.filename,
                                  ExtraArgs={"ACL": "public-read", "ContentType": photo_logo.content_type})
            photo_logo_url = f"https://{pengaturan.S3_BUCKET_NAME}.s3.amazonaws.com/{photo_logo.filename}"
            photo_logo = photo_logo.filename
        else:
            photo_logo_url = None
            photo_logo = None

        new_channel_topup = models.ChannelTopup(jenis_pembayaran=jenis_pembayaran,
                                                nama=nama,
                                                nomer=nomer,
                                                photo_logo=photo_logo,
                                                photo_logo_url=photo_logo_url,
                                                createdAt=createdAt)
        db.add(new_channel_topup)
        db.commit()
        db.refresh(new_channel_topup)
        msg = "Success create channel topup"
        status_code = response.status_code = status.HTTP_200_OK
        data_resp = None

    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data_resp = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data_resp,
    }


@router.get('/channeltopup')
async def get_channel_topup(response: Response,
                            db: Session = Depends(get_db),
                            token: str = Depends(pengaturan.oauth2_scheme),
                            ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.ChannelTopup).all()
        msg = "Success get channel topup"
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
