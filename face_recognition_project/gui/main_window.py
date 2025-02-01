from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .dashboard import Dashboard
from services.face_recognition_service import FaceRecognitionService
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import cv2
import os
import logging

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_services()
        self.setup_connections()

    def init_ui(self):
        self.setWindowTitle("Yüz Tanıma Sistemi")
        self.setGeometry(100, 100, 1200, 800)

        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Toolbar oluştur
        self.create_toolbar()

        # Dashboard'u ekle
        self.dashboard = Dashboard()
        layout.addWidget(self.dashboard)

        # Menü çubuğu
        self.create_menu_bar()

        # Stil ayarları
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QMenuBar {
                background-color: white;
                border-bottom: 1px solid #ddd;
            }
            QToolBar {
                background-color: white;
                border-bottom: 1px solid #ddd;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                color: #333;
            }
        """)

    def setup_connections(self):
        # Menü aksiyonlarını bağla
        self.import_action.triggered.connect(self.import_images)
        self.export_action.triggered.connect(self.export_reports)
        self.exit_action.triggered.connect(self.close)
        self.about_action.triggered.connect(self.show_about)

        # Toolbar aksiyonlarını bağla
        self.add_person_action.triggered.connect(self.add_person)
        self.report_action.triggered.connect(self.generate_report)

    def create_menu_bar(self):
        menubar = self.menuBar()

        # Dosya menüsü
        file_menu = menubar.addMenu('Dosya')
        self.import_action = QAction('Fotoğraf İçe Aktar', self)
        self.export_action = QAction('Rapor Dışa Aktar', self)
        self.exit_action = QAction('Çıkış', self)

        file_menu.addAction(self.import_action)
        file_menu.addAction(self.export_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # Ayarlar menüsü
        settings_menu = menubar.addMenu('Ayarlar')
        settings_menu.addAction('Tanıma Ayarları')
        settings_menu.addAction('Kamera Ayarları')

        # Yardım menüsü
        help_menu = menubar.addMenu('Yardım')
        self.about_action = QAction('Hakkında', self)
        help_menu.addAction(self.about_action)

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Kamera başlat/durdur butonu
        self.camera_action = QAction('Kamerayı Başlat', self)
        self.camera_action.setCheckable(True)
        self.camera_action.triggered.connect(self.toggle_camera)
        toolbar.addAction(self.camera_action)

        toolbar.addSeparator()

        # Kişi ekle butonu
        self.add_person_action = QAction('Kişi Ekle', self)
        toolbar.addAction(self.add_person_action)

        # Rapor oluştur butonu
        self.report_action = QAction('Rapor Oluştur', self)
        toolbar.addAction(self.report_action)

    def setup_services(self):
        try:
            # Veritabanı bağlantısı
            engine = create_engine('sqlite:///face_recognition.db')
            self.db_session = Session(engine)

            # Yüz tanıma servisi
            self.face_service = FaceRecognitionService(self.db_session)

            # Kamera timer'ı
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_frame)
            
            logger.info("Servisler başarıyla başlatıldı")
        except Exception as e:
            logger.error(f"Servisler başlatılırken hata: {str(e)}")
            raise

    def toggle_camera(self, checked):
        try:
            if checked:
                if self.face_service.start_camera():
                    self.camera_action.setText('Kamerayı Durdur')
                    self.timer.start(30)  # 30ms = ~33 fps
                    self.dashboard.camera_label.setText("Kamera aktif...")
                    logger.info("Kamera başlatıldı")
            else:
                self.face_service.stop_camera()
                self.camera_action.setText('Kamerayı Başlat')
                self.timer.stop()
                self.dashboard.camera_label.setText("Kamera durduruldu")
                logger.info("Kamera durduruldu")
        except Exception as e:
            logger.error(f"Kamera işlemi sırasında hata: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Kamera işlemi başarısız: {str(e)}")

    def update_frame(self):
        try:
            frame = self.face_service.get_frame()
            if frame is not None:
                # OpenCV BGR -> RGB dönüşümü
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w

                # QImage oluştur
                image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

                # Dashboard'daki kamera label'ını güncelle
                self.dashboard.camera_label.setPixmap(
                    QPixmap.fromImage(image).scaled(
                        self.dashboard.camera_label.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )
        except Exception as e:
            logger.error(f"Kare güncellenirken hata: {str(e)}")

    def import_images(self):
        try:
            file_dialog = QFileDialog()
            file_names, _ = file_dialog.getOpenFileNames(
                self,
                "Fotoğraf İçe Aktar",
                "",
                "Resim Dosyaları (*.jpg *.jpeg *.png)"
            )

            if file_names:
                for file_name in file_names:
                    # Kişi bilgileri için dialog göster
                    name, ok = QInputDialog.getText(
                        self, 'Kişi Ekle', 'Kişi adını girin:'
                    )
                    if ok and name:
                        try:
                            # Fotoğrafı known_faces klasörüne kopyala
                            dest_path = os.path.join('known_faces', f"{name}.jpg")
                            os.makedirs('known_faces', exist_ok=True)

                            # Yüz tanıma servisini güncelle
                            self.face_service.add_person(file_name, name)

                            QMessageBox.information(
                                self,
                                "Başarılı",
                                f"{name} isimli kişi başarıyla eklendi!"
                            )
                            logger.info(f"{name} isimli kişi başarıyla eklendi")
                        except Exception as e:
                            error_msg = f"Kişi eklenirken hata: {str(e)}"
                            logger.error(error_msg)
                            QMessageBox.critical(self, "Hata", error_msg)
        except Exception as e:
            logger.error(f"Fotoğraf içe aktarılırken hata: {str(e)}")

    def export_reports(self):
        try:
            file_dialog = QFileDialog()
            file_name, _ = file_dialog.getSaveFileName(
                self,
                "Rapor Dışa Aktar",
                "",
                "PDF Dosyaları (*.pdf);;CSV Dosyaları (*.csv)"
            )

            if file_name:
                try:
                    # Rapor oluştur
                    self.face_service.generate_report(file_name)
                    QMessageBox.information(
                        self,
                        "Başarılı",
                        "Rapor başarıyla dışa aktarıldı!"
                    )
                    logger.info(f"Rapor başarıyla oluşturuldu: {file_name}")
                except Exception as e:
                    error_msg = f"Rapor oluşturulurken hata: {str(e)}"
                    logger.error(error_msg)
                    QMessageBox.critical(self, "Hata", error_msg)
        except Exception as e:
            logger.error(f"Rapor dışa aktarılırken hata: {str(e)}")

    def add_person(self):
        try:
            # Kamera görüntüsünden kişi ekle
            if hasattr(self, 'face_service') and self.face_service.video_capture is not None:
                ret, frame = self.face_service.video_capture.read()
                if ret:
                    name, ok = QInputDialog.getText(
                        self, 'Kişi Ekle', 'Kişi adını girin:'
                    )
                    if ok and name:
                        try:
                            # Fotoğrafı kaydet ve kişiyi ekle
                            image_path = os.path.join('known_faces', f"{name}.jpg")
                            cv2.imwrite(image_path, frame)
                            self.face_service.add_person(image_path, name)

                            QMessageBox.information(
                                self,
                                "Başarılı",
                                f"{name} isimli kişi başarıyla eklendi!"
                            )
                            logger.info(f"{name} isimli kişi kameradan başarıyla eklendi")
                        except Exception as e:
                            error_msg = f"Kişi eklenirken hata: {str(e)}"
                            logger.error(error_msg)
                            QMessageBox.critical(self, "Hata", error_msg)
        except Exception as e:
            logger.error(f"Kameradan kişi eklenirken hata: {str(e)}")

    def generate_report(self):
        self.export_reports()

    def show_about(self):
        QMessageBox.about(
            self,
            "Hakkında",
            "Yüz Tanıma Sistemi\nSürüm 1.0\n\nGeliştirici: Yüz Tanıma Ekibi"
        )