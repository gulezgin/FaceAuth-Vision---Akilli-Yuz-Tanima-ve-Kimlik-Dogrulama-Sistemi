from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

class IPersonRepository(ABC):
    @abstractmethod
    def add(self, name: str, face_encoding: bytes, details: Dict[str, Any]) -> int:
        """Yeni bir kişi ekler.
        
        Args:
            name: Kişinin adı
            face_encoding: Yüz kodlaması
            details: Kişi detayları
            
        Returns:
            Eklenen kişinin ID'si
        """
        pass
    
    @abstractmethod
    def get_by_id(self, person_id: int) -> Optional[Dict[str, Any]]:
        """ID'ye göre kişi bilgilerini getirir.
        
        Args:
            person_id: Kişi ID'si
            
        Returns:
            Kişi bilgileri veya None
        """
        pass
    
    @abstractmethod
    def get_all_active(self) -> List[Dict[str, Any]]:
        """Aktif tüm kişileri getirir.
        
        Returns:
            Aktif kişiler listesi
        """
        pass
    
    @abstractmethod
    def update(self, person_id: int, details: Dict[str, Any]) -> bool:
        """Kişi bilgilerini günceller.
        
        Args:
            person_id: Kişi ID'si
            details: Güncellenecek bilgiler
            
        Returns:
            Güncelleme başarılı mı
        """
        pass
    
    @abstractmethod
    def deactivate(self, person_id: int) -> bool:
        """Kişiyi pasif duruma getirir.
        
        Args:
            person_id: Kişi ID'si
            
        Returns:
            İşlem başarılı mı
        """
        pass

class IRecognitionLogRepository(ABC):
    @abstractmethod
    def add_log(self, person_id: int, confidence_score: float, timestamp: datetime) -> int:
        """Yeni bir tanıma kaydı ekler.
        
        Args:
            person_id: Tanınan kişinin ID'si
            confidence_score: Tanıma güven skoru
            timestamp: İşlem zamanı
            
        Returns:
            Eklenen kaydın ID'si
        """
        pass
    
    @abstractmethod
    def get_logs(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Belirli tarih aralığındaki kayıtları getirir.
        
        Args:
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi
            
        Returns:
            Kayıt listesi
        """
        pass 