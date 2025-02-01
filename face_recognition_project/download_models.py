import os
import requests
import bz2
import logging
import shutil

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def download_file(url, local_path):
    try:
        logger.info(f"İndiriliyor: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        downloaded = 0
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    percentage = int((downloaded / total_size) * 100)
                    print(f"\rİndirme ilerlemesi: {percentage}%", end='')
        
        print()  # Yeni satır
        logger.info(f"İndirme tamamlandı: {local_path}")
        return True
    except Exception as e:
        logger.error(f"İndirme hatası: {str(e)}")
        return False

def extract_bz2(bz2_path, output_path):
    try:
        logger.info(f"Çıkartılıyor: {bz2_path}")
        with bz2.open(bz2_path, 'rb') as source, open(output_path, 'wb') as dest:
            shutil.copyfileobj(source, dest)
        logger.info(f"Çıkartma tamamlandı: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Çıkartma hatası: {str(e)}")
        return False

def main():
    try:
        # Model URL'leri
        models = {
            'shape_predictor_68_face_landmarks.dat': 'http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2'
        }

        # Models dizinini oluştur
        models_dir = 'models'
        os.makedirs(models_dir, exist_ok=True)

        for model_name, url in models.items():
            logger.info(f"\n{model_name} indiriliyor...")
            
            # İndirme yolları
            bz2_path = os.path.join(models_dir, f"{model_name}.bz2")
            model_path = os.path.join(models_dir, model_name)

            # Model zaten varsa atla
            if os.path.exists(model_path):
                logger.info(f"{model_name} zaten mevcut, atlanıyor...")
                continue

            # Modeli indir
            if not download_file(url, bz2_path):
                continue

            # BZ2 dosyasını çıkart
            if not extract_bz2(bz2_path, model_path):
                continue

            # BZ2 dosyasını sil
            try:
                os.remove(bz2_path)
                logger.info(f"Geçici dosya silindi: {bz2_path}")
            except Exception as e:
                logger.warning(f"Geçici dosya silinirken hata: {str(e)}")

        logger.info("\nTüm modeller başarıyla indirildi!")

    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}")
        raise

if __name__ == "__main__":
    main()