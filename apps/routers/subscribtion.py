import random
import time
from datetime import datetime, timedelta

import boto3
from fastapi import APIRouter, Response, Depends, Form, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from apps import database, models
from apps import pengaturan

get_db = database.get_db
router = APIRouter(tags=['SUBSCRIBTION SERVICE'])


class Subs(BaseModel):
    wallet_code: str
    account_id: int
    date_subs: int

    class Config:
        orm_mode = True


@router.post('/subs')
async def request_topup_wallet(req: Subs,
                               db: Session = Depends(get_db),
                               token: str = Depends(pengaturan.oauth2_scheme),
                               ):
    try:
        pengaturan.verify_token(token)
        ModelWallet = db.query(models.Toko).filter(models.Toko.wallet_code == req.wallet_code)
        wallet = ModelWallet.first()
        ModelAccount = db.query(models.Account).filter(models.Account.id == req.account_id)
        account = ModelAccount.first()

        invoice_subs = req.date_subs * 1000
        balance_wallet = wallet.wallet_balance
        status_subs = account.is_subs
        createdAt = int(round(time.time() * 1000))
        date_subs = datetime.today() + timedelta(days=int(req.date_subs))
        date_subs_epoch = int(round(date_subs.timestamp() * 1000))
        reff_id = "WLT-" + datetime.today().strftime('%Y%m%d%H%M%S')

        if balance_wallet <= invoice_subs:
            msg = "Failed create subscribtion, wallet not enough"
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            if status_subs == 1:
                msg = "Failed create subscribtion, your account in subscription"
                status_code = status.HTTP_400_BAD_REQUEST
            else:
                # ================================ UPDATE CREDIT WALLET ================================
                ModelWallet.update({
                    "wallet_balance": int(balance_wallet - invoice_subs)
                })
                # ================================ UPDATE SUBS USER ================================
                ModelAccount.update({
                    "is_subs": 1,
                    "subs_date": date_subs_epoch,
                })
                db.commit()

                # ================================ CRAETE WALLET TRX ================================
                years = datetime.today().strftime('%Y')
                mounth = datetime.today().strftime('%m')
                day = datetime.today().strftime('%d')
                hours = datetime.today().strftime('%H')
                munites = datetime.today().strftime('%M')
                seconds = datetime.today().strftime('%S')
                notes = f'Wallet {req.wallet_code} Success credit Balance Rp.{invoice_subs} for activate subscribtion ' \
                        f'Postku Plus {req.date_subs} days at {years}-{mounth}-{day} {hours}:{munites}:{seconds} '
                new_data = models.HistoryWallet(
                    wallet_code=req.wallet_code,
                    reff_id=reff_id,
                    type=2,
                    balance=invoice_subs,
                    note=notes,
                    createdAt=createdAt,
                )
                wallet.historywallet.append(new_data)

                db.add(new_data)
                db.commit()
                db.refresh(new_data)

                msg = "Success create subsribtion"
                status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.get('/subs')
async def request_topup_wallet(db: Session = Depends(get_db),
                               token: str = Depends(pengaturan.oauth2_scheme),
                               ):
    try:
        pengaturan.verify_token(token)
        now = int(round(time.time() * 1000))
        Account = db.query(models.Account).all()

        for i in Account:
            if i.subs_date is None:
                pass
            else:
                if int(i.subs_date) < int(now):
                    data = db.query(models.Account).filter(models.Account.id == i.id)
                    data.update({
                        "is_subs": 0,
                        "subs_date": None
                    })
                    db.commit()
                else:
                   pass

        msg = "Success create subsribtion"
        status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }
