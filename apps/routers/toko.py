import time
import boto3
from fastapi import APIRouter, Response, Depends, Form, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from apps import database, models
from apps import pengaturan

get_db = database.get_db
router = APIRouter(tags=['TOKO SERVICE'])


class Toko(BaseModel):
    name: str
    address: str
    province: str
    city: str
    district: str
    village: str
    category: str
    owner_id: int

    class Config:
        orm_mode = True


class TokoId(BaseModel):
    toko_id: int

    class Config:
        orm_mode = True


@router.get('/toko/menus')
async def toko_get_data_menu(response: Response,
                             db: Session = Depends(get_db),
                             token: str = Depends(pengaturan.oauth2_scheme),
                             toko_id: int = None,
                             kategori_id: int = None,
                             ):
    try:
        pengaturan.verify_token(token)
        if kategori_id is None:
            data_menus = db.query(models.Menu).filter(models.Menu.toko_id == toko_id).filter(
                models.Menu.is_deleted == 0).all()
        else:
            data_menus = db.query(models.Menu).filter(models.Menu.toko_id == toko_id).filter(
                models.Menu.kategori_id == kategori_id).filter(models.Menu.is_deleted == 0).all()

        msg = "Success get menu toko"
        status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data_menus = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data_menus,
    }


@router.post('/toko')
async def create_toko(
        response: Response,
        req: Toko,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data_account = db.query(models.Account).filter(models.Account.id == req.owner_id).first()
        createdAt = int(round(time.time() * 1000))
        new_toko = models.Toko(name=req.name, address=req.address, province=req.province, city=req.city,
                               district=req.district,
                               village=req.village, category=req.category, createdAt=createdAt, is_deleted=0)
        data_account.toko.append(new_toko)

        db.add(new_toko)
        db.commit()
        db.refresh(new_toko)
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created toko"
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        new_toko = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": new_toko
    }


@router.put('/toko')
async def toko_edit(response: Response,
                    db: Session = Depends(get_db),
                    toko_id: str = Form(...),
                    name: str = Form(...),
                    address: str = Form(...),
                    province: str = Form(...),
                    city: str = Form(...),
                    district: str = Form(...),
                    village: str = Form(...),
                    category: str = Form(...),
                    photo_logo: UploadFile = File(None),
                    token: str = Depends(pengaturan.oauth2_scheme),
                    ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Toko).filter(models.Toko.id == toko_id)

        s3 = boto3.resource('s3', aws_access_key_id=pengaturan.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=pengaturan.AWS_SECRET_ACCESS_KEY)
        bucket = s3.Bucket(pengaturan.S3_BUCKET_NAME)

        if photo_logo is not None:
            bucket.upload_fileobj(photo_logo.file, photo_logo.filename,
                                  ExtraArgs={"ACL": "public-read", "ContentType": photo_logo.content_type})
            photo_logo_url = f"https://{pengaturan.S3_BUCKET_NAME}.s3.amazonaws.com/{photo_logo.filename}"
            photo_logo = photo_logo.filename
        else:
            photo_logo_url = data.first().photo_norek_url
            photo_logo = data.first().photo_norek

        data.update({
            "name": name,
            "province": province,
            "address": address,
            "city": city,
            "district": district,
            "village": village,
            "category": category,
            "photo_logo_url": photo_logo_url,
            "photo_logo": photo_logo,
        })
        db.commit()
        msg = "Success update toko "
        status_code = response.status_code = status.HTTP_200_OK
        data_resp = {
            "name": name,
            "province": province,
            "address": address,
            "city": city,
            "district": district,
            "village": village,
            "category": category,
            "photo_logo_url": photo_logo_url,
            "photo_logo": photo_logo,
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


@router.patch('/toko')
async def toko_delete(response: Response,
                      req: TokoId,
                      db: Session = Depends(get_db),
                      token: str = Depends(pengaturan.oauth2_scheme),
                      ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Toko).filter(models.Toko.id == req.toko_id)

        data.update({
            "is_deleted": 1,
        })
        db.commit()
        msg = "Success delete toko"
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.get('/toko/{id}')
async def detail_toko(id: int,
                      response: Response,
                      db: Session = Depends(get_db),
                      token: str = Depends(pengaturan.oauth2_scheme)):
    try:
        pengaturan.verify_token(token)

        data = db.query(models.Toko).filter(models.Toko.id == id).first()
        owner = data.account.filter(models.Account.account_type == 1).all()
        employee = data.account.filter(models.Account.account_type == 2).filter(
            models.Account.is_deleted == 0).all()
        katmenu = db.query(models.KategoriMenu).filter(models.KategoriMenu.toko_id == id).filter(
            models.KategoriMenu.is_deleted == 0).all()
        cust = db.query(models.Customer).filter(models.Customer.toko_id == id).filter(
            models.Customer.is_deleted == 0).all()
        table = db.query(models.Table).filter(models.Table.toko_id == id).filter(
            models.Table.is_deleted == 0).all()
        order_type = db.query(models.OrderType).filter(models.OrderType.toko_id == id).filter(
            models.OrderType.is_deleted == 0).all()
        order_label = db.query(models.LabelOrder).filter(models.LabelOrder.toko_id == id).filter(
            models.LabelOrder.is_deleted == 0).all()
        disc = db.query(models.Discount).filter(models.Discount.toko_id == id).filter(
            models.Discount.is_deleted == 0).all()
        pajak = db.query(models.Pajak).filter(models.Pajak.toko_id == id).filter(
            models.Pajak.is_deleted == 0).all()
        sf = db.query(models.ServiceFee).filter(models.ServiceFee.toko_id == id).filter(
            models.ServiceFee.is_deleted == 0).all()

        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success get detail toko"
    except:
        data = None
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        owner = None
        employee = None
        katmenu = None
        cust = None
        table = None
        order_type = None
        order_label = None
        disc = None
        pajak = None
        sf = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data,
        "owner": owner,
        "employee": employee,
        "kategori_menu": katmenu,
        "customer": cust,
        "table": table,
        "order_type": order_type,
        "order_label": order_label,
        "discount": disc,
        "pajak": pajak,
        "service_fee": sf,
    }
