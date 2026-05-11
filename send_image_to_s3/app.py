import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QLabel
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from uploader_to_s3 import pick_random_image, upload_to_s3

class UploadWorker(QThread):
    success = pyqtSignal(str)  
    error = pyqtSignal(str)   

    def run(self):
        try:
            image_path = pick_random_image()
            s3_key = upload_to_s3(image_path)
            self.success.emit(s3_key)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Uploader")
        self.setFixedSize(340, 160)

        self.btn = QPushButton("📷  Send camera image")
        self.btn.setFixedHeight(44)

        self.status = QLabel("Chờ lệnh...")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setWordWrap(True)

       
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.btn)
        layout.addWidget(self.status)
        layout.addStretch()
        self.setLayout(layout)

        self.btn.clicked.connect(self.on_send)

    def on_send(self):
        self.btn.setEnabled(False)
        self.status.setText("Đang upload...")

        self.worker = UploadWorker()
        self.worker.success.connect(self.on_success)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_success(self, s3_key: str):
        self.status.setText(f"✅ Đã upload:\n{s3_key}")
        self.btn.setEnabled(True)

    def on_error(self, msg: str):
        self.status.setText(f"❌ Lỗi: {msg}")
        self.btn.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
