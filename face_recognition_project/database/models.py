from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, LargeBinary, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.pool import QueuePool
import os

Base = declarative_base()


class Person(Base):
    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    face_encoding = Column(LargeBinary, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    
    recognition_logs = relationship("FaceRecognitionLog", back_populates="person")

    def __repr__(self):
        return f"<Person(name='{self.name}', created_at='{self.created_at}')>"


class FaceRecognitionLog(Base):
    __tablename__ = 'recognition_logs'

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'))
    confidence_score = Column(Float)
    timestamp = Column(DateTime, nullable=False)
    
    person = relationship("Person", back_populates="recognition_logs")

    def __repr__(self):
        return f"<FaceRecognitionLog(person_id={self.person_id}, confidence_score={self.confidence_score})>"


def get_database_engine(db_path):
    return create_engine(
        f"sqlite:///{db_path}",
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800
    )

def init_database():
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(current_dir, 'face_recognition.db')
        
        # Veritabanı dizininin varlığını kontrol et
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Veritabanı bağlantısını test et
        engine = get_database_engine(db_path)
        try:
            engine.connect()
        except Exception as e:
            raise RuntimeError(f"Veritabanı bağlantısı başarısız: {str(e)}")
        
        # Tabloları oluştur
        Base.metadata.create_all(engine)
        
        # Session oluştur
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Session'ı test et
        try:
            session.execute("SELECT 1")
            session.commit()
        except Exception as e:
            session.close()
            raise RuntimeError(f"Veritabanı session testi başarısız: {str(e)}")
        
        return session
    except Exception as e:
        raise RuntimeError(f"Veritabanı başlatılırken hata: {str(e)}")