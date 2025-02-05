from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class Person:
    id: Optional[int]
    name: str
    face_encoding: bytes
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    details: Dict[str, Any]
    email: Optional[str]
    phone: Optional[str]
    department: Optional[str]
    access_level: int
    last_seen: Optional[datetime]
    photo_path: Optional[str]

@dataclass
class RecognitionLog:
    id: Optional[int]
    person_id: int
    confidence_score: float
    timestamp: datetime

@dataclass
class SystemLog:
    id: Optional[int]
    timestamp: datetime
    level: str
    message: str
    details: Optional[Dict[str, Any]] 