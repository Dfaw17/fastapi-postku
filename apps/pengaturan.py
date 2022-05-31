from datetime import datetime, timedelta
from pathlib import Path
from cryptography.fernet import Fernet
from fastapi.security import OAuth2PasswordBearer
from fastapi_mail import ConnectionConfig
from jose import jwt
from passlib.context import CryptContext
import os.path

# AUTH
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fernet = Fernet(b'vuP07BGuBbhASHB-HMBc8sKF_UFNSkxNj429oSjYiyo=')
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAY = 365
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# WHATSAPP
WA_KEY = "42c21ceb5f15c64953c8b45c3d235903f70df95feafc9ef1653216eb999defe3"

# AWS S3
S3_BUCKET_NAME = 'postku-fastapi-bucket'
AWS_ACCESS_KEY_ID = 'AKIA4R2DEXXG3RW54WTU'
AWS_SECRET_ACCESS_KEY = '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'
default_image = "MainIcon.png"
default_image_url = "https://postku-fastapi-bucket.s3.amazonaws.com/MainIcon.png"

# EMAIL

Temp_Path = os.path.realpath('.')
conf = ConnectionConfig(
    MAIL_USERNAME="postku.id@gmail.com",
    MAIL_PASSWORD="_Fawwaz170901_@@",
    MAIL_FROM="postku.id@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER='apps/templates',
)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAY)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    expires = payload.get("exp")

    return {
        "username": username,
        "expires": expires
    }
