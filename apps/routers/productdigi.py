import hashlib
import json
import random
import time
from datetime import datetime, timedelta

import boto3
import requests
from fastapi import APIRouter, Response, Depends, Form, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from apps import database, models
from apps import pengaturan

get_db = database.get_db
router = APIRouter(tags=['PRODUCT DIGI SERVICE'])


@router.get('/sync_product_digi')
async def request_topup_wallet(db: Session = Depends(get_db),
                               token: str = Depends(pengaturan.oauth2_scheme),
                               ):
    try:
        pengaturan.verify_token(token)
        # ================================ REFRESH DATA PRODUCT ================================
        db.query(models.ProductDigi).delete()
        db.execute(f'ALTER TABLE productdigi AUTO_INCREMENT = 1')

        createdAt = int(round(time.time() * 1000))
        username = "mefeyeorX4yW"
        password = "85597426-90a0-50cb-85d0-a82bd1f64bdd"
        signature = hashlib.md5((username + password + "pricelist").encode()).hexdigest()

        data = {
            'cmd': 'prepaid',
            'username': f'{username}',
            'sign': f'{signature}'
        }

        url = "https://api.digiflazz.com/v1/price-list"
        headers = {'content-type': 'application/json'}

        data = requests.post(url, data=json.dumps(data), headers=headers).json().get('data')
        for data in data:
            product_name = data.get('product_name')
            category = data.get('category')
            brand = data.get('brand')
            type = data.get('type')
            seller_name = data.get('seller_name')
            price = data.get('price')
            buyer_sku_code = data.get('buyer_sku_code')
            buyer_product_status = data.get('buyer_product_status')
            seller_product_status = data.get('seller_product_status')
            unlimited_stock = data.get('unlimited_stock')
            stock = data.get('stock')
            multi = data.get('multi')
            start_cut_off = data.get('start_cut_off')
            end_cut_off = data.get('end_cut_off')
            desc = data.get('desc')
            last_sync_at = createdAt

            if price > 90000:
                a = price + float(400)
            else:
                a = price + float(250)

            new_data = models.ProductDigi(
                product_name=product_name,
                category=category,
                brand=brand,
                type=type,
                seller_name=seller_name,
                price=price,
                price_postku=a,
                buyer_sku_code=buyer_sku_code,
                buyer_product_status=buyer_product_status,
                seller_product_status=seller_product_status,
                unlimited_stock=unlimited_stock,
                stock=stock,
                multi=multi,
                start_cut_off=start_cut_off,
                end_cut_off=end_cut_off,
                desc=desc,
                last_sync_at=last_sync_at
            )

            db.add(new_data)
            db.commit()
            db.refresh(new_data)

        msg = "Success synchronize ppob product"
        status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.post('/category_digi')
async def create_category_digi(response: Response,
                               db: Session = Depends(get_db),
                               category_ppob_name: str = Form(...),
                               category_ppob_key: str = Form(...),
                               photo_logo: UploadFile = File(None),
                               token: str = Depends(pengaturan.oauth2_scheme),
                               ):
    try:
        pengaturan.verify_token(token)
        createdAt = int(round(time.time() * 1000))
        s3 = boto3.resource('s3', aws_access_key_id=pengaturan.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=pengaturan.AWS_SECRET_ACCESS_KEY)
        bucket = s3.Bucket(pengaturan.S3_BUCKET_NAME)

        bucket.upload_fileobj(photo_logo.file, photo_logo.filename,
                              ExtraArgs={"ACL": "public-read", "ContentType": photo_logo.content_type})
        photo_logo_url = f"https://{pengaturan.S3_BUCKET_NAME}.s3.amazonaws.com/{photo_logo.filename}"
        photo_logo = photo_logo.filename

        new_data = models.CategoryDigi(
            category_ppob_name=category_ppob_name,
            category_ppob_key=category_ppob_key,
            photo_logo=photo_logo,
            photo_logo_url=photo_logo_url,
            createdAt=createdAt,
        )

        db.add(new_data)
        db.commit()
        db.refresh(new_data)

        msg = "Success create category ppob digi "
        status_code = response.status_code = status.HTTP_200_OK
        data_resp = new_data
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data_resp = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data_resp,
    }


@router.get('/category_digi')
async def get_category_digi(response: Response,
                            db: Session = Depends(get_db),
                            token: str = Depends(pengaturan.oauth2_scheme),
                            ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.CategoryDigi).all()

        msg = "Success get data category digi"
        status_code = response.status_code = status.HTTP_200_OK
        data_resp = data
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data_resp = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data_resp,
    }


@router.post('/brand_digi')
async def create_brand_digi(response: Response,
                            db: Session = Depends(get_db),
                            brand_ppob_name: str = Form(...),
                            brand_ppob_key: str = Form(...),
                            categorydigi_id: int = Form(...),
                            photo_logo: UploadFile = File(None),
                            token: str = Depends(pengaturan.oauth2_scheme),
                            ):
    try:
        pengaturan.verify_token(token)
        createdAt = int(round(time.time() * 1000))
        ModelCategory = db.query(models.CategoryDigi).filter(models.CategoryDigi.id == categorydigi_id).first()
        s3 = boto3.resource('s3', aws_access_key_id=pengaturan.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=pengaturan.AWS_SECRET_ACCESS_KEY)
        bucket = s3.Bucket(pengaturan.S3_BUCKET_NAME)

        bucket.upload_fileobj(photo_logo.file, photo_logo.filename,
                              ExtraArgs={"ACL": "public-read", "ContentType": photo_logo.content_type})
        photo_logo_url = f"https://{pengaturan.S3_BUCKET_NAME}.s3.amazonaws.com/{photo_logo.filename}"
        photo_logo = photo_logo.filename

        new_data = models.BrandDigi(
            brand_ppob_name=brand_ppob_name,
            brand_ppob_key=brand_ppob_key,
            photo_logo=photo_logo,
            photo_logo_url=photo_logo_url,
            createdAt=createdAt,
        )
        ModelCategory.branddigi.append(new_data)

        db.add(new_data)
        db.commit()
        db.refresh(new_data)

        msg = "Success create brand ppob digi "
        status_code = response.status_code = status.HTTP_200_OK
        data_resp = new_data
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data_resp = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data_resp,
    }


@router.get('/brand_digi')
async def get_category_digi(response: Response,
                            category_ppob_key: str,
                            db: Session = Depends(get_db),
                            token: str = Depends(pengaturan.oauth2_scheme),
                            ):
    try:
        pengaturan.verify_token(token)
        category = db.query(models.CategoryDigi).filter(models.CategoryDigi.category_ppob_key == category_ppob_key).first()
        data = db.query(models.BrandDigi).filter(models.BrandDigi.categorydigi_id == category.id).all()

        msg = "Success get data brand digi"
        status_code = response.status_code = status.HTTP_200_OK
        data_resp = data
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data_resp = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data_resp,
    }


@router.get('/product_digi')
async def get_product_digi(response: Response,
                           category_ppob_key: str,
                           brand_ppob_key: str,
                           db: Session = Depends(get_db),
                           token: str = Depends(pengaturan.oauth2_scheme),
                           ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.ProductDigi).filter(models.ProductDigi.category == category_ppob_key).filter(
            models.ProductDigi.brand == brand_ppob_key).all()

        msg = "Success get data product digi"
        status_code = response.status_code = status.HTTP_200_OK
        data_resp = data
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data_resp = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data_resp,
    }
