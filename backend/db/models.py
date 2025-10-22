from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    phone = Column(String(20), unique=True, nullable=True)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    from_city = Column(String(100))
    to_city = Column(String(100))
    date = Column(Date)
    price = Column(Numeric(10, 2))
    source = Column(String(50))
    status = Column(String(20), default="confirmed")
    booking_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User")
