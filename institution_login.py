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


class InstitutionLogin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Institution Login")
        self.setFixedSize(900, 550)

        self.init_db()
        self.init_ui()

    def init_db(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS institution_users ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "username TEXT UNIQUE NOT NULL, "
            "password TEXT NOT NULL)"
        )
        conn.commit()
        conn.close()

    def init_ui(self):

        root = QWidget()
        root.setStyleSheet("background-color:#F9F9F9;")
        self.setCentralWidget(root)

        
        # MAIN CONTAINER
        

        main_container = QVBoxLayout(root)
        main_container.setContentsMargins(0, 0, 0, 0)

        
        # TOP BAR 
        

        top_bar = QHBoxLayout()
        top_bar.addStretch()

        back_btn = QPushButton("Back")
        back_btn.setFixedWidth(90)
        back_btn.setStyleSheet(
            "background-color:#E53935;"
            "color:white;"
            "border-radius:8px;"
            "padding:6px;"
        )
        back_btn.clicked.connect(self.go_back)

        top_bar.addWidget(back_btn)

        main_container.addLayout(top_bar)

        
        # LOGIN LAYOUT
        

        layout = QHBoxLayout()
        layout.addStretch()

        card = QWidget()
        card.setFixedSize(380, 360)
        card.setStyleSheet(
            "background-color:#FFFFFF;"
            "border-radius:16px;"
            "border:1px solid #E5E5E5;"
        )

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setYOffset(12)
        shadow.setColor(QColor(0, 0, 0, 60))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 35, 35, 35)
        card_layout.setSpacing(18)

        title = QLabel("Institution Login")
        title.setFont(QFont("Segoe UI", 17, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Institution Username")
        self.username.setFixedHeight(42)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFixedHeight(42)

        for w in (self.username, self.password):
            w.setStyleSheet(
                "border:1px solid #DADADA;"
                "border-radius:10px;"
                "padding-left:12px;"
            )

        login_btn = QPushButton("Login")
        login_btn.setFixedHeight(44)
        login_btn.setStyleSheet(
            "background-color:#007AFF;"
            "color:white;"
            "border-radius:10px;"
        )
        login_btn.clicked.connect(self.login)

        signup = QLabel("Don’t have an account? Sign up")
        signup.setAlignment(Qt.AlignCenter)
        signup.setCursor(Qt.PointingHandCursor)
        signup.setStyleSheet("color:#007AFF;font-size:13px;")
        signup.mousePressEvent = self.open_signup

        card_layout.addWidget(title)
        card_layout.addWidget(self.username)
        card_layout.addWidget(self.password)
        card_layout.addWidget(login_btn)
        card_layout.addWidget(signup)

        layout.addWidget(card)
        layout.addStretch()

        main_container.addLayout(layout)

    
    # LOGIN FUNCTION
    

    def login(self):

        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "All fields are required")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM institution_users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            from institution_dash import InstitutionDash
            self.dashboard = InstitutionDash(username)
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Invalid username or password")

    
    # OPEN SIGNUP
    

    def open_signup(self, event):
        from institution_signup import InstitutionSignup
        self.signup = InstitutionSignup()
        self.signup.show()
        self.close()

    
    # BACK BUTTON FUNCTION
    

    def go_back(self):

        from home import HomeWindow
        self.home = HomeWindow()
        self.home.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    InstitutionLogin().show()
    sys.exit(app.exec_())