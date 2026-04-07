import os
import sqlite3
import hashlib
import cv2
import json
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QMessageBox, QFileDialog,
    QDialog, QSplitter, QHeaderView, QProgressBar,
    QLineEdit, QComboBox
)

from PyQt5.QtGui import QPixmap, QImage, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from ai.forensic_engine import analyze_certificate
from pyzbar.pyzbar import decode


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "main.db")



# VERIFICATION WORKER THREAD


class VerificationWorker(QThread):

    progress = pyqtSignal(int)
    stage = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, inst_hash, student_path):
        super().__init__()
        self.inst_hash = inst_hash
        self.student_path = student_path

    def run(self):
        try:

            self.stage.emit("Blockchain Verification")
            self.progress.emit(15)

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            cur.execute(
                "SELECT status FROM institution_certificates WHERE cert_hash=?",
                (self.inst_hash,)
            )

            row = cur.fetchone()
            conn.close()

            if not row:
                self.error.emit("Certificate not found in blockchain.")
                return

            status = row[0]

            if status == "REVOKED":
                self.error.emit("Certificate has been revoked.")
                return

            self.progress.emit(35)

            with open(self.student_path, "rb") as f:
                student_hash = hashlib.sha256(f.read()).hexdigest()

            if student_hash != self.inst_hash:
                self.error.emit("Blockchain hash mismatch.")
                return

            self.progress.emit(50)

            self.stage.emit("AI Forensic Analysis")
            analysis = analyze_certificate(self.student_path)

            self.progress.emit(85)

            self.stage.emit("Finalizing Report")
            self.progress.emit(100)

            analysis["blockchain"] = "VALID"

            self.finished.emit(analysis)

        except Exception as e:
            self.error.emit(str(e))



# PROGRESS DIALOG


class VerificationDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Verification in Progress")
        self.resize(420, 160)
        self.setModal(True)

        layout = QVBoxLayout(self)

        self.stage_label = QLabel("Starting...")
        self.stage_label.setAlignment(Qt.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)

        layout.addWidget(self.stage_label)
        layout.addWidget(self.progress)

    def update_stage(self, text):
        self.stage_label.setText(f"Stage: {text}")

    def update_progress(self, value):
        self.progress.setValue(value)



# MAIN DASHBOARD


class RecruiterDash(QMainWindow):

    def __init__(self, recruiter_name="Recruiter"):
        super().__init__()

        self.setWindowTitle("Fake Certificate Detection System")
        self.resize(1200, 750)

        self.init_ui()
        self.load_data()

    # -------------------------------------------------

    def init_ui(self):

        root = QWidget(self)
        self.setCentralWidget(root)
        main = QVBoxLayout(root)

        
        # TOP BAR (Logout)
        

        top_layout = QHBoxLayout()

        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet(
            "background-color:red;color:white;font-weight:bold;padding:6px;"
        )
        logout_btn.clicked.connect(self.logout)

        top_layout.addWidget(logout_btn)
        top_layout.addStretch()

        main.addLayout(top_layout)

        
        # TITLE
        

        title = QLabel("HYBRID CERTIFICATE VERIFICATION")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:18px;font-weight:bold;")
        main.addWidget(title)

        
        # SEARCH + FILTER BAR
        

        filter_layout = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Student / ID / College")
        self.search_bar.textChanged.connect(self.apply_filters)

        self.department_filter = QComboBox()
        self.department_filter.addItem("All Departments")
        self.department_filter.currentIndexChanged.connect(self.apply_filters)

        self.cgpa_filter = QComboBox()
        self.cgpa_filter.addItems([
            "All CGPA",
            "CGPA >= 6",
            "CGPA >= 7",
            "CGPA >= 8",
            "CGPA >= 9"
        ])
        self.cgpa_filter.currentIndexChanged.connect(self.apply_filters)

        reset_btn = QPushButton("Reset Filters")
        reset_btn.clicked.connect(self.reset_filters)

        filter_layout.addWidget(self.search_bar)
        filter_layout.addWidget(self.department_filter)
        filter_layout.addWidget(self.cgpa_filter)
        filter_layout.addWidget(reset_btn)

        main.addLayout(filter_layout)

        
        # TABLES
        

        self.inst_table = QTableWidget()
        self.inst_table.setColumnCount(6)
        self.inst_table.setHorizontalHeaderLabels(
            ["Student", "ID", "College", "Year", "Course", "Hash"]
        )
        self.inst_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.stu_table = QTableWidget()
        self.stu_table.setColumnCount(6)
        self.stu_table.setHorizontalHeaderLabels(
            ["Student", "ID", "College", "Year", "Course", "Department"]
        )
        self.stu_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        splitter_tables = QSplitter(Qt.Horizontal)
        splitter_tables.addWidget(self.inst_table)
        splitter_tables.addWidget(self.stu_table)

        main.addWidget(splitter_tables)

        
        # BUTTONS
        

        btn_layout = QHBoxLayout()

        verify_btn = QPushButton("Run Full Verification")
        verify_btn.clicked.connect(self.verify)

        qr_btn = QPushButton("QR Validate")
        qr_btn.clicked.connect(self.qr_validate)

        btn_layout.addWidget(verify_btn)
        btn_layout.addWidget(qr_btn)

        main.addLayout(btn_layout)

        
        # IMAGE PANELS
        

        self.original_panel = QLabel("Original")
        self.heatmap_panel = QLabel("GradCAM")
        self.ela_panel = QLabel("ELA")
        self.noise_panel = QLabel("Noise")

        for p in [self.original_panel, self.heatmap_panel, self.ela_panel, self.noise_panel]:
            p.setAlignment(Qt.AlignCenter)
            p.setStyleSheet("border:1px solid #AAA;")

        splitter_images = QSplitter(Qt.Horizontal)
        splitter_images.addWidget(self.original_panel)
        splitter_images.addWidget(self.heatmap_panel)
        splitter_images.addWidget(self.ela_panel)
        splitter_images.addWidget(self.noise_panel)

        main.addWidget(splitter_images)

    
    # LOGOUT FUNCTION
   

    def logout(self):

        try:
            from home import HomeWindow
            self.home = HomeWindow()
            self.home.show()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    
    # FILTER METHODS
    

    def reset_filters(self):

        self.search_bar.clear()
        self.department_filter.setCurrentIndex(0)
        self.cgpa_filter.setCurrentIndex(0)

        self.apply_filters()

    def apply_filters(self):

        search_text = self.search_bar.text().lower()
        dept_filter = self.department_filter.currentText()
        cgpa_filter = self.cgpa_filter.currentText()

        for row in range(self.stu_table.rowCount()):

            show = True

            student = self.stu_table.item(row,0).text().lower()
            sid = self.stu_table.item(row,1).text().lower()
            college = self.stu_table.item(row,2).text().lower()

            if search_text not in student and search_text not in sid and search_text not in college:
                show = False

            if dept_filter != "All Departments":
                table_dept = self.stu_table.item(row,5).text()
                if dept_filter != table_dept:
                    show = False

            if cgpa_filter != "All CGPA":
                try:
                    cgpa = float(self.stu_table.item(row,3).text())
                    value = int(cgpa_filter.split(">=")[1])
                    if cgpa < value:
                        show = False
                except:
                    pass

            self.stu_table.setRowHidden(row, not show)

    
    # LOAD DATA
    

    def load_data(self):

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            SELECT student_name, student_id, college_name,
                   year, course, cert_hash, status
            FROM institution_certificates
        """)

        inst = cur.fetchall()
        self.inst_table.setRowCount(len(inst))

        for r, row in enumerate(inst):
            status = row[-1]
            for c in range(6):
                item = QTableWidgetItem(str(row[c]))
                if status == "REVOKED":
                    item.setBackground(QColor("red"))
                    item.setForeground(QColor("white"))
                self.inst_table.setItem(r, c, item)

        cur.execute("""
            SELECT student_name, student_id, college_name,
                   year, course, department, cert_path
            FROM student_certificates
        """)

        stu = cur.fetchall()

        self.student_paths = []
        self.stu_table.setRowCount(len(stu))

        departments = set()

        for r, row in enumerate(stu):
            self.student_paths.append(row[-1])
            for c, val in enumerate(row[:-1]):
                self.stu_table.setItem(r, c, QTableWidgetItem(str(val)))

            departments.add(row[5])

        for d in sorted(departments):
            self.department_filter.addItem(d)

        conn.close()

    
    # VERIFY
    

    def verify(self):

        inst_row = self.inst_table.currentRow()
        stu_row = self.stu_table.currentRow()

        if inst_row == -1 or stu_row == -1:
            QMessageBox.warning(self, "Error", "Select both certificates")
            return

        inst_hash = self.inst_table.item(inst_row, 5).text()
        student_path = self.student_paths[stu_row]

        self.dialog = VerificationDialog()
        self.dialog.show()

        self.worker = VerificationWorker(inst_hash, student_path)

        self.worker.progress.connect(self.dialog.update_progress)
        self.worker.stage.connect(self.dialog.update_stage)
        self.worker.finished.connect(self.verification_finished)
        self.worker.error.connect(self.verification_failed)

        self.worker.start()

    # -------------------------------------------------

    def verification_finished(self, analysis):

        self.dialog.close()

        stu_row = self.stu_table.currentRow()
        student_path = self.student_paths[stu_row]

        original = cv2.imread(student_path)

        self.display_image(self.original_panel, original)

        if "gradcam" in analysis:
            self.display_image(self.heatmap_panel, analysis["gradcam"])

        self.display_image(self.ela_panel, analysis["ela"])
        self.display_image(self.noise_panel, analysis["noise"])

        QMessageBox.information(
            self,
            "Verification Complete",
            f"Mode: {analysis['mode']}\n"
            f"Prediction: {analysis['label']}\n"
            f"Confidence: {analysis['confidence']}%\n"
            f"Blockchain: {analysis.get('blockchain','UNKNOWN')}\n"
            f"Seal: {analysis.get('seal_status','UNKNOWN')}\n"
            f"Signature: {analysis.get('signature_status','UNKNOWN')}"
        )

    # -------------------------------------------------

    def verification_failed(self, message):
        self.dialog.close()
        QMessageBox.critical(self, "Verification Failed", message)

    # -------------------------------------------------

    def display_image(self, label, img):

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape

        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)

        pix = QPixmap.fromImage(qimg).scaled(
            label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        label.setPixmap(pix)

    # -------------------------------------------------

    def qr_validate(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select QR Image", "", "Images (*.png *.jpg)"
        )

        if not file_path:
            return

        img = cv2.imread(file_path)
        decoded = decode(img)

        if not decoded:
            QMessageBox.warning(self, "Invalid QR", "QR not readable")
            return

        try:
            qr_data = json.loads(decoded[0].data.decode("utf-8"))
        except:
            QMessageBox.critical(self, "QR Invalid", "Invalid QR format")
            return

        cert_hash = qr_data.get("certificate_hash")

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute(
            "SELECT cert_hash FROM institution_certificates WHERE cert_hash=?",
            (cert_hash,)
        )

        row = cur.fetchone()
        conn.close()

        if row:
            QMessageBox.information(
                self,
                "QR Valid",
                "Certificate exists in blockchain."
            )
        else:
            QMessageBox.critical(
                self,
                "QR Invalid",
                "Certificate NOT found."
            )