from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ScanResultBase(BaseModel):
    ingredients: List[str]
    safety_score: Optional[float] = None
    analysis_report: str

class ScanResultCreate(ScanResultBase):
    pass

class ScanResult(ScanResultBase):
    id: int
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ScanSessionBase(BaseModel):
    id: str
    skin_type: Optional[str] = None

class ScanSessionCreate(ScanSessionBase):
    user_id: Optional[int] = None

class ScanSession(ScanSessionBase):
    user_id: Optional[int] = None
    created_at: datetime
    results: List[ScanResult] = []

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: Optional[str] = None
    google_id: Optional[str] = None
    email: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime
    scans: List[ScanSession] = []

    class Config:
        from_attributes = True
