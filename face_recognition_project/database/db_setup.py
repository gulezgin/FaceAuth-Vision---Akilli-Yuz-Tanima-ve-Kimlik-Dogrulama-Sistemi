from models import Base
from sqlalchemy import create_engine
import os

# Veritabanı dosyasının tam yolu
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, '..', 'face_recognition.db')
DATABASE_URL = f"sqlite:///{db_path}"

# Veritabanı bağlantısı
engine = create_engine(DATABASE_URL)

def init_db():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
    print("Veritabanı başarıyla oluşturuldu!")