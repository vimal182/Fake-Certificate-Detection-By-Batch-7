import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout,
    QApplication, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap

from ai.model_loader import detect_hardware, load_model


class SplashScreen(QWidget):

    def __init__(self):
        super().__init__()

        #  Window settings
        self.setFixedSize(480, 400)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color:black;")

        self.progress_value = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # IMAGE 
        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_dir, "images", "splash.png")

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        pixmap = QPixmap(image_path)

        scaled_pixmap = pixmap.scaled(
            480, 400,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)

        #  STATUS 
        self.status_label = QLabel("Detecting hardware...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "color:white;font-size:14px;font-weight:bold;"
        )

        self.spec_label = QLabel("")
        self.spec_label.setAlignment(Qt.AlignCenter)
        self.spec_label.setStyleSheet(
            "color:white;font-size:12px;"
        )

        #  PROGRESS BAR 
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(True)

        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #222;
                border: none;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #00E5FF;
            }
        """)

        #  LAYOUT 
        layout.addStretch()
        layout.addWidget(self.image_label)
        layout.addSpacing(10)
        layout.addWidget(self.status_label)
        layout.addWidget(self.spec_label)
        layout.addSpacing(15)
        layout.addWidget(self.progress)
        layout.addStretch()

        #  TIMER 
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(80)

    #  PROGRESS FLOW 

    def update_progress(self):

        self.progress_value += 1
        self.progress.setValue(self.progress_value)

        if self.progress_value == 10:
            self.status_label.setText("Detecting hardware...")
            device, name, ram = detect_hardware()
            self.device = device
            self.device_name = name
            self.ram = ram

        if self.progress_value == 30:
            if self.device == "GPU":
                self.status_label.setText("Switching to GPU...")
            else:
                self.status_label.setText("Switching to CPU...")

        if self.progress_value == 50:
            if self.device == "GPU":
                self.spec_label.setText(
                    f"Using GPU: {self.device_name} | RAM: {self.ram} GB"
                )
            else:
                self.spec_label.setText(
                    f"Using CPU: {self.device_name} | RAM: {self.ram} GB"
                )

        if self.progress_value == 70:
            self.status_label.setText("Loading AI Model...")
            load_model()

        if self.progress_value >= 100:
            self.timer.stop()
            self.launch_home()

    # OPEN HOME WINDOW 

    def launch_home(self):

        # Import from home.py
        from home import HomeWindow   

        self.main = HomeWindow()
        self.main.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    sys.exit(app.exec_())