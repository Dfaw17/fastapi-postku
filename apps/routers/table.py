from fastapi import APIRouter, Response, Depends, Form, status
from sqlalchemy.orm import Session
from apps import database, models, pengaturan
from pydantic import BaseModel
import time

get_db = database.get_db
router = APIRouter(tags=['TABLE SERVICE'])


class CreateTable(BaseModel):
    name: str
    note: str
    toko_id: int

    class Config:
        orm_mode = True


class EditTable(BaseModel):
    name: str
    note: str
    table_id: int

    class Config:
        orm_mode = True


class TableID(BaseModel):
    table_id: int

    class Config:
        orm_mode = True


@router.post('/table')
async def create_table(
        response: Response,
        req: CreateTable,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data_toko = db.query(models.Toko).filter(models.Toko.id == req.toko_id).first()
        createdAt = int(round(time.time() * 1000))

        new_table = models.Table(name=req.name, note=req.note, createdAt=createdAt, is_deleted=0)
        data_toko.table.append(new_table)

        db.add(new_table)
        db.commit()
        db.refresh(new_table)
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success created table"
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
        new_table = None
    return {
        "status_code": status_code,
        "msg": msg,
        "data": new_table
    }


@router.put('/table')
async def edit_table(
        response: Response,
        req: EditTable,
        db: Session = Depends(get_db),
        token: str = Depends(pengaturan.oauth2_scheme),
):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Table).filter(models.Table.id == req.table_id)
        data.update({
            "name": req.name,
            "note": req.note,
        })
        db.commit()
        status_code = response.status_code = status.HTTP_201_CREATED
        msg = "Success edit table"
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


@router.patch('/table')
async def delete_table(response: Response,
                       req: TableID,
                       db: Session = Depends(get_db),
                       token: str = Depends(pengaturan.oauth2_scheme),
                       ):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Table).filter(models.Table.id == req.table_id)

        data.update({
            "is_deleted": 1,
        })
        db.commit()
        msg = "Success delete table"
        status_code = response.status_code = status.HTTP_200_OK
    except:
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
    }


@router.get('/table/{id}')
async def detail_table(id: int,
                       response: Response,
                       db: Session = Depends(get_db),
                       token: str = Depends(pengaturan.oauth2_scheme)):
    try:
        pengaturan.verify_token(token)
        data = db.query(models.Table).filter(models.Table.id == id).first()
        status_code = response.status_code = status.HTTP_200_OK
        msg = "Success get detail tableory"
    except:
        data = None
        msg = "Token Expired/Invalid"
        status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    return {
        "status_code": status_code,
        "msg": msg,
        "data": data
    }
