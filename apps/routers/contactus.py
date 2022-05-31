import boto3
from fastapi import APIRouter, Response, Depends, Form, status, UploadFile, File
from sqlalchemy.orm import Session
from apps import database, models, pengaturan
from pydantic import BaseModel
import time

get_db = database.get_db
router = APIRouter(tags=['CONTACT US SERVICE'])


@router.post('/contactus')
async def contact_us_create(response: Response,
                            db: Session = Depends(get_db),
                            label: str = Form(...),
                            value: str = Form(...),
                            url: str = Form(...),
                            photo_contactus: UploadFile = File(None),
                            token: str = Depends(pengaturan.oauth2_scheme),
                            ):
    try:
        pengaturan.verify_token(token)
        createdAt = int(round(time.time() * 1000))

        s3 = boto3.resource('s3', aws_access_key_id=pengaturan.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=pengaturan.AWS_SECRET_ACCESS_KEY)
        bucket = s3.Bucket(pengaturan.S3_BUCKET_NAME)

        if photo_contactus is not None:
            bucket.upload_fileobj(photo_contactus.file, photo_contactus.filename,
                                  ExtraArgs={"ACL": "public-read", "ContentType": photo_contactus.content_type})
            photo_contactus_url = f"https://{pengaturan.S3_BUCKET_NAME}.s3.amazonaws.com/{photo_contactus.filename}"
            photo_contactus = photo_contactus.filename
        else:
            photo_contactus_url = None
            photo_contactus = None

        new_cu = models.ContactUs(label=label, value=value, url=url, photo_contactus=photo_contactus,
                                  photo_contactus_url=photo_contactus_url,
                                  createdAt=createdAt)
        db.add(new_cu)
        db.commit()
        db.refresh(new_cu)
        msg = "Success create contact us "
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        new_cu = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": new_cu,
    }


@router.get('/contactus')
async def contact_us_all(response: Response,
                         db: Session = Depends(get_db),
                         token: str = Depends(pengaturan.oauth2_scheme),
                         ):
    try:
        pengaturan.verify_token(token)
        data_banner = db.query(models.ContactUs).all()

        msg = "Success get all contact us"
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
