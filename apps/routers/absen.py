import boto3
from fastapi import APIRouter, Response, Depends, Form, status, UploadFile, File
from sqlalchemy.orm import Session
from apps import database, models, pengaturan
from pydantic import BaseModel
import time

get_db = database.get_db
router = APIRouter(tags=['ABSEN SERVICE'])


@router.post('/absen')
async def create_absen(response: Response,
                       db: Session = Depends(get_db),
                       account_id: str = Form(...),
                       toko_id: str = Form(...),
                       photo_absen: UploadFile = File(None),
                       token: str = Depends(pengaturan.oauth2_scheme),
                       ):
    try:
        pengaturan.verify_token(token)
        createdAt = int(round(time.time() * 1000))

        data = db.query(models.Absen).filter(models.Absen.account_id == account_id).first()

        s3 = boto3.resource('s3', aws_access_key_id=pengaturan.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=pengaturan.AWS_SECRET_ACCESS_KEY)
        bucket = s3.Bucket(pengaturan.S3_BUCKET_NAME)

        if photo_absen is not None:
            bucket.upload_fileobj(photo_absen.file, photo_absen.filename,
                                  ExtraArgs={"ACL": "public-read", "ContentType": photo_absen.content_type})
            photo_absen_url = f"https://{pengaturan.S3_BUCKET_NAME}.s3.amazonaws.com/{photo_absen.filename}"
            photo_absen = photo_absen.filename
        else:
            photo_absen_url = None
            photo_absen = None

        if data is None:
            data_absen = models.Absen(photo_absen1=photo_absen, photo_absen1_url=photo_absen_url,
                                      time_abesen1=createdAt,
                                      createdAt=createdAt, account_id=account_id, toko_id=toko_id)
            db.add(data_absen)
            db.commit()
            db.refresh(data_absen)
        else:
            data_last = db.query(models.Absen).filter(models.Absen.account_id == account_id).order_by(
                models.Absen.id.desc()).first()

            if data_last.time_abesen1 is not None and data_last.time_abesen2 is not None:
                data_absen = models.Absen(photo_absen1=photo_absen, photo_absen1_url=photo_absen_url,
                                          time_abesen1=createdAt,
                                          createdAt=createdAt, account_id=account_id, toko_id=toko_id)
                db.add(data_absen)
                db.commit()
                db.refresh(data_absen)
            else:
                data_absen = db.query(models.Absen).filter(models.Absen.id == data_last.id).update({
                    "photo_absen2": photo_absen,
                    "photo_absen2_url": photo_absen_url,
                    "time_abesen2": createdAt,
                })
                db.commit()

        msg = "Success create absen "
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg
    }


@router.get('/checkabsen/{id}')
async def check_absen(id: int,
                      response: Response,
                      db: Session = Depends(get_db),
                      token: str = Depends(pengaturan.oauth2_scheme)):
    try:
        pengaturan.verify_token(token)
        data_last = db.query(models.Absen).filter(models.Absen.account_id == id).order_by(
            models.Absen.id.desc()).first()
        if data_last is None:
            status_code = response.status_code = status.HTTP_200_OK
            msg = "Success check status absen"
            data = "ABSEN MASUK"
        else:
            if data_last.time_abesen2 is None:
                status_code = response.status_code = status.HTTP_200_OK
                msg = "Success check status absen"
                data = "ABSEN KELUAR"
            else:
                status_code = response.status_code = status.HTTP_200_OK
                msg = "Success check status absen"
                data = "ABSEN MASUK"
    except:
        data = None
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data
    }


@router.get('/absen')
async def get_absen(start_date: int,
                    end_date: int,
                    toko_id: int,
                    db: Session = Depends(get_db),
                    token: str = Depends(pengaturan.oauth2_scheme),
                    ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Absen).filter(models.Absen.toko_id == toko_id).filter(
            models.Absen.createdAt.between(start_date, end_date)).all()
        msg = "Success get absen"
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


@router.get('/absen/{id}')
async def detail_absen(id: int,
                            response: Response,
                            db: Session = Depends(get_db),
                            token: str = Depends(pengaturan.oauth2_scheme)):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Absen).filter(models.Absen.id == id).first()
        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success get detail absen"
    except:
        data = None
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data
    }
