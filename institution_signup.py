import sys
import os
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "institution.db")


class InstitutionSignup(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Institution Signup")
        self.setFixedSize(900, 550)
        self.init_ui()

    def init_ui(self):
        root = QWidget()
        root.setStyleSheet("background-color: #F9F9F9;")
        self.setCentralWidget(root)

        layout = QHBoxLayout(root)
        layout.addStretch()

        card = QWidget()
        card.setFixedSize(380, 380)
        card.setStyleSheet(
            "background-color: #FFFFFF;"
            "border-radius: 16px;"
            "border: 1px solid #E5E5E5;"
        )

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setYOffset(12)
        shadow.setColor(QColor(0, 0, 0, 60))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 35, 35, 35)
        card_layout.setSpacing(18)

        title = QLabel("Institution Signup")
        title.setFont(QFont("Segoe UI", 17, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setFixedHeight(42)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFixedHeight(42)

        self.username.setStyleSheet("border:1px solid #DADADA;border-radius:10px;padding-left:12px;")
        self.password.setStyleSheet("border:1px solid #DADADA;border-radius:10px;padding-left:12px;")

        signup_btn = QPushButton("Create Account")
        signup_btn.setFixedHeight(44)
        signup_btn.setStyleSheet("background-color:#007AFF;color:white;border-radius:10px;")
        signup_btn.clicked.connect(self.signup)

        back = QLabel("← Back to Login")
        back.setAlignment(Qt.AlignCenter)
        back.setCursor(Qt.PointingHandCursor)
        back.setStyleSheet("color:#007AFF;font-size:13px;")
        back.mousePressEvent = self.go_back

        card_layout.addWidget(title)
        card_layout.addWidget(self.username)
        card_layout.addWidget(self.password)
        card_layout.addWidget(signup_btn)
        card_layout.addWidget(back)

        layout.addWidget(card)
        layout.addStretch()

    def signup(self):
        if not self.username.text() or not self.password.text():
            QMessageBox.warning(self, "Error", "All fields required")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO institution_users (username, password) VALUES (?,?)",
                (self.username.text(), self.password.text())
            )
            conn.commit()
            QMessageBox.information(self, "Success", "Account created successfully")
            self.go_back(None)
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Error", "Username already exists")
        finally:
            conn.close()

    def go_back(self, event):
        from institution_login import InstitutionLogin
        self.login = InstitutionLogin()
        self.login.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    InstitutionSignup().show()
    sys.exit(app.exec_())
