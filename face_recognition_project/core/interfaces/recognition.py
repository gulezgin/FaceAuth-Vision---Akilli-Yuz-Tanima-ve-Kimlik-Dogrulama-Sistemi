from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import numpy as np

class IFaceRecognitionService(ABC):
    @abstractmethod
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Görüntüdeki yüzleri tespit eder.
        
        Args:
            image: İşlenecek görüntü
            
        Returns:
            Tespit edilen yüzlerin koordinatları [(top, right, bottom, left)]
        """
        pass
    
    @abstractmethod
    def encode_face(self, image: np.ndarray, face_location: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """Tespit edilen yüzün kodlamasını oluşturur.
        
        Args:
            image: Kaynak görüntü
            face_location: Yüzün koordinatları
            
        Returns:
            Yüz kodlaması veya None
        """
        pass
    
    @abstractmethod
    def compare_faces(self, face_encoding: np.ndarray, known_face_encodings: List[np.ndarray], tolerance: float = 0.6) -> List[bool]:
        """Verilen yüz kodlamasını bilinen yüzlerle karşılaştırır.
        
        Args:
            face_encoding: Karşılaştırılacak yüz kodlaması
            known_face_encodings: Bilinen yüz kodlamaları listesi
            tolerance: Eşleşme toleransı
            
        Returns:
            Eşleşme sonuçları listesi
        """
        pass 