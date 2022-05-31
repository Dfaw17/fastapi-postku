from fastapi import FastAPI
from apps import database
from apps.routers import account, toko, menu, kategori_menu, pelanggan, table, ordertype, labelorder, discount, pajak, \
    servicefee, banner, article, kritiksaran, absen, payment, contactus, transaction, qris

app = FastAPI(title="MICROSERVICE POSTKU", description="Dokumentasi Backend Service POSTKU System",
              swagger_ui_parameters={"defaultModelsExpandDepth": -1})
database.Base.metadata.create_all(database.engine)

# =============================================== ROUTERS ===============================================
app.include_router(account.router)
app.include_router(toko.router)
app.include_router(menu.router)
app.include_router(kategori_menu.router)
app.include_router(pelanggan.router)
app.include_router(table.router)
app.include_router(ordertype.router)
app.include_router(labelorder.router)
app.include_router(discount.router)
app.include_router(pajak.router)
app.include_router(servicefee.router)
app.include_router(banner.router)
app.include_router(article.router)
app.include_router(kritiksaran.router)
app.include_router(absen.router)
app.include_router(payment.router)
app.include_router(contactus.router)
app.include_router(transaction.router)
app.include_router(qris.router)
