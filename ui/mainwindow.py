from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QHBoxLayout, QFrame, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QFont

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShortsSplit 🐢")
        self.setMinimumSize(500, 400)
        self.setStyleSheet(self.stylesheet())

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        title = QLabel("ShortsSplit")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Stack your clips. Burn the subs. Split the views.")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addWidget(self.divider())

        self.top_button = QPushButton("🎥 Load Top Clip")
        self.top_button.clicked.connect(lambda: self.load_file("top"))
        layout.addWidget(self.top_button)

        self.bottom_button = QPushButton("📼 Load Bottom Clip")
        self.bottom_button.clicked.connect(lambda: self.load_file("bottom"))
        layout.addWidget(self.bottom_button)

        self.create_button = QPushButton("⚙️ Create Shorts Video")
        self.create_button.clicked.connect(self.create_short)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #888;")
        return line

    def load_file(self, clip_type):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, f"Select {clip_type.capitalize()} Clip")
        if file_path:
            print(f"Loaded {clip_type} clip: {file_path}")
            # Store file path in self for later use
            setattr(self, f"{clip_type}_clip", file_path)

    def create_short(self):
        # This would trigger the main logic
        print("Generating short...")

    def stylesheet(self):
        return """
        QWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
            font-family: 'Segoe UI', sans-serif;
        }
        QPushButton {
            background-color: #3c3f41;
            border: none;
            border-radius: 8px;
            padding: 12px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #505356;
        }
        QPushButton:pressed {
            background-color: #2e2f31;
        }
        QLabel {
            color: #f0f0f0;
        }
        """

# To run the UI manually (if needed):
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
