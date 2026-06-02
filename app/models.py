from sqlalchemy import Column, Integer, String
from .database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    target = Column(String, index=True)
    risk = Column(String, default="unknown")
