import os
import hashlib
import sqlite3
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QInputDialog
)
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt

from blockchain.chain import Blockchain
from blockchain.crypto_utils import generate_keys
from qr.qr_generator import generate_qr


class InstitutionDash(QMainWindow):

    def __init__(self, institution_name):
        super().__init__()

        self.institution_id = institution_name
        self.institution_name = institution_name
        self.blockchain = Blockchain()

        self.setWindowTitle("Institution Dashboard")
        self.setGeometry(100, 100, 1300, 750)

        self.init_ui()
        self.load_certificates()

    
    # UI SETUP
    

    def init_ui(self):

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()

        header_layout = QHBoxLayout()

        self.welcome_label = QLabel(f"Welcome {self.institution_name}")
        self.welcome_label.setStyleSheet(
            "font-size:18px;font-weight:bold;"
        )
        header_layout.addWidget(self.welcome_label)

        header_layout.addStretch()

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setStyleSheet(
            "background:red;color:white;padding:6px 15px;"
        )
        self.logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_btn)

        main_layout.addLayout(header_layout)

        form = QFormLayout()

        self.student_name = QLineEdit()
        self.student_id = QLineEdit()
        self.college_name = QLineEdit()
        self.college_id = QLineEdit()
        self.year = QLineEdit()
        self.course = QLineEdit()
        self.department = QLineEdit()

        form.addRow("Student Name:", self.student_name)
        form.addRow("Student ID:", self.student_id)
        form.addRow("College Name:", self.college_name)
        form.addRow("College ID:", self.college_id)
        form.addRow("Year:", self.year)
        form.addRow("Course:", self.course)
        form.addRow("Department:", self.department)

        self.upload_btn = QPushButton("Upload & Issue Certificate")
        self.upload_btn.setStyleSheet(
            "background:green;color:white;padding:6px;"
        )
        self.upload_btn.clicked.connect(self.upload_certificate)

        main_layout.addLayout(form)
        main_layout.addWidget(self.upload_btn)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Image", "Name", "ID", "Department",
            "Cert Hash", "Block Hash",
            "Status", "Revoke", "Delete"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)

        main_layout.addWidget(self.table)
        central.setLayout(main_layout)

    
    # LOGOUT
    

    def logout(self):
        from institution_login import InstitutionLogin
        self.login_window = InstitutionLogin()
        self.login_window.show()
        self.close()

    
    # HASH GENERATION
    

    def generate_hash(self, file_path):
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    
    # ISSUE CERTIFICATE
    

    def upload_certificate(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Certificate",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )

        if not file_path:
            return

        cert_hash = self.generate_hash(file_path)

        
        
        

        key_dir = "blockchain/keys"
        os.makedirs(key_dir, exist_ok=True)

        private_key_path = f"{key_dir}/{self.institution_id}_private.pem"

        if not os.path.exists(private_key_path):
            generate_keys(self.institution_id)

        
        # Add block
        

        block_data = self.blockchain.add_certificate_block(
            self.institution_id,
            [cert_hash]
        )

        block_hash = block_data["block_hash"]

        qr_data = {
            "institution_id": self.institution_id,
            "certificate_hash": cert_hash,
            "block_hash": block_hash
        }

        qr_path = generate_qr(qr_data, cert_hash)

        conn = sqlite3.connect("database/main.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO institution_certificates
            (institution_id, student_name, student_id,
             college_name, college_id, year,
             course, department,
             cert_path, cert_hash,
             prev_hash, block_hash,
             timestamp, qr_path, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE')
        """, (
            self.institution_id,
            self.student_name.text(),
            self.student_id.text(),
            self.college_name.text(),
            self.college_id.text(),
            self.year.text(),
            self.course.text(),
            self.department.text(),
            file_path,
            cert_hash,
            block_data["previous_hash"],
            block_hash,
            datetime.now(),
            qr_path
        ))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success",
                                "Certificate Issued Successfully")

        self.clear_fields()
        self.load_certificates()

    
    # LOAD TABLE
    

    def load_certificates(self):

        conn = sqlite3.connect("database/main.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, cert_path, student_name,
                   student_id, department,
                   cert_hash, block_hash,
                   status
            FROM institution_certificates
            WHERE institution_id = ?
        """, (self.institution_id,))

        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):

            db_id = row[0]
            image_path = row[1]
            status = row[7]
            cert_hash = row[5]

            pixmap = QPixmap(image_path).scaled(
                80, 80, Qt.KeepAspectRatio
            )
            label = QLabel()
            label.setPixmap(pixmap)
            self.table.setCellWidget(row_index, 0, label)

            self.table.setItem(row_index, 1,
                               QTableWidgetItem(row[2]))
            self.table.setItem(row_index, 2,
                               QTableWidgetItem(row[3]))
            self.table.setItem(row_index, 3,
                               QTableWidgetItem(row[4]))
            self.table.setItem(row_index, 4,
                               QTableWidgetItem(row[5]))
            self.table.setItem(row_index, 5,
                               QTableWidgetItem(row[6]))

            status_item = QTableWidgetItem(status)

            if status == "REVOKED":
                status_item.setBackground(QColor(255, 100, 100))
            else:
                status_item.setBackground(QColor(100, 255, 100))

            self.table.setItem(row_index, 6, status_item)

            revoke_btn = QPushButton("Revoke")
            revoke_btn.setStyleSheet("background:orange;")
            revoke_btn.clicked.connect(
                lambda _, h=cert_hash, id=db_id:
                self.revoke_certificate(h, id)
            )
            self.table.setCellWidget(row_index, 7, revoke_btn)

            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet(
                "background:red;color:white;"
            )
            delete_btn.clicked.connect(
                lambda _, id=db_id:
                self.delete_certificate(id)
            )
            self.table.setCellWidget(row_index, 8, delete_btn)

    
    # REVOKE
    

    def revoke_certificate(self, cert_hash, db_id):

        reason, ok = QInputDialog.getText(
            self,
            "Revoke Certificate",
            "Enter Revocation Reason:"
        )

        if not ok:
            return

        self.blockchain.revoke_certificate(
            self.institution_id,
            cert_hash,
            reason
        )

        conn = sqlite3.connect("database/main.db")
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE institution_certificates
            SET status='REVOKED',
                revoked_at=?,
                revocation_reason=?
            WHERE id=?
        """, (datetime.now(), reason, db_id))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Revoked",
                                "Certificate Revoked Successfully")

        self.load_certificates()

    
    # DELETE
    

    def delete_certificate(self, db_id):

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.No:
            return

        conn = sqlite3.connect("database/main.db")
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM institution_certificates
            WHERE id=?
        """, (db_id,))

        conn.commit()
        conn.close()

        self.load_certificates()

    
    # CLEAR FORM
    

    def clear_fields(self):
        self.student_name.clear()
        self.student_id.clear()
        self.college_name.clear()
        self.college_id.clear()
        self.year.clear()
        self.course.clear()
        self.department.clear()