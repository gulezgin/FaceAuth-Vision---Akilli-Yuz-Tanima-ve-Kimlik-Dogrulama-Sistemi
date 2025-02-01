from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import logging

logger = logging.getLogger(__name__)

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Ana layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Üst panel - İstatistikler
        stats_panel = QHBoxLayout()
        layout.addLayout(stats_panel)

        # İstatistik kartları
        self.add_stat_card(stats_panel, "Toplam Kişi", "0")
        self.add_stat_card(stats_panel, "Bugün Tanınan", "0")
        self.add_stat_card(stats_panel, "Başarı Oranı", "0%")

        # Orta panel - Kamera görüntüsü
        camera_panel = QVBoxLayout()
        layout.addLayout(camera_panel)

        # Kamera başlığı
        camera_title = QLabel("Canlı Kamera Görüntüsü")
        camera_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                margin: 10px 0;
            }
        """)
        camera_panel.addWidget(camera_title)

        # Kamera görüntüsü için label
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #ddd;
                border: 2px solid #ccc;
                border-radius: 5px;
            }
        """)
        camera_panel.addWidget(self.camera_label)

        # Alt panel - Son aktiviteler
        activity_panel = QVBoxLayout()
        layout.addLayout(activity_panel)

        # Aktivite başlığı
        activity_title = QLabel("Son Aktiviteler")
        activity_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                margin: 10px 0;
            }
        """)
        activity_panel.addWidget(activity_title)

        # Aktivite listesi
        self.activity_list = QListWidget()
        self.activity_list.setMaximumHeight(150)
        self.activity_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        activity_panel.addWidget(self.activity_list)

    def add_stat_card(self, layout, title, value):
        try:
            # Kart container
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 10px;
                    margin: 5px;
                }
            """)
            card_layout = QVBoxLayout()
            card.setLayout(card_layout)

            # Başlık
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #666;
                }
            """)
            card_layout.addWidget(title_label)

            # Değer
            value_label = QLabel(value)
            value_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #333;
                }
            """)
            card_layout.addWidget(value_label)

            # Kartı layout'a ekle
            layout.addWidget(card)
            
            logger.debug(f"İstatistik kartı eklendi: {title}")
        except Exception as e:
            logger.error(f"İstatistik kartı eklenirken hata: {str(e)}")

    def update_stats(self, total_persons, today_recognized, success_rate):
        try:
            # İstatistikleri güncelle
            stats = self.findChildren(QFrame)
            if len(stats) >= 3:
                stats[0].findChild(QLabel, "", Qt.FindChildOption.FindChildrenRecursively).setText(str(total_persons))
                stats[1].findChild(QLabel, "", Qt.FindChildOption.FindChildrenRecursively).setText(str(today_recognized))
                stats[2].findChild(QLabel, "", Qt.FindChildOption.FindChildrenRecursively).setText(f"{success_rate}%")
            
            logger.debug("İstatistikler güncellendi")
        except Exception as e:
            logger.error(f"İstatistikler güncellenirken hata: {str(e)}")

    def add_activity(self, message):
        try:
            # Yeni aktivite ekle
            item = QListWidgetItem(message)
            self.activity_list.insertItem(0, item)  # En üste ekle
            
            # Maksimum 100 aktivite göster
            if self.activity_list.count() > 100:
                self.activity_list.takeItem(self.activity_list.count() - 1)
            
            logger.debug(f"Yeni aktivite eklendi: {message}")
        except Exception as e:
            logger.error(f"Aktivite eklenirken hata: {str(e)}")

    def clear_activities(self):
        try:
            self.activity_list.clear()
            logger.debug("Aktivite listesi temizlendi")
        except Exception as e:
            logger.error(f"Aktivite listesi temizlenirken hata: {str(e)}")

    def add_chart_area(self, layout):
        chart_group = QGroupBox("Günlük İstatistikler")
        chart_layout = QVBoxLayout(chart_group)

        # Matplotlib figürü oluştur
        figure = plt.figure(figsize=(8, 4))
        canvas = FigureCanvas(figure)

        # Örnek grafik
        ax = figure.add_subplot(111)
        ax.plot([1, 2, 3, 4], [1, 4, 2, 3])

        chart_layout.addWidget(canvas)
        layout.addWidget(chart_group)

    def add_camera_feed(self, layout):
        camera_group = QGroupBox("Canlı Kamera")
        camera_layout = QVBoxLayout(camera_group)

        # Kamera görüntüsü için label
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 2px solid #ddd;
                border-radius: 4px;
            }
        """)

        # Başlangıç metni
        self.camera_label.setText("Kamera başlatılıyor...")

        camera_layout.addWidget(self.camera_label)
        layout.addWidget(camera_group)