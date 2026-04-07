import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QPushButton, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Fake Certificate Detection System")
        self.setFixedSize(1080, 600)

        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)

        
        nav_widget = QWidget()
        nav_widget.setFixedWidth(260)
        nav_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(15, 18, 25, 220);
            }
        """)

        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(20)
        nav_layout.setContentsMargins(30, 120, 30, 120)
        nav_widget.setLayout(nav_layout)

        
        button_style = """
            QPushButton {
                color: #E6E6E6;
                background-color: transparent;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 10px;
                padding: 14px;
                font-size: 16px;
                text-align: left;
            }

            QPushButton:hover {
                background-color: rgba(0, 140, 255, 50);
                border: 1px solid #008CFF;
                color: #FFFFFF;
            }
        """

        font = QFont("Segoe UI", 11)

        
        btn_institution = QPushButton("  INSTITUTION")
        btn_recruiter = QPushButton("  RECRUITER")
        btn_student = QPushButton("  STUDENT")

        for btn in (btn_institution, btn_recruiter, btn_student):
            btn.setFont(font)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(button_style)
            btn.setFixedHeight(50)
            nav_layout.addWidget(btn)

        nav_layout.addStretch()

       
        btn_institution.clicked.connect(self.open_institution)
        btn_recruiter.clicked.connect(self.open_recruiter)
        btn_student.clicked.connect(self.open_student)

       
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-image: url("images/bground.png");
                background-repeat: no-repeat;
                background-position: center;
                background-attachment: fixed;
            }
        """)

        
        main_layout.addWidget(nav_widget)
        main_layout.addWidget(content_widget)

    
    def open_institution(self):
        from institution_login import InstitutionLogin
        self.institution_window = InstitutionLogin()
        self.institution_window.show()
        self.close()

    def open_recruiter(self):
        from recruiter_login import RecruiterLogin
        self.recruiter_window = RecruiterLogin()
        self.recruiter_window.show()
        self.close()

    def open_student(self):
        from student_login import StudentLogin
        self.student_window = StudentLogin()
        self.student_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    sys.exit(app.exec_())
