import unittest
from services.face_recognition_service import FaceRecognitionService
from database.models import Person
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


class TestFaceRecognition(unittest.TestCase):
    def setUp(self):
        # Test veritabanı bağlantısı
        self.engine = create_engine('sqlite:///:memory:')
        self.session = Session(self.engine)
        self.service = FaceRecognitionService(self.session)

    def test_camera_start(self):
        result = self.service.start_camera()
        self.assertTrue(result)
        self.service.stop_camera()

    def tearDown(self):
        self.session.close()