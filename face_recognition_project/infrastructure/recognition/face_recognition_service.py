import face_recognition
import numpy as np
from typing import List, Optional, Tuple
from core.interfaces.recognition import IFaceRecognitionService

class FaceRecognitionService(IFaceRecognitionService):
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Görüntüdeki yüzleri tespit eder."""
        try:
            return face_recognition.face_locations(image)
        except Exception as e:
            raise RuntimeError(f"Yüz tespiti sırasında hata: {str(e)}")
    
    def encode_face(self, image: np.ndarray, face_location: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """Tespit edilen yüzün kodlamasını oluşturur."""
        try:
            face_encodings = face_recognition.face_encodings(image, [face_location])
            return face_encodings[0] if face_encodings else None
        except Exception as e:
            raise RuntimeError(f"Yüz kodlama sırasında hata: {str(e)}")
    
    def compare_faces(self, face_encoding: np.ndarray, known_face_encodings: List[np.ndarray], tolerance: float = 0.6) -> List[bool]:
        """Verilen yüz kodlamasını bilinen yüzlerle karşılaştırır."""
        try:
            return face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance)
        except Exception as e:
            raise RuntimeError(f"Yüz karşılaştırma sırasında hata: {str(e)}")
            
    def get_face_distance(self, face_encoding: np.ndarray, known_face_encoding: np.ndarray) -> float:
        """İki yüz kodlaması arasındaki mesafeyi hesaplar."""
        try:
            return face_recognition.face_distance([known_face_encoding], face_encoding)[0]
        except Exception as e:
            raise RuntimeError(f"Yüz mesafesi hesaplanırken hata: {str(e)}")
            
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Görüntüyü yüz tanıma için hazırlar."""
        try:
            # Görüntüyü RGB formatına dönüştür
            if len(image.shape) == 2:  # Gri tonlamalı görüntü
                return np.stack((image,) * 3, axis=-1)
            elif image.shape[2] == 4:  # RGBA görüntü
                return image[:, :, :3]
            return image
        except Exception as e:
            raise RuntimeError(f"Görüntü ön işleme sırasında hata: {str(e)}") 