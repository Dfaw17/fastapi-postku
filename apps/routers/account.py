import json
from typing import List

import boto3
import requests
from cryptography.fernet import Fernet
from fastapi import APIRouter, Response, Depends, Form, status, UploadFile, File
from fastapi_mail import MessageSchema, FastMail
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from apps import database, schemas, models, pengaturan
import time, random

get_db = database.get_db
router = APIRouter(tags=['ACCOUNT SERVICE'])


class Owner(BaseModel):
    name: str
    phone: str
    email: str
    pwd: str

    class Config:
        orm_mode = True


class Employee(BaseModel):
    name: str
    phone: str
    email: str
    pwd: str
    toko_id: int

    class Config:
        orm_mode = True


class LoginGeneral(BaseModel):
    username: str
    pwd: str

    class Config:
        orm_mode = True


class ChangePwd(BaseModel):
    email: str
    pwd: str

    class Config:
        orm_mode = True


class LoginWa(BaseModel):
    whatsapp: str

    class Config:
        orm_mode = True


class LoginEmail(BaseModel):
    email: str

    class Config:
        orm_mode = True


class VerifyOtp(BaseModel):
    email: str
    OTP: int

    class Config:
        orm_mode = True


class EmailSchema(BaseModel):
    email: List[EmailStr]


class EmployeeID(BaseModel):
    id_employee: int

    class Config:
        orm_mode = True


@router.get('/ping')
async def check_server():
    return {
        "msg": "pong",
    }


@router.get('/user/decode/{id}')
async def decode_user(id: int, response: Response, db: Session = Depends(get_db)):
    data = db.query(models.Account).filter(models.Account.id == id).first()

    if not data:
        status_code = response.status_code = status.HTTP_404_NOT_FOUND
        msg = "Not Found User"
        decode = None
    else:
        f = Fernet(data.key_ecd)
        decode = f.decrypt(data.ecd.encode()).decode()

        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success Get Decode User"
    return {
        "status_code": status_code,
        "msg": msg,
        "data": decode,
    }


@router.get('/user/{id}')
async def detail_account(id: int, response: Response, db: Session = Depends(get_db),
                         token: str = Depends(pengaturan.oauth2_scheme)):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Account).filter(models.Account.id == id).first()
        data_toko = data.toko.filter(models.Toko.is_deleted == 0).all()
        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success get detail user"
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        data = None
        data_toko = None

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data,
        "data_toko": data_toko,
    }


@router.post('/user/owner')
async def register_owner_account(
        response: Response,
        req: Owner,
        db: Session = Depends(get_db),
):
    check_username = db.query(models.Account).filter(models.Account.name == req.name).first()
    check_email = db.query(models.Account).filter(models.Account.email == req.email).first()
    check_phone = db.query(models.Account).filter(models.Account.phone == req.phone).first()

    if check_username is not None:
        msg = "Username has been used"
        status_code = response.status_code = status.HTTP_400_BAD_REQUEST
        new_user = None
    elif check_email is not None:
        msg = "Email has been used"
        status_code = response.status_code = status.HTTP_400_BAD_REQUEST
        new_user = None
    elif check_phone is not None:
        msg = "No Whatsaap has been used"
        status_code = response.status_code = status.HTTP_400_BAD_REQUEST
        new_user = None
    else:
        # ENKRIPSI PWD USER
        hashed_pwd = pengaturan.pwd_context.hash(req.pwd)

        # ENCODE
        key = Fernet.generate_key()
        f = Fernet(key)
        encode_pwd = f.encrypt(req.pwd.encode())

        # STORE TO DB
        createdAt = int(round(time.time() * 1000))
        new_user = models.Account(name=req.name, email=req.email, pwd=hashed_pwd, phone=req.phone, ecd=encode_pwd,
                                  key_ecd=key,
                                  account_type=1, createdAt=createdAt, is_deleted=0)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created owner account"

    return {
        "status_code": status_code,
        "msg": msg,
        "data": new_user
    }


@router.post('/user/employee')
async def register_employee_account(
        response: Response,
        req: Employee,
        db: Session = Depends(get_db),
):
    check_username = db.query(models.Account).filter(models.Account.name == req.name).first()
    check_email = db.query(models.Account).filter(models.Account.email == req.email).first()
    check_phone = db.query(models.Account).filter(models.Account.phone == req.phone).first()

    if check_username is not None:
        msg = "Username has been used"
        status_code = response.status_code = status.HTTP_400_BAD_REQUEST
        new_user = None
    elif check_email is not None:
        msg = "Email has been used"
        status_code = response.status_code = status.HTTP_400_BAD_REQUEST
        new_user = None
    elif check_phone is not None:
        msg = "No Whatsaap has been used"
        status_code = response.status_code = status.HTTP_400_BAD_REQUEST
        new_user = None
    else:
        # ENKRIPSI PWD USER
        hashed_pwd = pengaturan.pwd_context.hash(req.pwd)

        # ENCODE
        key = Fernet.generate_key()
        f = Fernet(key)
        encode_pwd = f.encrypt(req.pwd.encode())

        # STORE TO DB
        createdAt = int(round(time.time() * 1000))
        data_toko = db.query(models.Toko).filter(models.Toko.id == req.toko_id).first()
        new_user = models.Account(name=req.name, email=req.email, pwd=hashed_pwd, phone=req.phone, ecd=encode_pwd,
                                  key_ecd=key,
                                  account_type=2, createdAt=createdAt, is_deleted=0)
        data_toko.account.append(new_user)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created employee account"

    return {
        "status_code": status_code,
        "msg": msg,
        "data": new_user
    }


@router.post('/user/login/general')
async def login_user_general(response: Response,
                             req: LoginGeneral,
                             db: Session = Depends(get_db)):
    data = db.query(models.Account).filter(models.Account.name == req.username).first()

    # VERIFY PWD USER
    try:
        verify = pengaturan.pwd_context.verify(req.pwd, data.pwd)
    except:
        verify = False

    if not data:
        status_code = response.status_code = status.HTTP_404_NOT_FOUND
        msg = "Invalid: account not found"
        data = None
        access_token = None
    elif not verify:
        status_code = response.status_code = status.HTTP_404_NOT_FOUND
        msg = "Invalid: wrong password account"
        data = None
        access_token = None
    else:
        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success login account"
        access_token = pengaturan.create_access_token(data={"sub": data.email})
        data_toko = data.toko.filter(models.Toko.is_deleted == 0).all()
        data = {
            "akun": data,
            "list_toko": data_toko,
        }

    return {
        "status_code": status_code,
        "msg": msg,
        "token": {"access_token": access_token, "token_type": "bearer"},
        "data": data,
    }


@router.post('/user/login/wa')
async def login_user_whatsapp(response: Response,
                              req: LoginWa,
                              db: Session = Depends(get_db)):
    data = db.query(models.Account).filter(models.Account.phone == req.whatsapp).first()
    f = Fernet(data.key_ecd)
    decode = f.decrypt(data.ecd.encode()).decode()

    # VERIFY PWD USER
    try:
        verify = pengaturan.pwd_context.verify(decode, data.pwd)
    except:
        verify = False

    if not data:
        status_code = response.status_code = status.HTTP_404_NOT_FOUND
        msg = "Invalid: account not found"
        data = None
        access_token = None
    elif not verify:
        status_code = response.status_code = status.HTTP_404_NOT_FOUND
        msg = "Invalid: wrong password account"
        data = None
        access_token = None
    else:
        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success login account"
        access_token = pengaturan.create_access_token(data={"sub": data.email})
        data_toko = data.toko.filter(models.Toko.is_deleted == 0).all()
        data = {
            "akun": data,
            "list_toko": data_toko,
        }

    return {
        "status_code": status_code,
        "msg": msg,
        "token": {"access_token": access_token, "token_type": "bearer"},
        "data": data,
    }


@router.post('/user/login/email')
async def login_user_email(response: Response,
                           req: LoginEmail,
                           db: Session = Depends(get_db)):
    data = db.query(models.Account).filter(models.Account.email == req.email).first()
    f = Fernet(data.key_ecd)
    decode = f.decrypt(data.ecd.encode()).decode()

    # VERIFY PWD USER
    try:
        verify = pengaturan.pwd_context.verify(decode, data.pwd)
    except:
        verify = False

    if not data:
        status_code = response.status_code = status.HTTP_404_NOT_FOUND
        msg = "Invalid: account not found"
        data = None
        access_token = None
    elif not verify:
        status_code = response.status_code = status.HTTP_404_NOT_FOUND
        msg = "Invalid: wrong password accound"
        data = None
        access_token = None
    else:
        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success login account"
        access_token = pengaturan.create_access_token(data={"sub": data.email})
        data_toko = data.toko.filter(models.Toko.is_deleted == 0).all()
        data = {
            "akun": data,
            "list_toko": data_toko,
        }

    return {
        "status_code": status_code,
        "msg": msg,
        "token": {"access_token": access_token, "token_type": "bearer"},
        "data": data,
    }


@router.post('/user/otp/request/wa')
async def user_request_otp_whatsapp(response: Response,
                                    req: LoginWa,
                                    db: Session = Depends(get_db)):
    data = db.query(models.Account).filter(models.Account.phone == req.whatsapp)
    OTP = random.randint(1000, 9999)
    data.update({
        "OTP": OTP,
    })
    db.commit()

    # SEND WHATAPPS
    wa = "62" + data.first().phone[1:]
    data_otp = {
        "phone": wa,
        "messageType": "otp",
        "body": f'Berikut adalah kode otp kamu, jangan memberi kode otp ini kepada siapapun ini bersifat rahasia, penyalahgunaan kode OTP bukan tanggung jawab POSTKU OTP code :  *{OTP}*'
    }

    url = "https://sendtalk-api.taptalk.io/api/v1/message/send_whatsapp"
    headers = {'content-type': 'application/json',
               "API-Key": pengaturan.WA_KEY}

    send_otp = requests.post(url, data=json.dumps(data_otp), headers=headers)
    status_code = response.status_code = status.HTTP_200_OK
    return {
        "status_code": status_code,
        "msg": f"Success send otp to phone from account {data.first().email}",
    }


@router.post('/user/otp/verify')
async def user_verify_otp(response: Response,
                          req: VerifyOtp,
                          db: Session = Depends(get_db)):
    data = db.query(models.Account).filter(models.Account.email == req.email).first()
    if data.OTP == req.OTP:
        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success verification otp"
    else:
        status_code = response.status_code = status.HTTP_404_NOT_FOUND
        msg = "Failed verification, otp not match"

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.put('/user')
async def user_edit(response: Response,
                    db: Session = Depends(get_db),
                    account_id: str = Form(...),
                    address: str = Form(...),
                    no_rekening: str = Form(...),
                    jenis_bank: str = Form(...),
                    profile_photo: UploadFile = File(None),
                    norek_photo: UploadFile = File(None),
                    token: str = Depends(pengaturan.oauth2_scheme),
                    ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Account).filter(models.Account.id == account_id)

        s3 = boto3.resource('s3', aws_access_key_id=pengaturan.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=pengaturan.AWS_SECRET_ACCESS_KEY)
        bucket = s3.Bucket(pengaturan.S3_BUCKET_NAME)

        if profile_photo is not None:
            bucket.upload_fileobj(profile_photo.file, profile_photo.filename,
                                  ExtraArgs={"ACL": "public-read", "ContentType": profile_photo.content_type})
            photo_profile_url = f"https://{pengaturan.S3_BUCKET_NAME}.s3.amazonaws.com/{profile_photo.filename}"
            photo_profile = profile_photo.filename
        else:
            photo_profile = data.first().photo_profile
            photo_profile_url = data.first().photo_profile_url

        if norek_photo is not None:
            bucket.upload_fileobj(norek_photo.file, norek_photo.filename,
                                  ExtraArgs={"ACL": "public-read", "ContentType": norek_photo.content_type})
            photo_norek_url = f"https://{pengaturan.S3_BUCKET_NAME}.s3.amazonaws.com/{norek_photo.filename}"
            photo_norek = norek_photo.filename
        else:
            photo_norek_url = data.first().photo_norek_url
            photo_norek = data.first().photo_norek

        data.update({
            "address": address,
            "no_rekening": no_rekening,
            "jenis_bank": jenis_bank,
            "photo_profile": photo_profile,
            "photo_profile_url": photo_profile_url,
            "photo_norek": photo_norek,
            "photo_norek_url": photo_norek_url,
        })
        db.commit()
        msg = "Success update data account "
        status_code = response.status_code = status.HTTP_200_OK
        data_resp = {
            "email": data.first().email,
            "name": data.first().name,
            "phone": data.first().phone,
            "address": address,
            "no_rekening": no_rekening,
            "jenis_bank": jenis_bank,
            "photo_profile": photo_profile,
            "photo_profile_url": photo_profile_url,
            "photo_norek": photo_norek,
            "photo_norek_url": photo_norek_url,
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


@router.post('/user/change_password')
async def user_change_password(response: Response,
                               req: ChangePwd,
                               db: Session = Depends(get_db)):
    data = db.query(models.Account).filter(models.Account.email == req.email)

    # ENKRIPSI PWD USER
    hashed_pwd = pengaturan.pwd_context.hash(req.pwd)

    # ENCODE
    key = Fernet.generate_key()
    f = Fernet(key)
    encode_pwd = f.encrypt(req.pwd.encode())

    data.update({
        "pwd": hashed_pwd,
        "ecd": encode_pwd,
        "key_ecd": key,
    })
    db.commit()
    msg = "Success change password "
    status_code = response.status_code = status.HTTP_200_OK

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.post("/user/otp/request/email")
async def user_request_otp_email(response: Response,
                                 background_tasks: BackgroundTasks,
                                 email: EmailSchema,
                                 db: Session = Depends(get_db)):
    email_penerima = email.dict().get("email")[0]
    OTP = random.randint(1000, 9999)
    try:
        data = db.query(models.Account).filter(models.Account.email == email_penerima)
        data.update({
            "OTP": OTP,
        })
        db.commit()

        body = {"OTP": OTP}

        message = MessageSchema(
            subject="Postku | OTP Code",
            recipients=email.dict().get("email"),
            template_body=body
        )

        fm = FastMail(pengaturan.conf)
        background_tasks.add_task(fm.send_message, message, template_name="email_template.html")
        status_code = response.status_code = status.HTTP_200_OK
        msg = f"Sukses send otp to email {data.first().email}"
    except:
        status_code = response.status_code = status.HTTP_404_NOT_FOUND
        msg = "Email not found"
    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.patch('/user')
async def employee_delete(response: Response,
                          req: EmployeeID,
                          db: Session = Depends(get_db),
                          token: str = Depends(pengaturan.oauth2_scheme),
                          ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Account).filter(models.Account.id == req.id_employee)

        data.update({
            "is_deleted": 1,
        })
        db.commit()
        msg = "Success delete data employee "
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }
