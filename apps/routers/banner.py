import boto3
from fastapi import APIRouter, Response, Depends, Form, status, UploadFile, File
from sqlalchemy.orm import Session
from apps import database, models, pengaturan
from pydantic import BaseModel
import time

get_db = database.get_db
router = APIRouter(tags=['BANNER SERVICE'])


class BannerID(BaseModel):
    banner_id: int

    class Config:
        orm_mode = True


@router.post('/banner')
async def banner_create(response: Response,
                        db: Session = Depends(get_db),
                        name: str = Form(...),
                        body: str = Form(...),
                        photo_banner: UploadFile = File(None),
                        token: str = Depends(pengaturan.oauth2_scheme),
                        ):
    try:
        pengaturan.verify_token(token)
        createdAt = int(round(time.time() * 1000))

        s3 = boto3.resource('s3', aws_access_key_id=pengaturan.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=pengaturan.AWS_SECRET_ACCESS_KEY)
        bucket = s3.Bucket(pengaturan.S3_BUCKET_NAME)

        if photo_banner is not None:
            bucket.upload_fileobj(photo_banner.file, photo_banner.filename,
                                  ExtraArgs={"ACL": "public-read", "ContentType": photo_banner.content_type})
            photo_banner_url = f"https://{pengaturan.S3_BUCKET_NAME}.s3.amazonaws.com/{photo_banner.filename}"
            photo_banner = photo_banner.filename
        else:
            photo_banner_url = None
            photo_banner = None

        new_banner = models.Banner(name=name, body=body, photo_banner=photo_banner, photo_banner_url=photo_banner_url,
                                   createdAt=createdAt, is_deleted=0)
        db.add(new_banner)
        db.commit()
        db.refresh(new_banner)
        msg = "Success create banner "
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        new_banner = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": new_banner,
    }


@router.get('/banner')
async def banner_all(response: Response,
                     db: Session = Depends(get_db),
                     token: str = Depends(pengaturan.oauth2_scheme),
                     ):
    try:
        pengaturan.verify_token(token)
        data_banner = db.query(models.Banner).filter(models.Banner.is_deleted == 0).all()

        msg = "Success get all banner"
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data_banner = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data_banner,
    }


@router.patch('/banner')
async def delete_banner(response: Response,
                        req: BannerID,
                        db: Session = Depends(get_db),
                        token: str = Depends(pengaturan.oauth2_scheme),
                        ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Banner).filter(models.Banner.id == req.banner_id)

        data.update({
            "is_deleted": 1,
        })
        db.commit()
        msg = "Success delete banner"
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.get('/banner/{id}')
async def detail_banner(id: int,
                        response: Response,
                        db: Session = Depends(get_db),
                        token: str = Depends(pengaturan.oauth2_scheme)):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Banner).filter(models.Banner.id == id).first()
        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success get detail banner"
    except:
        data = None
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data
    }
