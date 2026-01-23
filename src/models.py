from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from src.database import Base

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    ts_code = Column(String, index=True)
    name = Column(String)
    quantity = Column(Integer)
    cost_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
