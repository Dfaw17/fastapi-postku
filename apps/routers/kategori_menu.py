import time
import boto3
from fastapi import APIRouter, Response, Depends, Form, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from apps import database, models
from apps import pengaturan

get_db = database.get_db
router = APIRouter(tags=['KATEGORI MENU SERVICE'])


class KatMenu(BaseModel):
    name: str
    toko_id: int

    class Config:
        orm_mode = True


class KatMenuEdit(BaseModel):
    name: str
    id_kat_menu: int

    class Config:
        orm_mode = True


class KatMenuId(BaseModel):
    id_kat_menu: int

    class Config:
        orm_mode = True


@router.post('/katmenu')
async def create_kategori_menu(
        response: Response,
        req: KatMenu,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data_toko = db.query(models.Toko).filter(models.Toko.id == req.toko_id).first()
        createdAt = int(round(time.time() * 1000))
        new_katmenu = models.KategoriMenu(name=req.name, createdAt=createdAt, is_deleted=0)
        data_toko.kategori_menu.append(new_katmenu)
        db.add(new_katmenu)
        db.commit()
        db.refresh(new_katmenu)
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created menu category"
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        new_katmenu = None
    return {
        "status_code": status_code,
        "msg": msg,
        "data": new_katmenu
    }


@router.put('/katmenu')
async def edit_kategori_menu(
        response: Response,
        req: KatMenuEdit,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.KategoriMenu).filter(models.KategoriMenu.id == req.id_kat_menu)
        data.update({
            "name": req.name
        })
        db.commit()
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success edit menu category"
        data = req
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data = None
    return {
        "status_code": status_code,
        "msg": msg,
        "data": data
    }


@router.patch('/katmenu')
async def kat_menu_delete(response: Response,
                          req: KatMenuId,
                          db: Session = Depends(get_db),
                          token: str = Depends(pengaturan.oauth2_scheme),
                          ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.KategoriMenu).filter(models.KategoriMenu.id == req.id_kat_menu)

        data.update({
            "is_deleted": 1,
        })
        db.commit()
        msg = "Success delete menu category"
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.get('/katmenu/{id}')
async def detail_katmenu(id: int,
                         response: Response,
                         db: Session = Depends(get_db),
                         token: str = Depends(pengaturan.oauth2_scheme)):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.KategoriMenu).filter(models.KategoriMenu.id == id).first()
        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success get detail menu category"
    except:
        data = None
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data
    }
