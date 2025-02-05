import cv2
import numpy as np
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from core.interfaces.recognition import IFaceRecognitionService
from core.interfaces.persistence import IPersonRepository, IRecognitionLogRepository

class RecognitionService:
    def __init__(
        self,
        face_recognition: IFaceRecognitionService,
        person_repository: IPersonRepository,
        log_repository: IRecognitionLogRepository
    ):
        self.face_recognition = face_recognition
        self.person_repository = person_repository
        self.log_repository = log_repository
        self.known_faces = self._load_known_faces()
    
    def _load_known_faces(self) -> Dict[int, Tuple[str, np.ndarray]]:
        """Veritabanından bilinen yüzleri yükler."""
        persons = self.person_repository.get_all_active()
        return {
            p['id']: (p['name'], np.frombuffer(p['face_encoding']))
            for p in persons
        }
    
    def add_person(self, image_path: str, name: str, details: Dict[str, Any]) -> int:
        """Yeni bir kişi ekler."""
        try:
            # Görüntüyü yükle
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Görüntü yüklenemedi")
            
            # RGB'ye dönüştür
            image = self.face_recognition.preprocess_image(image)
            
            # Yüzü tespit et
            face_locations = self.face_recognition.detect_faces(image)
            if not face_locations:
                raise ValueError("Görüntüde yüz bulunamadı")
            
            # İlk yüzü kodla
            face_encoding = self.face_recognition.encode_face(image, face_locations[0])
            if face_encoding is None:
                raise ValueError("Yüz kodlanamadı")
            
            # Kişiyi veritabanına ekle
            details['photo_path'] = image_path
            person_id = self.person_repository.add(name, face_encoding.tobytes(), details)
            
            # Bilinen yüzleri güncelle
            self.known_faces[person_id] = (name, face_encoding)
            
            return person_id
            
        except Exception as e:
            raise RuntimeError(f"Kişi eklenirken hata: {str(e)}")
    
    def recognize_face(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Görüntüdeki yüzleri tanır."""
        try:
            # Görüntüyü hazırla
            image = self.face_recognition.preprocess_image(image)
            
            # Yüzleri tespit et
            face_locations = self.face_recognition.detect_faces(image)
            results = []
            
            for face_location in face_locations:
                # Yüzü kodla
                face_encoding = self.face_recognition.encode_face(image, face_location)
                if face_encoding is None:
                    continue
                
                # Bilinen yüzlerle karşılaştır
                known_encodings = [enc for _, enc in self.known_faces.values()]
                matches = self.face_recognition.compare_faces(face_encoding, known_encodings)
                
                if True in matches:
                    # Eşleşen yüzü bul
                    match_index = matches.index(True)
                    person_id = list(self.known_faces.keys())[match_index]
                    name = self.known_faces[person_id][0]
                    
                    # Güven skorunu hesapla
                    confidence = 1 - self.face_recognition.get_face_distance(
                        face_encoding,
                        known_encodings[match_index]
                    )
                    
                    # Logu kaydet
                    self.log_repository.add_log(
                        person_id=person_id,
                        confidence_score=float(confidence),
                        timestamp=datetime.now()
                    )
                    
                    results.append({
                        'person_id': person_id,
                        'name': name,
                        'confidence': confidence,
                        'location': face_location
                    })
                else:
                    results.append({
                        'person_id': None,
                        'name': 'Bilinmeyen',
                        'confidence': 0.0,
                        'location': face_location
                    })
            
            return results
            
        except Exception as e:
            raise RuntimeError(f"Yüz tanıma sırasında hata: {str(e)}")
    
    def update_person(self, person_id: int, details: Dict[str, Any]) -> bool:
        """Kişi bilgilerini günceller."""
        try:
            success = self.person_repository.update(person_id, details)
            if success and 'face_encoding' in details:
                # Bilinen yüzleri güncelle
                person = self.person_repository.get_by_id(person_id)
                if person:
                    self.known_faces[person_id] = (
                        person['name'],
                        np.frombuffer(person['face_encoding'])
                    )
            return success
        except Exception as e:
            raise RuntimeError(f"Kişi güncellenirken hata: {str(e)}")
    
    def deactivate_person(self, person_id: int) -> bool:
        """Kişiyi pasif duruma getirir."""
        try:
            success = self.person_repository.deactivate(person_id)
            if success and person_id in self.known_faces:
                del self.known_faces[person_id]
            return success
        except Exception as e:
            raise RuntimeError(f"Kişi deaktive edilirken hata: {str(e)}")
    
    def get_recognition_logs(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Tanıma loglarını getirir."""
        try:
            return self.log_repository.get_logs(start_date, end_date)
        except Exception as e:
            raise RuntimeError(f"Loglar alınırken hata: {str(e)}") 