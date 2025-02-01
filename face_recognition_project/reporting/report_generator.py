import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from database.models import FaceRecognitionLog
import logging


class ReportGenerator:
    def __init__(self, db_session):
        self.session = db_session
        self.logger = logging.getLogger(__name__)

    def generate_daily_report(self, date=None):
        try:
            if not date:
                date = datetime.now()

            # Günlük tanıma istatistikleri
            daily_stats = self.session.query(
                FaceRecognitionLog
            ).filter(
                FaceRecognitionLog.timestamp >= date.date()
            ).all()

            return self.create_report(daily_stats)
        except Exception as e:
            self.logger.error(f"Rapor oluşturulurken hata: {str(e)}")
            raise

    def create_report(self, data):
        try:
            # DataFrame oluştur
            df = pd.DataFrame([{
                'timestamp': log.timestamp,
                'person_id': log.person_id,
                'confidence_score': log.confidence_score,
                'location': log.location
            } for log in data])

            # İstatistikleri hesapla
            stats = {
                'total_recognitions': len(df),
                'unique_persons': df['person_id'].nunique(),
                'avg_confidence': df['confidence_score'].mean()
            }

            return stats
        except Exception as e:
            self.logger.error(f"Rapor detayları oluşturulurken hata: {str(e)}")
            raise