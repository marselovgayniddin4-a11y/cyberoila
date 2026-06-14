from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base   # 👈 BU JUDA MUHIM

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    target = Column(String, index=True)
    risk = Column(String, default="unknown")
    report_type = Column(String, default="other")
    category = Column(String, default="other")
    description = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class Blacklist(Base):
    __tablename__ = "blacklist"

    id = Column(Integer, primary_key=True, index=True)
    target = Column(String, unique=True, index=True)
    reason = Column(String, default="auto")
    created_at = Column(DateTime, default=datetime.utcnow)
