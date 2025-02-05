from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional, Dict, Any
from core.interfaces.persistence import IPersonRepository, IRecognitionLogRepository
from core.entities.person import Person, RecognitionLog
from database.models import Person as PersonModel
from database.models import FaceRecognitionLog as LogModel

class PersonRepository(IPersonRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def add(self, name: str, face_encoding: bytes, details: Dict[str, Any]) -> int:
        try:
            person = PersonModel(
                name=name,
                face_encoding=face_encoding,
                is_active=True,
                created_at=datetime.now(),
                details=details,
                email=details.get('email'),
                phone=details.get('phone'),
                department=details.get('department'),
                access_level=details.get('access_level', 1),
                photo_path=details.get('photo_path')
            )
            self.session.add(person)
            self.session.commit()
            return person.id
        except Exception as e:
            self.session.rollback()
            raise RuntimeError(f"Kişi eklenirken hata: {str(e)}")
    
    def get_by_id(self, person_id: int) -> Optional[Dict[str, Any]]:
        try:
            person = self.session.query(PersonModel).filter_by(id=person_id).first()
            if person:
                return {
                    'id': person.id,
                    'name': person.name,
                    'face_encoding': person.face_encoding,
                    'is_active': person.is_active,
                    'created_at': person.created_at,
                    'details': person.details,
                    'email': person.email,
                    'phone': person.phone,
                    'department': person.department,
                    'access_level': person.access_level,
                    'last_seen': person.last_seen,
                    'photo_path': person.photo_path
                }
            return None
        except Exception as e:
            raise RuntimeError(f"Kişi bilgileri alınırken hata: {str(e)}")
    
    def get_all_active(self) -> List[Dict[str, Any]]:
        try:
            persons = self.session.query(PersonModel).filter_by(is_active=True).all()
            return [{
                'id': p.id,
                'name': p.name,
                'face_encoding': p.face_encoding,
                'is_active': p.is_active,
                'created_at': p.created_at,
                'details': p.details,
                'email': p.email,
                'phone': p.phone,
                'department': p.department,
                'access_level': p.access_level,
                'last_seen': p.last_seen,
                'photo_path': p.photo_path
            } for p in persons]
        except Exception as e:
            raise RuntimeError(f"Aktif kişiler alınırken hata: {str(e)}")
    
    def update(self, person_id: int, details: Dict[str, Any]) -> bool:
        try:
            person = self.session.query(PersonModel).filter_by(id=person_id).first()
            if person:
                for key, value in details.items():
                    if hasattr(person, key):
                        setattr(person, key, value)
                person.updated_at = datetime.now()
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            raise RuntimeError(f"Kişi güncellenirken hata: {str(e)}")
    
    def deactivate(self, person_id: int) -> bool:
        try:
            person = self.session.query(PersonModel).filter_by(id=person_id).first()
            if person:
                person.is_active = False
                person.updated_at = datetime.now()
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            raise RuntimeError(f"Kişi deaktive edilirken hata: {str(e)}")

class RecognitionLogRepository(IRecognitionLogRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def add_log(self, person_id: int, confidence_score: float, timestamp: datetime) -> int:
        try:
            log = LogModel(
                person_id=person_id,
                confidence_score=confidence_score,
                timestamp=timestamp
            )
            self.session.add(log)
            self.session.commit()
            return log.id
        except Exception as e:
            self.session.rollback()
            raise RuntimeError(f"Log eklenirken hata: {str(e)}")
    
    def get_logs(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        try:
            logs = self.session.query(LogModel).filter(
                LogModel.timestamp.between(start_date, end_date)
            ).all()
            return [{
                'id': log.id,
                'person_id': log.person_id,
                'confidence_score': log.confidence_score,
                'timestamp': log.timestamp
            } for log in logs]
        except Exception as e:
            raise RuntimeError(f"Loglar alınırken hata: {str(e)}") 