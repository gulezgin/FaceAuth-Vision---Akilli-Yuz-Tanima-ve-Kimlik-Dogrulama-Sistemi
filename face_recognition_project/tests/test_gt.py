import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel


def test_qt():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setGeometry(100, 100, 300, 200)
    window.setWindowTitle('Qt Test')

    label = QLabel('Qt çalışıyor!', window)
    label.move(100, 80)

    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    test_qt()