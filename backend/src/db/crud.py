from sqlalchemy.orm import Session
from . import models, schemas
import uuid

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_google_id(db: Session, google_id: str):
    return db.query(models.User).filter(models.User.google_id == google_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    # Check if user already exists
    if user.google_id:
        existing = db.query(models.User).filter(models.User.google_id == user.google_id).first()
        if existing:
            return existing
    if user.email:
        existing = db.query(models.User).filter(models.User.email == user.email).first()
        if existing:
            return existing
    if user.username:
        existing = db.query(models.User).filter(models.User.username == user.username).first()
        if existing:
            return existing

    db_user = models.User(
        username=user.username or f"user_{uuid.uuid4().hex[:8]}",
        google_id=user.google_id,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_scan_session(db: Session, session: schemas.ScanSessionCreate):
    db_session = models.ScanSession(
        id=session.id,
        user_id=session.user_id,
        skin_type=session.skin_type
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def create_scan_result(db: Session, session_id: str, result: schemas.ScanResultCreate):
    db_result = models.ScanResult(
        session_id=session_id,
        ingredients=result.ingredients,
        safety_score=result.safety_score,
        analysis_report=result.analysis_report
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

def get_scan_history(db: Session, limit: int = 100):
    return db.query(models.ScanSession).order_by(models.ScanSession.created_at.desc()).limit(limit).all()

def get_user_scan_history(db: Session, user_id: int, limit: int = 100):
    return db.query(models.ScanSession).filter(models.ScanSession.user_id == user_id).order_by(models.ScanSession.created_at.desc()).limit(limit).all()
