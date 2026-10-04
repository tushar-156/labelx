from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    scans = relationship("ScanSession", back_populates="user")

class ScanSession(Base):
    __tablename__ = "scan_sessions"

    id = Column(String, primary_key=True, index=True) # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    skin_type = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="scans")
    results = relationship("ScanResult", back_populates="session")

class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("scan_sessions.id"))
    ingredients = Column(JSON) # List of ingredients extracted
    safety_score = Column(Float, nullable=True)
    analysis_report = Column(String) # Raw or formatted analysis output
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ScanSession", back_populates="results")
