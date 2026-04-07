import sys
import os
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "student.db")


class StudentLogin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Login")
        self.setFixedSize(900, 550)

        self.init_db()
        self.init_ui()

    def init_db(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS student_users ("
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
            "background:#FFFFFF;"
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

        title = QLabel("Student Login")
        title.setFont(QFont("Segoe UI", 17, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setFixedHeight(42)
        self.username.setStyleSheet(
            "border:1px solid #DADADA;"
            "border-radius:10px;"
            "padding-left:12px;"
        )

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFixedHeight(42)
        self.password.setStyleSheet(
            "border:1px solid #DADADA;"
            "border-radius:10px;"
            "padding-left:12px;"
        )

        login_btn = QPushButton("Login")
        login_btn.setFixedHeight(44)
        login_btn.setStyleSheet(
            "background:#007AFF;"
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
        if not self.username.text() or not self.password.text():
            QMessageBox.warning(self, "Error", "All fields are required")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM student_users WHERE username=? AND password=?",
            (self.username.text(), self.password.text())
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            from student_dash import StudentDash
            self.dashboard = StudentDash(self.username.text())
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Invalid credentials")

    
    # SIGNUP REDIRECT
    

    def open_signup(self, event):
        from student_signup import StudentSignup
        self.signup = StudentSignup()
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
    StudentLogin().show()
    sys.exit(app.exec_())