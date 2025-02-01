from fastapi import FastAPI, HTTPException, Depends, Security, File, UploadFile
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from services.face_recognition_service import FaceRecognitionService
from database.models import Person, init_database
from config.settings import Config
import logging
import base64
import io
from PIL import Image

app = FastAPI(title="Yüz Tanıma API", version="1.0.0")
logger = logging.getLogger(__name__)

# API güvenlik başlığı
api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != Config.get_api_key():
        logger.warning(f"Geçersiz API anahtarı denemesi")
        raise HTTPException(
            status_code=403,
            detail="Geçersiz API anahtarı"
        )
    return api_key_header

def get_service():
    db = init_database()
    try:
        service = FaceRecognitionService(db)
        yield service
    finally:
        db.close()

class RecognitionRequest(BaseModel):
    image: str  # base64 encoded image
    threshold: float = 0.6

class PersonCreate(BaseModel):
    name: str
    image: str  # base64 encoded image

class PersonUpdate(BaseModel):
    name: Optional[str] = None
    image: Optional[str] = None

class RecognitionResponse(BaseModel):
    status: str
    results: List[dict]
    timestamp: datetime

@app.post("/api/v1/recognize", response_model=RecognitionResponse)
async def recognize_face(
    request: RecognitionRequest,
    service: FaceRecognitionService = Depends(get_service),
    api_key: str = Depends(get_api_key)
):
    try:
        # Base64 görüntüyü decode et
        image_data = base64.b64decode(request.image)
        image = Image.open(io.BytesIO(image_data))
        
        # Görüntüyü işle
        results = service.process_image(
            image,
            threshold=request.threshold
        )
        
        return {
            "status": "success",
            "results": results,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Yüz tanıma hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/persons")
async def add_person(
    person: PersonCreate,
    service: FaceRecognitionService = Depends(get_service),
    api_key: str = Depends(get_api_key)
):
    try:
        # Base64 görüntüyü decode et
        image_data = base64.b64decode(person.image)
        image = Image.open(io.BytesIO(image_data))
        
        # Geçici dosya oluştur
        temp_path = f"temp_{datetime.now().timestamp()}.jpg"
        image.save(temp_path)
        
        # Kişiyi ekle
        service.add_person(temp_path, person.name)
        
        # Geçici dosyayı sil
        import os
        os.remove(temp_path)
        
        return {"status": "success", "message": f"{person.name} başarıyla eklendi"}
    except Exception as e:
        logger.error(f"Kişi ekleme hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/persons/{person_id}")
async def update_person(
    person_id: int,
    person: PersonUpdate,
    service: FaceRecognitionService = Depends(get_service),
    api_key: str = Depends(get_api_key)
):
    try:
        temp_path = None
        if person.image:
            # Base64 görüntüyü decode et
            image_data = base64.b64decode(person.image)
            image = Image.open(io.BytesIO(image_data))
            
            # Geçici dosya oluştur
            temp_path = f"temp_{datetime.now().timestamp()}.jpg"
            image.save(temp_path)
        
        # Kişiyi güncelle
        service.update_person(person_id, person.name, temp_path)
        
        # Geçici dosyayı sil
        if temp_path:
            import os
            os.remove(temp_path)
        
        return {"status": "success", "message": "Kişi başarıyla güncellendi"}
    except Exception as e:
        logger.error(f"Kişi güncelleme hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/persons/{person_id}")
async def delete_person(
    person_id: int,
    service: FaceRecognitionService = Depends(get_service),
    api_key: str = Depends(get_api_key)
):
    try:
        service.delete_person(person_id)
        return {"status": "success", "message": "Kişi başarıyla silindi"}
    except Exception as e:
        logger.error(f"Kişi silme hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))