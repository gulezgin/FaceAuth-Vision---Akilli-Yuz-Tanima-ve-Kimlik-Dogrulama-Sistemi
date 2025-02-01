import sys
import os
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from config.settings import Config
from database.models import Base
from sqlalchemy import create_engine
import dlib
import logging

# Logging ayarları
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def check_and_download_models():
    try:
        # Önce models klasörünü oluştur
        models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
        os.makedirs(models_dir, exist_ok=True)

        # Model dosyasının varlığını kontrol et
        model_file = os.path.join(models_dir, 'shape_predictor_68_face_landmarks.dat')
        if not os.path.exists(model_file):
            import download_models
            download_models.main()
            if not os.path.exists(model_file):
                raise RuntimeError("Model dosyası indirilemedi!")
            
        logger.info("Model dosyaları başarıyla kontrol edildi/indirildi")
    except Exception as e:
        logger.error(f"Model indirme hatası: {str(e)}")
        raise

def setup_qt_plugins():
    try:
        # Qt plugin yolu
        qt_plugin_path = os.path.join(os.path.dirname(os.path.dirname(sys.executable)),
                                    'Lib', 'site-packages', 'PyQt5', 'Qt5', 'plugins')

        if os.path.exists(qt_plugin_path):
            os.environ['QT_PLUGIN_PATH'] = qt_plugin_path
            logger.info(f"Qt Plugin Yolu: {qt_plugin_path}")

            # Platform plugin'inin varlığını kontrol et
            platform_plugin = os.path.join(qt_plugin_path, 'platforms')
            if os.path.exists(platform_plugin):
                logger.info(f"Platform eklentileri mevcut: {os.listdir(platform_plugin)}")
            else:
                logger.warning("Platform eklentileri dizini bulunamadı!")
        else:
            logger.warning(f"Qt Plugin dizini bulunamadı: {qt_plugin_path}")
    except Exception as e:
        logger.error(f"Qt plugin ayarlanırken hata: {str(e)}")

def main():
    try:
        # Model dosyalarını kontrol et ve indir
        check_and_download_models()

        # Qt plugin yolunu ayarla
        setup_qt_plugins()

        # Veritabanı bağlantısı
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, 'face_recognition.db')
        
        # Veritabanı dizininin varlığını kontrol et
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
        logger.info("Veritabanı bağlantısı başarılı")

        # GUI başlat
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        logger.info("GUI başlatıldı")

        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Kritik hata: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"\n❌ KRİTİK HATA: {e}")
        logger.info("\n🛠️ ÇÖZÜM ADIMLARI:")
        logger.info("1. Model dosyasını indir: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
        logger.info("2. İndirdiğin dosyayı aç ve:")
        logger.info(f"   a) Ya şuraya kopyala: {os.path.dirname(dlib.__file__)}")
        logger.info(f"   b) Veya proje kökünde 'models' klasörü oluşturup içine yerleştir")
        logger.info("3. Programı yeniden başlat")
        sys.exit(1)