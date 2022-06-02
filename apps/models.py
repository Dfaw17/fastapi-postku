from sqlalchemy.orm import relationship

from apps import database
from sqlalchemy import Column, Integer, String, Text, Boolean, Table, ForeignKey, BigInteger, Float

account_toko = Table('account_toko', database.Base.metadata,
                     Column('id', Integer(), primary_key=True, index=True),
                     Column('account_id', Integer(), ForeignKey('account.id')),
                     Column('toko_id', Integer(), ForeignKey('toko.id')),
                     )

cart_servicefee = Table('cart_servicefee', database.Base.metadata,
                        Column('id', Integer(), primary_key=True, index=True),
                        Column('cart_id', Integer(), ForeignKey('cart.id')),
                        Column('servicefee_id', Integer(), ForeignKey('servicefee.id')),
                        )

transaction_settlement = Table('transaction_settlement', database.Base.metadata,
                               Column('id', Integer(), primary_key=True, index=True),
                               Column('transaction_id', Integer(), ForeignKey('transaction.id')),
                               Column('settlement_id', Integer(), ForeignKey('settlement.id')),
                               )


class Account(database.Base):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    email = Column(String(256))
    pwd = Column(String(640))
    ecd = Column(String(640))
    key_ecd = Column(String(640))
    phone = Column(String(256))
    address = Column(Text)
    no_rekening = Column(String(256))
    jenis_bank = Column(String(256))
    photo_profile = Column(Text)
    photo_profile_url = Column(Text)
    photo_norek = Column(Text)
    photo_norek_url = Column(Text)
    account_type = Column(Integer)
    OTP = Column(Integer)
    createdAt = Column(String(128))
    is_deleted = Column(Boolean)

    toko = relationship('Toko', secondary=account_toko, back_populates='account', lazy='dynamic')
    kritiksaran = relationship('KritikSaran', back_populates='account')
    absen = relationship('Absen', back_populates='account')
    cart = relationship('Cart', back_populates='account')
    transaction = relationship('Transaction', back_populates='account')


class Toko(database.Base):
    __tablename__ = 'toko'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    address = Column(String(384))
    province = Column(String(256))
    city = Column(String(256))
    district = Column(String(256))
    village = Column(String(256))
    category = Column(String(128))
    photo_logo = Column(Text)
    photo_logo_url = Column(Text)
    is_deleted = Column(Boolean)
    createdAt = Column(String(128))

    account = relationship('Account', secondary=account_toko, back_populates='toko', lazy='dynamic', )
    kategori_menu = relationship('KategoriMenu', back_populates='toko')
    menu = relationship('Menu', back_populates='toko')
    customer = relationship('Customer', back_populates='toko')
    table = relationship('Table', back_populates='toko')
    ordertype = relationship('OrderType', back_populates='toko')
    labelorder = relationship('LabelOrder', back_populates='toko')
    discount = relationship('Discount', back_populates='toko')
    pajak = relationship('Pajak', back_populates='toko')
    servicefee = relationship('ServiceFee', back_populates='toko')
    absen = relationship('Absen', back_populates='toko')
    cartitem = relationship('CartItem', back_populates='toko')
    cart = relationship('Cart', back_populates='toko')
    transaction = relationship('Transaction', back_populates='toko')
    settlement = relationship('Settlement', back_populates='toko')


class KategoriMenu(database.Base):
    __tablename__ = 'kategori_menu'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    is_deleted = Column(Boolean)
    createdAt = Column(String(128))
    toko_id = Column(Integer, ForeignKey('toko.id'))

    toko = relationship('Toko', back_populates='kategori_menu')
    menu = relationship('Menu', back_populates='kategori_menu')
    cartitem = relationship('CartItem', back_populates='kategori_menu')


class Customer(database.Base):
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    phone = Column(String(256))
    email = Column(String(256))
    createdAt = Column(String(128))
    toko_id = Column(Integer, ForeignKey('toko.id'))
    is_deleted = Column(Boolean)

    toko = relationship('Toko', back_populates='customer')
    cart = relationship('Cart', back_populates='customer')


class Menu(database.Base):
    __tablename__ = 'menu'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    desc = Column(String(384))
    harga_asli = Column(BigInteger)
    harga_jual = Column(BigInteger)
    is_deleted = Column(Boolean)
    is_stock = Column(Boolean)
    current_stock = Column(BigInteger)
    photo_menu = Column(Text)
    photo_menu_url = Column(Text)
    createdAt = Column(String(128))
    kategori_id = Column(Integer, ForeignKey('kategori_menu.id'))
    toko_id = Column(Integer, ForeignKey('toko.id'))

    kategori_menu = relationship('KategoriMenu', back_populates='menu')
    toko = relationship('Toko', back_populates='menu')
    cartitem = relationship('CartItem', back_populates='menu')
    historystockmenu = relationship('HistoryStockMenu', back_populates='menu')


# 1 = tambah, 2 = kurang, 3 = reset, 4 = penjualan
class HistoryStockMenu(database.Base):
    __tablename__ = 'historystockmenu'

    id = Column(Integer, primary_key=True, index=True)
    adjustment_stock = Column(BigInteger)
    type = Column(Integer)
    note = Column(Text)
    menu_id = Column(Integer, ForeignKey('menu.id'))
    createdAt = Column(String(128))

    menu = relationship('Menu', back_populates='historystockmenu')


class Table(database.Base):
    __tablename__ = 'table'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    note = Column(String(256))
    createdAt = Column(String(128))
    toko_id = Column(Integer, ForeignKey('toko.id'))
    is_deleted = Column(Boolean)
    is_booked = Column(Boolean)

    toko = relationship('Toko', back_populates='table')
    cart = relationship('Cart', back_populates='table')


class OrderType(database.Base):
    __tablename__ = 'ordertype'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    desc = Column(String(256))
    toko_id = Column(Integer, ForeignKey('toko.id'))
    is_deleted = Column(Boolean)
    createdAt = Column(String(128))

    toko = relationship('Toko', back_populates='ordertype')
    cart = relationship('Cart', back_populates='ordertype')


class LabelOrder(database.Base):
    __tablename__ = 'labelorder'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    desc = Column(String(256))
    toko_id = Column(Integer, ForeignKey('toko.id'))
    is_deleted = Column(Boolean)
    createdAt = Column(String(128))

    toko = relationship('Toko', back_populates='labelorder')
    cart = relationship('Cart', back_populates='labelorder')


class Discount(database.Base):
    __tablename__ = 'discount'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    nominal = Column(BigInteger)
    type_disc = Column(Integer)
    toko_id = Column(Integer, ForeignKey('toko.id'))
    is_deleted = Column(Boolean)
    createdAt = Column(String(128))

    toko = relationship('Toko', back_populates='discount')
    cartitem = relationship('CartItem', back_populates='discount')
    cart = relationship('Cart', back_populates='discount')


class Pajak(database.Base):
    __tablename__ = 'pajak'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    nominal = Column(BigInteger)
    type_pajak = Column(Integer)
    toko_id = Column(Integer, ForeignKey('toko.id'))
    is_deleted = Column(Boolean)
    createdAt = Column(String(128))

    toko = relationship('Toko', back_populates='pajak')
    cart = relationship('Cart', back_populates='pajak')


class ServiceFee(database.Base):
    __tablename__ = 'servicefee'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    nominal = Column(BigInteger)
    toko_id = Column(Integer, ForeignKey('toko.id'))
    is_deleted = Column(Boolean)
    createdAt = Column(String(128))

    toko = relationship('Toko', back_populates='servicefee')
    cart = relationship('Cart', secondary=cart_servicefee, back_populates='servicefee', lazy='dynamic', )


class Bank(database.Base):
    __tablename__ = 'bank'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    code = Column(Integer)
    created_at = Column(String(128))


class Banner(database.Base):
    __tablename__ = 'banner'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    body = Column(Text)
    photo_banner = Column(Text)
    photo_banner_url = Column(Text)
    is_deleted = Column(Boolean)
    createdAt = Column(String(128))


class Article(database.Base):
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    body = Column(Text)
    count_seen = Column(BigInteger)
    photo_article = Column(Text)
    photo_article_url = Column(Text)
    is_deleted = Column(Boolean)
    createdAt = Column(String(128))


class KritikSaran(database.Base):
    __tablename__ = 'kritiksaran'

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(256))
    body = Column(Text)
    account_id = Column(Integer, ForeignKey('account.id'))
    createdAt = Column(String(128))

    account = relationship('Account', back_populates='kritiksaran')


class Absen(database.Base):
    __tablename__ = 'absen'

    id = Column(Integer, primary_key=True, index=True)
    photo_absen1 = Column(Text)
    photo_absen1_url = Column(Text)
    time_abesen1 = Column(String(128))
    photo_absen2 = Column(Text)
    photo_absen2_url = Column(Text)
    time_abesen2 = Column(String(128))
    account_id = Column(Integer, ForeignKey('account.id'))
    toko_id = Column(Integer, ForeignKey('toko.id'))
    createdAt = Column(String(128))

    account = relationship('Account', back_populates='absen')
    toko = relationship('Toko', back_populates='absen')


class Payment(database.Base):
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True, index=True)
    paymnet = Column(String(256))
    createdAt = Column(String(128))

    transaction = relationship('Transaction', back_populates='payment')


class ContactUs(database.Base):
    __tablename__ = 'contactus'

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(256))
    value = Column(String(256))
    url = Column(String(256))
    photo_contactus = Column(Text)
    photo_contactus_url = Column(Text)
    createdAt = Column(String(128))


class Cart(database.Base):
    __tablename__ = 'cart'

    id = Column(Integer, primary_key=True, index=True)
    cart_code = Column(String(256))
    nama_cart = Column(String(256))
    ordered = Column(Boolean)
    total_price_item = Column(Float)
    total_disc = Column(Float)
    sub_total_price = Column(Float)
    total_pajak = Column(Float)
    total_service_fee = Column(Float)
    grand_total_price = Column(Float)
    total_item = Column(Integer)
    is_canceled = Column(Boolean)
    account_id = Column(Integer, ForeignKey('account.id'))
    toko_id = Column(Integer, ForeignKey('toko.id'))
    disc_id = Column(Integer, ForeignKey('discount.id'))
    pajak_id = Column(Integer, ForeignKey('pajak.id'))
    ordertype_id = Column(Integer, ForeignKey('ordertype.id'))
    labelorder_id = Column(Integer, ForeignKey('labelorder.id'))
    table_id = Column(Integer, ForeignKey('table.id'))
    customer_id = Column(Integer, ForeignKey('customer.id'))
    createdAt = Column(String(128))

    servicefee = relationship('ServiceFee', secondary=cart_servicefee, back_populates='cart', lazy='dynamic')
    cartitem = relationship('CartItem', back_populates='cart')
    account = relationship('Account', back_populates='cart')
    toko = relationship('Toko', back_populates='cart')
    discount = relationship('Discount', back_populates='cart')
    pajak = relationship('Pajak', back_populates='cart')
    ordertype = relationship('OrderType', back_populates='cart')
    labelorder = relationship('LabelOrder', back_populates='cart')
    customer = relationship('Customer', back_populates='cart')
    table = relationship('Table', back_populates='cart')
    transaction = relationship('Transaction', back_populates='cart')


class CartItem(database.Base):
    __tablename__ = 'cartitem'

    id = Column(Integer, primary_key=True, index=True)
    qty = Column(Integer)
    ordered = Column(Boolean)
    ordered_at = Column(String(128))
    price = Column(Float)
    hpp = Column(Float)
    total_disc = Column(Float)
    grand_total_price = Column(Float)
    is_cancel = Column(Boolean)
    cart_id = Column(Integer, ForeignKey('cart.id'))
    menu_id = Column(Integer, ForeignKey('menu.id'))
    menu_kat_id = Column(Integer, ForeignKey('kategori_menu.id'))
    toko_id = Column(Integer, ForeignKey('toko.id'))
    disc_id = Column(Integer, ForeignKey('discount.id'))
    createdAt = Column(String(128))

    cart = relationship('Cart', back_populates='cartitem')
    menu = relationship('Menu', back_populates='cartitem')
    kategori_menu = relationship('KategoriMenu', back_populates='cartitem')
    toko = relationship('Toko', back_populates='cartitem')
    discount = relationship('Discount', back_populates='cartitem')


class Transaction(database.Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True, index=True)
    reff_code = Column(String(256))
    sub_total_price = Column(Float)
    total_pajak = Column(Float)
    grand_total_price = Column(Float)
    uang_bayar = Column(Float)
    uang_kembalian = Column(Float)
    is_cancel = Column(Boolean)
    is_settlement = Column(Boolean)
    payment_id = Column(Integer, ForeignKey('payment.id'))
    cart_id = Column(Integer, ForeignKey('cart.id'))
    toko_id = Column(Integer, ForeignKey('toko.id'))
    account_id = Column(Integer, ForeignKey('account.id'))
    createdAt = Column(String(128))

    settlement = relationship('Settlement', secondary=transaction_settlement, back_populates='transaction',
                              lazy='dynamic')
    cart = relationship('Cart', back_populates='transaction')
    payment = relationship('Payment', back_populates='transaction')
    toko = relationship('Toko', back_populates='transaction')
    account = relationship('Account', back_populates='transaction')


class CallbackXendit(database.Base):
    __tablename__ = 'callbackxendit'

    id = Column(Integer, primary_key=True, index=True)
    event = Column(String(256))
    external_id = Column(String(256))
    ammount = Column(Float)
    status = Column(String(256))
    createdAt = Column(String(128))


class ChannelTopup(database.Base):
    __tablename__ = 'channeltopup'

    id = Column(Integer, primary_key=True, index=True)
    jenis_pembayaran = Column(String(256))
    nama = Column(String(256))
    nomer = Column(String(256))
    photo_logo = Column(Text)
    photo_logo_url = Column(Text)
    createdAt = Column(String(128))


class Settlement(database.Base):
    __tablename__ = 'settlement'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    status_settelement = Column(String(256))
    grand_total_price = Column(Float)
    photo_bukti = Column(Text)
    photo_bukti_url = Column(Text)
    toko_id = Column(Integer, ForeignKey('toko.id'))
    createdAt = Column(String(128))

    transaction = relationship('Transaction', secondary=transaction_settlement, back_populates='settlement',
                               lazy='dynamic')
    toko = relationship('Toko', back_populates='settlement')
