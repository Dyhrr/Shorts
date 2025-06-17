from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QHBoxLayout,
    QFrame,
    QApplication,
    QMessageBox,
    QLineEdit,
    QComboBox,
    QDialog,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from core import generate_short, load_config, save_config
from core.subtitle_utils import DEFAULT_STYLE

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()

        self.setWindowTitle("ShortsSplit 🐢")
        self.setMinimumSize(500, 450)
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

        self.output_button = QPushButton("📁 Set Output File")
        self.output_button.clicked.connect(self.set_output)
        layout.addWidget(self.output_button)

        self.create_button = QPushButton("⚙️ Create Shorts Video")
        self.create_button.clicked.connect(self.create_short)
        layout.addWidget(self.create_button)

        self.settings_button = QPushButton("🔧 Settings")
        self.settings_button.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_button)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # Load saved paths
        for clip in ("top", "bottom"):
            if clip_path := self.config.get(f"{clip}_clip"):
                setattr(self, f"{clip}_clip", clip_path)

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
            setattr(self, f"{clip_type}_clip", file_path)
            self.config[f"{clip_type}_clip"] = file_path
            save_config(self.config)

    def set_output(self):
        file_dialog = QFileDialog()
        path, _ = file_dialog.getSaveFileName(self, "Select Output File", self.config.get("output_path", "output.mp4"), "MP4 files (*.mp4)")
        if path:
            self.config["output_path"] = path
            save_config(self.config)

    def create_short(self):
        try:
            top = getattr(self, "top_clip")
            bottom = getattr(self, "bottom_clip")
        except AttributeError:
            QMessageBox.warning(self, "Missing Clips", "Load both top and bottom clips first.")
            return

        def progress(msg: str) -> None:
            self.status_label.setText(msg)
            QApplication.processEvents()

        output = generate_short(
            top,
            bottom,
            device=self.config.get("device", "auto"),
            style=self.config.get("subtitle_style"),
            output_path=self.config.get("output_path"),
            progress=progress,
        )
        QMessageBox.information(self, "Done", f"Created {output}")
        self.status_label.setText(f"Created {output}")
        self.config["top_clip"] = top
        self.config["bottom_clip"] = bottom
        save_config(self.config)

    def open_settings(self):
        dialog = SettingsDialog(self.config)
        if dialog.exec():
            save_config(self.config)

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


class SettingsDialog(QDialog):
    def __init__(self, config: dict):
        super().__init__()
        self.setWindowTitle("Settings")
        self.config = config
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Whisper device:"))
        self.device_combo = QComboBox()
        self.device_combo.addItems(["auto", "cpu", "cuda"])
        self.device_combo.setCurrentText(config.get("device", "auto"))
        layout.addWidget(self.device_combo)

        style = config.get("subtitle_style", DEFAULT_STYLE)
        layout.addWidget(QLabel("Subtitle font:"))
        self.font_edit = QLineEdit(style.get("FontName", "Arial"))
        layout.addWidget(self.font_edit)

        layout.addWidget(QLabel("Font size:"))
        self.size_edit = QLineEdit(str(style.get("FontSize", 36)))
        layout.addWidget(self.size_edit)

        layout.addWidget(QLabel("Primary colour:"))
        self.primary_edit = QLineEdit(style.get("PrimaryColour", "&H00FFFFFF"))
        layout.addWidget(self.primary_edit)

        layout.addWidget(QLabel("Outline colour:"))
        self.outline_edit = QLineEdit(style.get("OutlineColour", "&H00000000"))
        layout.addWidget(self.outline_edit)

        layout.addWidget(QLabel("Outline width:"))
        self.outline_width_edit = QLineEdit(str(style.get("Outline", 2)))
        layout.addWidget(self.outline_width_edit)

        layout.addWidget(QLabel("YouTube URL:"))
        self.youtube_edit = QLineEdit(config.get("youtube", ""))
        layout.addWidget(self.youtube_edit)

        layout.addWidget(QLabel("TikTok URL:"))
        self.tiktok_edit = QLineEdit(config.get("tiktok", ""))
        layout.addWidget(self.tiktok_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def accept(self) -> None:
        self.config["device"] = self.device_combo.currentText()
        self.config["youtube"] = self.youtube_edit.text()
        self.config["tiktok"] = self.tiktok_edit.text()
        self.config["subtitle_style"] = {
            "FontName": self.font_edit.text() or DEFAULT_STYLE["FontName"],
            "FontSize": int(self.size_edit.text() or DEFAULT_STYLE["FontSize"]),
            "PrimaryColour": self.primary_edit.text() or DEFAULT_STYLE["PrimaryColour"],
            "OutlineColour": self.outline_edit.text() or DEFAULT_STYLE["OutlineColour"],
            "BorderStyle": 1,
            "Outline": int(self.outline_width_edit.text() or DEFAULT_STYLE["Outline"]),
            "Shadow": 0,
            "Alignment": 2,
        }
        super().accept()


def run_app() -> None:
    """Launch the application and show the main window."""
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

# To run the UI manually (if needed):
if __name__ == "__main__":
    run_app()
