import time
from typing import Optional
import boto3
from fastapi import APIRouter, Response, Depends, Form, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from apps import database, models
from apps import pengaturan

get_db = database.get_db
router = APIRouter(tags=['MENU SERVICE'])


class Menu(BaseModel):
    name: str
    desc: str
    harga_asli: int
    harga_jual: int
    toko_id: int
    kategori_id: Optional[int] = None
    is_stock: Optional[bool] = False
    current_stock: Optional[int] = None
    note_stock: Optional[str] = None

    class Config:
        orm_mode = True


class MenuId(BaseModel):
    menu_id: int

    class Config:
        orm_mode = True


@router.post('/menu')
async def create_menu(
        response: Response,
        req: Menu,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        createdAt = int(round(time.time() * 1000))
        new_menu = models.Menu(name=req.name,
                               desc=req.desc,
                               harga_asli=req.harga_asli,
                               harga_jual=req.harga_jual,
                               toko_id=req.toko_id,
                               kategori_id=req.kategori_id,
                               is_stock=req.is_stock,
                               current_stock=req.current_stock,
                               is_deleted=0,
                               createdAt=createdAt)
        db.add(new_menu)
        db.commit()
        db.refresh(new_menu)

        # ============================= CREATE STOCK =============================
        if req.is_stock is None:
            pass
        else:
            new_menu_stock = models.HistoryStockMenu(
                adjustment_stock=req.current_stock,
                type=1,
                note=req.note_stock,
                menu_id=new_menu.id,
                createdAt=createdAt
            )
            db.add(new_menu_stock)
            db.commit()
            db.refresh(new_menu_stock)

        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created"
        new_menu = req
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        new_menu = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": new_menu
    }


@router.get('/menu/{id}')
async def detail_menu(id: int,
                      response: Response,
                      db: Session = Depends(get_db),
                      token: str = Depends(pengaturan.oauth2_scheme)):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Menu).filter(models.Menu.id == id).first()
        print(data.kategori_menu)
        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success get detail menu"
    except:
        data = None
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data
    }


@router.put('/menu')
async def menu_edit(response: Response,
                    db: Session = Depends(get_db),
                    token: str = Depends(pengaturan.oauth2_scheme),
                    menu_id: str = Form(...),
                    name: str = Form(...),
                    desc: str = Form(...),
                    harga_asli: str = Form(...),
                    harga_jual: str = Form(...),
                    photo_menu: UploadFile = File(None),
                    kategori_id: int = Form(None),
                    ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Menu).filter(models.Menu.id == menu_id)

        s3 = boto3.resource('s3', aws_access_key_id=pengaturan.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=pengaturan.AWS_SECRET_ACCESS_KEY)
        bucket = s3.Bucket(pengaturan.S3_BUCKET_NAME)
        if photo_menu is not None:
            bucket.upload_fileobj(photo_menu.file, photo_menu.filename,
                                  ExtraArgs={"ACL": "public-read", "ContentType": photo_menu.content_type})
            photo_menu_url = f"https://{pengaturan.S3_BUCKET_NAME}.s3.amazonaws.com/{photo_menu.filename}"
            photo_menu = photo_menu.filename
        else:
            photo_menu_url = data.first().photo_menu_url
            photo_menu = data.first().photo_menu

        if kategori_id is not None:
            kategori_id = kategori_id
        else:
            kategori_id = data.first().kategori_id

        data.update({
            "name": name,
            "desc": desc,
            "harga_asli": harga_asli,
            "harga_jual": harga_jual,
            "photo_menu_url": photo_menu_url,
            "photo_menu": photo_menu,
            "kategori_id": kategori_id,
        })

        db.commit()
        msg = "Success update menu"
        status_code = response.status_code = status.HTTP_200_OK
        data_resp = {
            "name": name,
            "desc": desc,
            "harga_asli": harga_asli,
            "harga_jual": harga_jual,
            "photo_logo_url": photo_menu_url,
            "photo_logo": photo_menu,
            "kategori_id": kategori_id,
        }
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data_resp = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data_resp,
    }


@router.patch('/menu')
async def menu_delete(response: Response,
                      req: MenuId,
                      db: Session = Depends(get_db),
                      token: str = Depends(pengaturan.oauth2_scheme),
                      ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Menu).filter(models.Menu.id == req.menu_id)

        data.update({
            "is_deleted": 1,
        })
        db.commit()
        msg = "Success delete menu "
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }
