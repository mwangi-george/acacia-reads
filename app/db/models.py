import shortuuid
from datetime import timezone, datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float, Enum, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from app.db.enumerated_types import BookCategory, OrderStatus

# Base class for all db models
Base = declarative_base()

class TimestampMixin:
    """Base tracking for all models"""
    added_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))



class Author(Base, TimestampMixin):
    """Author model
    
    Fields:
        - author_id (str)
        - first_name (str)
        - last_name (str)
        - email (str)
        - bio (str)
        - books (list)
        - added_at (datetime)
        - updated_at (datetime)
    """
    __tablename__ = 'authors'
    
    author_id = Column(String(22), primary_key=True, unique=True, index=True, default=shortuuid.uuid)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(60), nullable=False, unique=True, index=True)
    bio = Column(Text, nullable=True)

    # relationships
    books = relationship('Book', back_populates='author', lazy="joined", cascade="all, delete-orphan")



class Book(Base, TimestampMixin):
    """Book model
    
    Fields:
        - book_id (str)
        - author_id (str)
        - title (str)
        - description (str)
        - isbn (str)
        - price (float)
        - category (BookCategory)
        - added_at (datetime)
        - updated_at (datetime)
    """
    __tablename__ = 'books'
    
    book_id = Column(String(22), primary_key=True, unique=True, index=True, default=shortuuid.uuid)
    author_id = Column(String(22), ForeignKey('authors.author_id'), nullable=False, index=True)  # deliberately allowed one author
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    isbn = Column(String(22), nullable=False, unique=True, index=True)
    price = Column(Float, nullable=False)
    category = Column(Enum(BookCategory), nullable=False, index=True)
    stock_count = Column(Integer, nullable=False, default=0)  # Inventory stock
    
    # relationships
    author = relationship('Author', back_populates="books")
    order_items = relationship('OrderItem', back_populates='book', lazy="joined", cascade="all, delete-orphan")



class Customer(Base, TimestampMixin):
    """Customer model
    
    Fields:
        - customer_id (str)
        - name (str)
        - email (str)
        - hashed_password (str)
        - added_at (datetime)
        - updated_at (datetime)
    """
    
    __tablename__ = 'customers'
    customer_id = Column(String(22), primary_key=True, unique=True, index=True, default=shortuuid.uuid)
    name = Column(String(100), nullable=False)
    email = Column(String(60), nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)

    # relationships
    orders =relationship('Order', back_populates='customer', lazy="joined", cascade="all, delete-orphan")



class Order(Base, TimestampMixin):
    """Order model

    Fields:
    - order_id (str)
    - customer_id (int)
    - order_date (datetime)
    - order_status (str)
    - added_at (datetime)
    - updated_at (datetime)
    """
    __tablename__ = 'orders'
    order_id = Column(String(22), primary_key=True, unique=True, index=True, default=shortuuid.uuid)
    customer_id = Column(String(22), ForeignKey('customers.customer_id'), nullable=False, index=True)
    order_date = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    order_status = Column(Enum(OrderStatus), nullable=False, index=True)

    # relationships
    customer = relationship('Customer', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order', lazy="joined", cascade="all, delete-orphan")
    


class OrderItem(Base, TimestampMixin):
    """OrderItem model

    Fields:
        - order_item_id (int)
        - order_id (str)
        - book_id (str)
        - quantity (int)
        - unit_price (float)
        - total_price (float)
        - added_at (datetime)
        - updated_at (datetime)
    """
    __tablename__ = 'order_items'
    order_item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(22), ForeignKey('orders.order_id'), nullable=False)
    book_id = Column(String(22), ForeignKey('books.book_id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    @hybrid_property
    def total_price(self):
        return self.quantity * self.unit_price

    # relationships
    order = relationship('Order', back_populates='order_items')
    book = relationship('Book', back_populates='order_items')