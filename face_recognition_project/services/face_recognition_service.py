import face_recognition
import cv2
import numpy as np
from database.models import Person, FaceRecognitionLog
from sqlalchemy.orm import Session
import os
import logging
from datetime import datetime
import dlib
import time
from typing import Dict, List, Tuple


class FaceRecognitionService:
    def __init__(self, db_session: Session):
        try:
            self.logger = logging.getLogger(__name__)
            self.model_path = self.check_models()
            self.db = db_session
            self.known_face_encodings = []
            self.known_face_names = []
            self._last_process_time = 0
            self._frame_interval = 0.5  # Her 500ms'de bir işle
            self._face_locations_cache = {}  # Son tespit edilen yüz konumları
            self._face_encodings_cache = {}  # Son tespit edilen yüz kodlamaları
            
            # Kamera ve model kontrolü
            if not cv2.getBuildInformation():
                raise RuntimeError("OpenCV kurulumu eksik veya hatalı")
                
            # Face recognition kontrolü
            if not face_recognition.face_locations:
                raise RuntimeError("Face recognition kütüphanesi düzgün yüklenmemiş")
                
            self.load_known_faces()
            self.logger.info("FaceRecognitionService başarıyla başlatıldı")
        except Exception as e:
            self.logger.error(f"Servis başlatılırken hata: {str(e)}")
            raise

    def check_models(self) -> str:
        try:
            # Dlib model kontrolü
            dlib_predictor_path = os.path.join(
                os.path.dirname(dlib.__file__),
                "shape_predictor_68_face_landmarks.dat"
            )
            
            # Alternatif konum kontrolü
            local_model_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'models',
                'shape_predictor_68_face_landmarks.dat'
            )
            
            if not os.path.exists(dlib_predictor_path) and not os.path.exists(local_model_path):
                raise RuntimeError(
                    f"Model dosyası bulunamadı! Lütfen dosyayı şu konumlardan birine yerleştirin:\n"
                    f"1. {dlib_predictor_path}\n"
                    f"2. {local_model_path}"
                )
            
            return local_model_path if os.path.exists(local_model_path) else dlib_predictor_path
        
        except Exception as e:
            self.logger.error(f"Model kontrol hatası: {str(e)}")
            raise

    def load_known_faces(self):
        try:
            persons = self.db.query(Person).filter(Person.is_active == True).all()
            self.known_face_encodings = []
            self.known_face_names = []
            
            for person in persons:
                face_encoding = np.frombuffer(person.face_encoding)
                self.known_face_encodings.append(face_encoding)
                self.known_face_names.append(person.name)
                
            self.logger.info(f"{len(persons)} kişi yüklendi")
        except Exception as e:
            self.logger.error(f"Kayıtlı yüzler yüklenirken hata: {str(e)}")
            raise

    def start_camera(self) -> bool:
        try:
            self.video_capture = cv2.VideoCapture(0)
            if not self.video_capture.isOpened():
                self.logger.error("Kamera başlatılamadı")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Kamera başlatılırken hata: {str(e)}")
            return False

    def stop_camera(self):
        try:
            if hasattr(self, 'video_capture'):
                self.video_capture.release()
                self.logger.info("Kamera kapatıldı")
        except Exception as e:
            self.logger.error(f"Kamera kapatılırken hata: {str(e)}")

    def should_process_frame(self) -> bool:
        current_time = time.time()
        if current_time - self._last_process_time > self._frame_interval:
            self._last_process_time = current_time
            return True
        return False

    def get_frame(self):
        try:
            if not hasattr(self, 'video_capture'):
                return None

            ret, frame = self.video_capture.read()
            if not ret or frame is None or frame.size == 0:
                return None

            # Her frame'i işleme
            if self.should_process_frame():
                # Yüz tanıma işlemi
                face_locations = face_recognition.face_locations(frame)
                face_encodings = face_recognition.face_encodings(frame, face_locations)
                
                # Önbelleğe al
                self._face_locations_cache = face_locations
                self._face_encodings_cache = face_encodings
            else:
                # Önbellekten al
                face_locations = self._face_locations_cache
                face_encodings = self._face_encodings_cache

            # Tanınan yüzleri işaretle
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(
                    self.known_face_encodings,
                    face_encoding,
                    tolerance=0.6
                )
                name = "Bilinmeyen"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]

                    # Log kaydı
                    confidence_score = face_recognition.face_distance(
                        [self.known_face_encodings[first_match_index]],
                        face_encoding
                    )[0]
                    
                    if confidence_score < 0.6:  # Sadece güven skoru yüksek olanları logla
                        self.log_recognition(name, confidence_score)

                # Yüzü çerçevele
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    name,
                    (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75,
                    (0, 255, 0),
                    2
                )

            return frame

        except Exception as e:
            self.logger.error(f"Kare işlenirken hata: {str(e)}")
            return None

    def log_recognition(self, person_name: str, confidence_score: float):
        try:
            person = self.db.query(Person).filter(Person.name == person_name).first()
            if person:
                log = FaceRecognitionLog(
                    person_id=person.id,
                    confidence_score=confidence_score,
                    timestamp=datetime.now()
                )
                self.db.add(log)
                self.db.commit()
                self.logger.debug(f"Tanıma logu kaydedildi: {person_name} ({confidence_score:.2f})")
        except Exception as e:
            self.logger.error(f"Tanıma logu kaydedilirken hata: {str(e)}")
            self.db.rollback()

    def add_person(self, image_path: str, name: str):
        try:
            # Fotoğraftaki yüzü bul ve kodla
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)

            if not face_encodings:
                raise ValueError("Fotoğrafta yüz bulunamadı")

            face_encoding = face_encodings[0]

            # Veritabanına kaydet
            person = Person(
                name=name,
                face_encoding=face_encoding.tobytes(),
                created_at=datetime.now()
            )

            self.db.add(person)
            self.db.commit()

            # Yüklü yüzleri güncelle
            self.load_known_faces()
            
            self.logger.info(f"{name} isimli kişi başarıyla eklendi")
            
        except Exception as e:
            self.logger.error(f"Kişi eklenirken hata: {str(e)}")
            self.db.rollback()
            raise

    def update_person(self, person_id: int, new_name: str = None, new_image_path: str = None):
        try:
            person = self.db.query(Person).filter(Person.id == person_id).first()
            if not person:
                raise ValueError(f"ID {person_id} olan kişi bulunamadı")

            if new_name:
                person.name = new_name

            if new_image_path:
                image = face_recognition.load_image_file(new_image_path)
                face_encodings = face_recognition.face_encodings(image)
                
                if not face_encodings:
                    raise ValueError("Yeni fotoğrafta yüz bulunamadı")
                
                person.face_encoding = face_encodings[0].tobytes()

            person.updated_at = datetime.now()
            self.db.commit()
            
            # Yüklü yüzleri güncelle
            self.load_known_faces()
            
            self.logger.info(f"Kişi güncellendi: {person.name}")
            
        except Exception as e:
            self.logger.error(f"Kişi güncellenirken hata: {str(e)}")
            self.db.rollback()
            raise

    def delete_person(self, person_id: int):
        try:
            person = self.db.query(Person).filter(Person.id == person_id).first()
            if not person:
                raise ValueError(f"ID {person_id} olan kişi bulunamadı")

            person.is_active = False
            person.updated_at = datetime.now()
            self.db.commit()
            
            # Yüklü yüzleri güncelle
            self.load_known_faces()
            
            self.logger.info(f"Kişi silindi: {person.name}")
            
        except Exception as e:
            self.logger.error(f"Kişi silinirken hata: {str(e)}")
            self.db.rollback()
            raise

    def generate_report(self, file_path):
        try:
            # Basit bir rapor oluştur
            if file_path.endswith('.pdf'):
                self.generate_pdf_report(file_path)
            elif file_path.endswith('.csv'):
                self.generate_csv_report(file_path)
            else:
                raise ValueError("Desteklenmeyen dosya formatı")
        except Exception as e:
            self.logger.error(f"Rapor oluşturulurken hata: {str(e)}")
            raise

    def generate_pdf_report(self, file_path):
        # PDF rapor oluşturma işlemleri
        pass

    def generate_csv_report(self, file_path):
        # CSV rapor oluşturma işlemleri
        pass

