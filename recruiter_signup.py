import sys, os, sqlite3
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "recruiter.db")


class RecruiterSignup(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recruiter Signup")
        self.setFixedSize(900, 550)
        self.init_ui()

    def init_ui(self):
        root = QWidget()
        root.setStyleSheet("background-color:#F9F9F9;")
        self.setCentralWidget(root)

        layout = QHBoxLayout(root)
        layout.addStretch()

        card = QWidget()
        card.setFixedSize(380, 380)
        card.setStyleSheet("background:#FFF;border-radius:16px;border:1px solid #E5E5E5;")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setYOffset(12)
        shadow.setColor(QColor(0,0,0,60))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35,35,35,35)

        title = QLabel("Recruiter Signup")
        title.setFont(QFont("Segoe UI",17,QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.user = QLineEdit()
        self.user.setPlaceholderText("Username")
        self.passw = QLineEdit()
        self.passw.setPlaceholderText("Password")
        self.passw.setEchoMode(QLineEdit.Password)

        for w in (self.user, self.passw):
            w.setFixedHeight(42)
            w.setStyleSheet("border:1px solid #DADADA;border-radius:10px;padding-left:12px;")

        btn = QPushButton("Create Account")
        btn.setFixedHeight(44)
        btn.setStyleSheet("background:#007AFF;color:white;border-radius:10px;")
        btn.clicked.connect(self.signup)

        back = QLabel("← Back to Login")
        back.setAlignment(Qt.AlignCenter)
        back.setCursor(Qt.PointingHandCursor)
        back.setStyleSheet("color:#007AFF;font-size:13px;")
        back.mousePressEvent = self.back

        card_layout.addWidget(title)
        card_layout.addWidget(self.user)
        card_layout.addWidget(self.passw)
        card_layout.addWidget(btn)
        card_layout.addWidget(back)

        layout.addWidget(card)
        layout.addStretch()

    def signup(self):
        if not self.user.text() or not self.passw.text():
            QMessageBox.warning(self,"Error","All fields required")
            return

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO recruiter_users VALUES(NULL,?,?)",
                        (self.user.text(), self.passw.text()))
            conn.commit()
            QMessageBox.information(self,"Success","Signup successful")
            self.back(None)
        except sqlite3.IntegrityError:
            QMessageBox.critical(self,"Error","Username already exists")
        finally:
            conn.close()

    def back(self,event):
        from recruiter_login import RecruiterLogin
        RecruiterLogin().show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    RecruiterSignup().show()
    sys.exit(app.exec_())
