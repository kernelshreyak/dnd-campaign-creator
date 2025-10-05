import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maximized PyQt Wayland Window")

        # Your application's main widget
        label = QLabel("This window should start maximized on Wayland.")
        self.setCentralWidget(label)

        # Maximize the window
        self.showMaximized()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())