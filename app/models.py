"""SQLAlchemy ORM models."""
from sqlalchemy import Column, Integer, String, Float, Date
from app.database import Base


class Order(Base):
    """Order model representing an order in the database."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    order_date = Column(Date, nullable=False)
