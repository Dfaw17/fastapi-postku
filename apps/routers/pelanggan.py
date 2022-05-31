from fastapi import APIRouter, Response, Depends, Form, status
from sqlalchemy.orm import Session
from apps import database, models, pengaturan
from pydantic import BaseModel
import time

get_db = database.get_db
router = APIRouter(tags=['CUSTOMER SERVICE'])


class Customer(BaseModel):
    name: str
    phone: str
    email: str
    toko_id: int

    class Config:
        orm_mode = True


class CustomerEdit(BaseModel):
    name: str
    phone: str
    email: str
    id_customer: int

    class Config:
        orm_mode = True


class CustomerID(BaseModel):
    id_customer: int

    class Config:
        orm_mode = True


@router.post('/customer')
async def create_customer(
        response: Response,
        customer: Customer,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data_toko = db.query(models.Toko).filter(models.Toko.id == customer.toko_id).first()
        createdAt = int(round(time.time() * 1000))
        new_pelanggan = models.Customer(name=customer.name, phone=customer.phone, email=customer.email,
                                        createdAt=createdAt, is_deleted=0)
        data_toko.customer.append(new_pelanggan)
        db.add(new_pelanggan)
        db.commit()
        db.refresh(new_pelanggan)
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created customer"
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        customer = None
    return {
        "status_code": status_code,
        "msg": msg,
        "data": customer
    }


@router.put('/customer')
async def edit_customer(
        response: Response,
        req: CustomerEdit,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Customer).filter(models.Customer.id == req.id_customer)
        data.update({
            "name": req.name,
            "phone": req.phone,
            "email": req.email,
        })
        db.commit()
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success edit customer"
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


@router.patch('/customer')
async def customer_delete(response: Response,
                          req: CustomerID,
                          db: Session = Depends(get_db),
                          token: str = Depends(pengaturan.oauth2_scheme),
                          ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Customer).filter(models.Customer.id == req.id_customer)

        data.update({
            "is_deleted": 1,
        })
        db.commit()
        msg = "Success delete customer "
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.get('/customer/{id}')
async def detail_pelanggan(id: int,
                           response: Response,
                           db: Session = Depends(get_db),
                           token: str = Depends(pengaturan.oauth2_scheme)):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Customer).filter(models.Customer.id == id).first()
        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success get detail customer"
    except:
        data = None
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data
    }
