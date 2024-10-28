from sqlalchemy import Column , Integer , String , ForeignKey , Float , Boolean
from database import base
from sqlalchemy.orm import relationship


class User(base):
    __tablename__ ='User'

    id = Column(Integer , primary_key=True , index=True)
    email = Column(String , nullable=False)
    username = Column(String , nullable=False)
    password = Column(String , nullable=False)
    user_type = Column(String , nullable=False)
    otp = Column(String)
    is_verified = Column(Boolean , default=False)

    shop = relationship('Shop' , back_populates='user')
    book = relationship('Book' , back_populates='user')
    cart = relationship('Cart' , back_populates='user' ,uselist=False)  # Each user has one cart
    payment = relationship('Payment' , back_populates='user')

class Shop(base):
    __tablename__ = 'Shop'

    id=Column(Integer , primary_key=True,index=True)
    shop_name = Column(String , nullable=False)
    user_id = Column(Integer , ForeignKey('User.id'))

    user = relationship('User', back_populates= 'shop')
    book = relationship('Book' , back_populates='shop')
    cart_items = relationship('CartItem' , back_populates='shop')

class Book(base):
    __tablename__ = 'Book'

    id = Column(Integer , primary_key=True , index=True)
    book_name = Column(String , nullable=False , unique=True)
    price = Column(Float , nullable=False)
    stock_quantity = Column(Integer , default=1)
    shop_id = Column(Integer , ForeignKey('Shop.id'))
    user_id = Column(Integer , ForeignKey('User.id'))

    shop = relationship('Shop' , back_populates='book')
    user = relationship('User', back_populates='book')
    cart_items = relationship('CartItem', back_populates='book')

class Cart(base):
    __tablename__ = 'Cart'

    id = Column(Integer, primary_key=True, index=True)
    total_price = Column(Float, nullable=False, default=0.0)
    buyer_id = Column(Integer, ForeignKey('User.id'))

    user = relationship('User', back_populates='cart')
    cart_items = relationship('CartItem', back_populates='cart')

class CartItem(base):
    __tablename__ = 'CartItem'

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, default=1)
    book_id = Column(Integer, ForeignKey('Book.id'))
    cart_id = Column(Integer, ForeignKey('Cart.id'))
    shop_id = Column(Integer, ForeignKey('Shop.id'))

    book = relationship('Book', back_populates='cart_items')
    cart = relationship('Cart', back_populates='cart_items')
    shop = relationship('Shop', back_populates='cart_items')

class Payment(base):
    __tablename__ = 'Payment'

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)  # Total payment amount
    payment_method = Column(String, nullable=False)  # e.g., 'Credit Card', 'PayPal', etc.
    payment_status = Column(String, nullable=False, default='pending')  # 'pending', 'completed', 'failed'
    user_id = Column(Integer, ForeignKey('User.id'))  # Reference to the buyer

    user = relationship('User', back_populates='payment')