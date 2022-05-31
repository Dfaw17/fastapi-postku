import boto3
from fastapi import APIRouter, Response, Depends, Form, status, UploadFile, File
from sqlalchemy.orm import Session
from apps import database, models, pengaturan
from pydantic import BaseModel
import time

get_db = database.get_db
router = APIRouter(tags=['ARTICLE SERVICE'])


class ArticleID(BaseModel):
    article_id: int

    class Config:
        orm_mode = True


@router.post('/article')
async def create_article(response: Response,
                         db: Session = Depends(get_db),
                         name: str = Form(...),
                         body: str = Form(...),
                         photo_article: UploadFile = File(None),
                         token: str = Depends(pengaturan.oauth2_scheme),
                         ):
    try:
        pengaturan.verify_token(token)
        createdAt = int(round(time.time() * 1000))

        s3 = boto3.resource('s3', aws_access_key_id=pengaturan.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=pengaturan.AWS_SECRET_ACCESS_KEY)
        bucket = s3.Bucket(pengaturan.S3_BUCKET_NAME)

        if photo_article is not None:
            bucket.upload_fileobj(photo_article.file, photo_article.filename,
                                  ExtraArgs={"ACL": "public-read", "ContentType": photo_article.content_type})
            photo_article_url = f"https://{pengaturan.S3_BUCKET_NAME}.s3.amazonaws.com/{photo_article.filename}"
            photo_article = photo_article.filename
        else:
            photo_article_url = None
            photo_article = None

        new_article = models.Article(name=name, body=body, photo_article=photo_article,
                                     photo_article_url=photo_article_url, count_seen=1,
                                     createdAt=createdAt, is_deleted=0)
        db.add(new_article)
        db.commit()
        db.refresh(new_article)
        msg = "Success create article "
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        new_article = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": new_article,
    }


@router.get('/article')
async def article_all(response: Response,
                      db: Session = Depends(get_db),
                      token: str = Depends(pengaturan.oauth2_scheme),
                      ):
    try:
        pengaturan.verify_token(token)
        data_banner = db.query(models.Article).filter(models.Article.is_deleted == 0).all()

        msg = "Success get all article"
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


@router.patch('/article')
async def delete_article(response: Response,
                         req: ArticleID,
                         db: Session = Depends(get_db),
                         token: str = Depends(pengaturan.oauth2_scheme),
                         ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Article).filter(models.Article.id == req.article_id)

        data.update({
            "is_deleted": 1,
        })
        db.commit()
        msg = "Success delete article"
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.get('/article/{id}')
async def detail_article(id: int,
                         response: Response,
                         db: Session = Depends(get_db),
                         token: str = Depends(pengaturan.oauth2_scheme)
                         ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Article).filter(models.Article.id == id).first()
        count_seen = data.count_seen + 1

        db.query(models.Article).filter(models.Article.id == id).update({"count_seen": count_seen})
        db.commit()
        db.refresh(data)
        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success get detail article"
    except:
        data = None
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data
    }
