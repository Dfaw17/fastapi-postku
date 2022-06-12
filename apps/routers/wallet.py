import random
import time
from datetime import datetime

import boto3
from fastapi import APIRouter, Response, Depends, Form, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from apps import database, models
from apps import pengaturan

get_db = database.get_db
router = APIRouter(tags=['WALLETS SERVICE'])


class Topup(BaseModel):
    wallet_code: str
    balance: int

    class Config:
        orm_mode = True


class AdminTopup(BaseModel):
    request_topup_id: int
    accept: str
    reason: str

    class Config:
        orm_mode = True


@router.get('/wallet')
async def check_status_wallet(wallet_code: str,
                              db: Session = Depends(get_db),
                              token: str = Depends(pengaturan.oauth2_scheme),
                              ):
    try:
        pengaturan.verify_token(token)
        wallet = db.query(models.Toko).filter(models.Toko.wallet_code == wallet_code).first()
        status_topup = wallet.status_req_deposit

        if status_topup == 0:
            status_topup = 0
            desc = "wallet ready for topup"
            balance_transfer = 0
        elif status_topup == 1:
            status_topup = 1
            desc = "pending topup, contimue transfer topup"
            balance_transfer = wallet.balance_req
        else:
            status_topup = 2
            desc = "Top is checking by admin"
            balance_transfer = 0

        msg = "Success get status wallet"
        status_code = status.HTTP_200_OK
        data = {
            "wallet_code": wallet.wallet_code,
            "balance_wallet": wallet.wallet_balance,
            "status_topup": status_topup,
            "desc": desc,
            "balance_transfer": balance_transfer,
        }
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data,
    }


@router.get('/request_topup')
async def get_request_topup(db: Session = Depends(get_db),
                            token: str = Depends(pengaturan.oauth2_scheme),
                            ):
    try:
        pengaturan.verify_token(token)
        get_data = db.query(models.TopupWallet).filter(models.TopupWallet.status_topup == 1).all()

        msg = "Success get data request topup"
        status_code = status.HTTP_200_OK
        data = get_data
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data,
    }


@router.post('/request_topup')
async def request_topup_wallet(req: Topup,
                               db: Session = Depends(get_db),
                               token: str = Depends(pengaturan.oauth2_scheme),
                               ):
    try:
        pengaturan.verify_token(token)
        ModelWallet = db.query(models.Toko).filter(models.Toko.wallet_code == req.wallet_code)
        balance = req.balance + random.randint(100, 999)

        # ================================ UPDATE TOKO ================================
        ModelWallet.update({
            "balance_req": balance,
            "status_req_deposit": 1
        })
        db.commit()

        msg = "Success request topup wallet"
        status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.put('/request_topup')
async def confirm_topup_wallet(db: Session = Depends(get_db),
                               wallet_code: str = Form(...),
                               channel_topup_id: int = Form(...),
                               photo_bukti: UploadFile = File(None),
                               token: str = Depends(pengaturan.oauth2_scheme),
                               ):
    try:
        pengaturan.verify_token(token)
        ModelWallet = db.query(models.Toko).filter(models.Toko.wallet_code == wallet_code)
        ModelToko = ModelWallet.first()
        ModelChannelTopup = db.query(models.ChannelTopup).filter(models.ChannelTopup.id == channel_topup_id).first()
        createdAt = int(round(time.time() * 1000))

        # ================================ CREATE TOPUP WALLET ================================
        s3 = boto3.resource('s3', aws_access_key_id=pengaturan.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=pengaturan.AWS_SECRET_ACCESS_KEY)
        bucket = s3.Bucket(pengaturan.S3_BUCKET_NAME)
        bucket.upload_fileobj(photo_bukti.file, photo_bukti.filename,
                              ExtraArgs={"ACL": "public-read", "ContentType": photo_bukti.content_type})
        photo_bukti_url = f"https://{pengaturan.S3_BUCKET_NAME}.s3.amazonaws.com/{photo_bukti.filename}"
        photo_bukti = photo_bukti.filename
        new_topup_wallet = models.TopupWallet(wallet_code=ModelWallet.first().wallet_code,
                                              status_topup=1,
                                              createdAt=createdAt,
                                              balance_req=ModelWallet.first().balance_req,
                                              photo_bukti=photo_bukti,
                                              photo_bukti_url=photo_bukti_url,
                                              )
        ModelChannelTopup.topupwallet.append(new_topup_wallet)
        ModelToko.topupwallet.append(new_topup_wallet)

        db.add(new_topup_wallet)
        db.commit()
        db.refresh(new_topup_wallet)

        # ================================ UPDATE TOKO WALLET ================================
        ModelWallet.update({
            "status_req_deposit": 2
        })
        db.commit()

        msg = "Success confirm topup wallet"
        status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.patch('/request_topup')
async def admin_request_topup_wallet(req: AdminTopup,
                                     db: Session = Depends(get_db),
                                     token: str = Depends(pengaturan.oauth2_scheme),
                                     ):
    try:
        pengaturan.verify_token(token)
        createdAt = int(round(time.time() * 1000))
        ModelTopupWallet = db.query(models.TopupWallet).filter(models.TopupWallet.id == req.request_topup_id)
        ModelToko = db.query(models.Toko).filter(models.Toko.id == ModelTopupWallet.first().toko_id)
        ModelTokos = ModelToko.first()
        update_balance = int(ModelToko.first().wallet_balance) + int(ModelTopupWallet.first().balance_req)
        reff_id = "WLT-" + datetime.today().strftime('%Y%m%d%H%M%S')
        years = datetime.today().strftime('%Y')
        mounth = datetime.today().strftime('%m')
        day = datetime.today().strftime('%d')
        hours = datetime.today().strftime('%H')
        munites = datetime.today().strftime('%M')
        seconds = datetime.today().strftime('%S')
        notes = f'Wallet {ModelToko.first().wallet_code} Success topup Balance Rp.{ModelTopupWallet.first().balance_req} at {years}-{mounth}-{day} {hours}:{munites}:{seconds}'

        # ================================ LOGIC ================================
        if req.accept == "ACCEPT":
            ModelTopupWallet.update({"status_topup": 2, "reason": req.reason})
            ModelToko.update({"status_req_deposit": 0, "balance_req": 0, "wallet_balance": update_balance})
            db.commit()

            # ================================ CREATE HISTORY WALLET ================================
            new_data = models.HistoryWallet(
                wallet_code=ModelToko.first().wallet_code,
                reff_id=reff_id,
                type=4,
                balance=ModelTopupWallet.first().balance_req,
                note=notes,
                createdAt=createdAt,
            )
            ModelTokos.historywallet.append(new_data)

            db.add(new_data)
            db.commit()
            db.refresh(new_data)
        elif req.accept == "CANCEL":
            ModelTopupWallet.update({"status_topup": 3, "reason": req.reason})
            ModelToko.update({"status_req_deposit": 0, "balance_req": 0})
            db.commit()
        else:
            print("c")

        msg = "Success accept or cancel request topup"
        status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }
