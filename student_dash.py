import os
import sqlite3
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "main.db")


class StudentDash(QMainWindow):

    def __init__(self, username):
        super().__init__()

        self.username = username

        self.setWindowTitle("Student Dashboard")
        self.setGeometry(100, 100, 1200, 700)

        self.init_ui()
        self.load_certificates()

    
    # UI
    

    def init_ui(self):

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()

        # HEADER
        header_layout = QHBoxLayout()

        welcome = QLabel(f"Welcome {self.username}")
        welcome.setStyleSheet("font-size:18px;font-weight:bold;")
        header_layout.addWidget(welcome)

        header_layout.addStretch()

        logout = QPushButton("Logout")
        logout.setStyleSheet("background:red;color:white;")
        logout.clicked.connect(self.logout)
        header_layout.addWidget(logout)

        main_layout.addLayout(header_layout)

        # FORM
        form = QFormLayout()

        self.student_id = QLineEdit()
        self.department = QLineEdit()
        self.stream = QLineEdit()
        self.cgpa = QLineEdit()

        form.addRow("Student ID:", self.student_id)
        form.addRow("Department:", self.department)
        form.addRow("Stream:", self.stream)
        form.addRow("CGPA:", self.cgpa)

        upload_btn = QPushButton("Upload Certificate")
        upload_btn.setStyleSheet("background:green;color:white;")
        upload_btn.clicked.connect(self.upload_certificate)

        main_layout.addLayout(form)
        main_layout.addWidget(upload_btn)

        # TABLE
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Image", "ID", "Department",
            "Stream", "CGPA",
            "Uploaded At", "Delete"
        ])

        main_layout.addWidget(self.table)
        central.setLayout(main_layout)

    
    # LOGOUT
    

    def logout(self):
        from student_login import StudentLogin
        self.login_window = StudentLogin()
        self.login_window.show()
        self.close()

    
    # UPLOAD
    

    def upload_certificate(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Certificate",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )

        if not file_path:
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO student_certificates
            (student_name, student_id,
             department, course,
             college_name, year,
             cert_path, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.username,
            self.student_id.text(),
            self.department.text(),
            self.stream.text(),
            "N/A",
            self.cgpa.text(),
            file_path,
            datetime.now()
        ))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success",
                                "Certificate Uploaded Successfully")

        self.clear_fields()
        self.load_certificates()

    
    # LOAD CERTIF
    

    def load_certificates(self):

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, cert_path,
                   student_id,
                   department,
                   course,
                   year,
                   uploaded_at
            FROM student_certificates
            WHERE student_name = ?
        """, (self.username,))

        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):

            db_id = row[0]
            image_path = row[1]

            pixmap = QPixmap(image_path).scaled(
                80, 80, Qt.KeepAspectRatio
            )

            label = QLabel()
            label.setPixmap(pixmap)
            self.table.setCellWidget(row_index, 0, label)

            self.table.setItem(row_index, 1, QTableWidgetItem(row[2]))
            self.table.setItem(row_index, 2, QTableWidgetItem(row[3]))
            self.table.setItem(row_index, 3, QTableWidgetItem(row[4]))
            self.table.setItem(row_index, 4, QTableWidgetItem(str(row[5])))
            self.table.setItem(row_index, 5, QTableWidgetItem(str(row[6])))

            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("background:red;color:white;")
            delete_btn.clicked.connect(
                lambda _, id=db_id:
                self.delete_certificate(id)
            )

            self.table.setCellWidget(row_index, 6, delete_btn)

    
    # DELETE
    

    def delete_certificate(self, db_id):

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.No:
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM student_certificates WHERE id=?",
            (db_id,)
        )

        conn.commit()
        conn.close()

        self.load_certificates()

    
    # CLEAR
    

    def clear_fields(self):
        self.student_id.clear()
        self.department.clear()
        self.stream.clear()
        self.cgpa.clear()