import logging
import yaml
import os
import secrets
from typing import Optional

logger = logging.getLogger(__name__)

class Config:
    # API Güvenlik
    API_KEY: str = os.getenv('FACE_RECOGNITION_API_KEY', secrets.token_urlsafe(32))
    
    # Veritabanı
    DATABASE_URL: str = os.getenv('FACE_RECOGNITION_DB_URL', 'sqlite:///face_recognition.db')
    
    # Model Ayarları
    FACE_DETECTION_MODEL: str = os.getenv('FACE_DETECTION_MODEL', 'hog')  # 'hog' veya 'cnn'
    FACE_RECOGNITION_TOLERANCE: float = float(os.getenv('FACE_RECOGNITION_TOLERANCE', '0.6'))
    
    # Kamera Ayarları
    CAMERA_INDEX: int = int(os.getenv('CAMERA_INDEX', '0'))
    FRAME_INTERVAL: float = float(os.getenv('FRAME_INTERVAL', '0.5'))  # saniye
    
    # Dosya Yolu Ayarları
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODELS_DIR: str = os.path.join(BASE_DIR, 'models')
    KNOWN_FACES_DIR: str = os.path.join(BASE_DIR, 'known_faces')
    
    # Log Ayarları
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.path.join(BASE_DIR, 'app.log')
    
    def __init__(self):
        self.load_config()
        self.setup_logging()

    def load_config(self):
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'config',
                'config.yaml'
            )

            # Varsayılan ayarlar
            self.default_settings = {
                'database': {
                    'path': 'face_recognition.db'
                },
                'camera': {
                    'device_id': 0,
                    'frame_width': 640,
                    'frame_height': 480,
                    'fps': 30
                },
                'face_recognition': {
                    'tolerance': 0.6,
                    'model_path': os.path.join('models', 'shape_predictor_68_face_landmarks.dat')
                },
                'logging': {
                    'level': 'INFO',
                    'file': 'app.log'
                },
                'gui': {
                    'window_title': 'Yüz Tanıma Sistemi',
                    'window_width': 1200,
                    'window_height': 800,
                    'theme': 'light'
                }
            }

            # Config dosyası varsa oku
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_settings = yaml.safe_load(f)
                    
                # Kullanıcı ayarlarını varsayılan ayarlarla birleştir
                self._merge_settings(user_settings)
                logger.info("Yapılandırma dosyası yüklendi")
            else:
                # Varsayılan ayarları kaydet
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(self.default_settings, f, allow_unicode=True)
                logger.info("Varsayılan yapılandırma dosyası oluşturuldu")

            # Ayarları sınıf özelliklerine dönüştür
            for key, value in self.default_settings.items():
                setattr(self, key, value)

        except Exception as e:
            logger.error(f"Yapılandırma yüklenirken hata: {str(e)}")
            # Hata durumunda varsayılan ayarları kullan
            for key, value in self.default_settings.items():
                setattr(self, key, value)

    def _merge_settings(self, user_settings):
        """Kullanıcı ayarlarını varsayılan ayarlarla birleştirir."""
        def merge_dict(default, user):
            for key, value in user.items():
                if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                    merge_dict(default[key], value)
                else:
                    default[key] = value

        merge_dict(self.default_settings, user_settings)

    def save_config(self):
        """Mevcut ayarları config dosyasına kaydeder."""
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'config',
                'config.yaml'
            )

            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.default_settings, f, allow_unicode=True)
            
            logger.info("Yapılandırma dosyası kaydedildi")
            return True
        except Exception as e:
            logger.error(f"Yapılandırma kaydedilirken hata: {str(e)}")
            return False

    def update_setting(self, section, key, value):
        """Belirli bir ayarı günceller ve kaydeder."""
        try:
            if section in self.default_settings and key in self.default_settings[section]:
                self.default_settings[section][key] = value
                setattr(self, section, self.default_settings[section])
                return self.save_config()
            return False
        except Exception as e:
            logger.error(f"Ayar güncellenirken hata: {str(e)}")
            return False

    def setup_logging(self):
        logging.basicConfig(
            level=getattr(logging, self.default_settings['logging']['level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.default_settings['logging']['file']),
                logging.StreamHandler()
            ]
        )

    @classmethod
    def get_api_key(cls) -> str:
        """API anahtarını döndür veya yeni oluştur"""
        if not hasattr(cls, '_api_key'):
            cls._api_key = cls.API_KEY
        return cls._api_key
    
    @classmethod
    def setup_directories(cls):
        """Gerekli dizinleri oluştur"""
        os.makedirs(cls.MODELS_DIR, exist_ok=True)
        os.makedirs(cls.KNOWN_FACES_DIR, exist_ok=True)
    
    @classmethod
    def get_model_path(cls, model_name: str) -> Optional[str]:
        """Model dosyasının tam yolunu döndür"""
        model_path = os.path.join(cls.MODELS_DIR, model_name)
        return model_path if os.path.exists(model_path) else None