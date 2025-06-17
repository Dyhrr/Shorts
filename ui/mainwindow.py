from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QFrame,
    QApplication,
    QMessageBox,
    QLineEdit,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont, QColor, QPixmap

from core import generate_short, load_config, save_config
from core.subtitle_utils import DEFAULT_STYLE

ACCENT = "#00BCD4"
BG = "#212121"
FG = "#E0E0E0"
BTN_BG = "#424242"
BTN_HOVER = "#616161"
INPUT_BG = "#2E2E2E"
INPUT_FG = "#FFFFFF"
SHADOW_COLOR = "#000000"

class AnimatedButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.OutBack)

    def enterEvent(self, e):
        geom = self.geometry()
        target = QRect(geom.x()-5, geom.y()-5, geom.width()+10, geom.height()+10)
        self._anim.stop()
        self._anim.setStartValue(geom)
        self._anim.setEndValue(target)
        self._anim.start()
        super().enterEvent(e)

    def leaveEvent(self, e):
        geom = self.geometry()
        original = self.parent().layout().itemAt(self.parent().layout().indexOf(self)).widget().geometry()
        self._anim.stop()
        self._anim.setStartValue(geom)
        self._anim.setEndValue(original)
        self._anim.start()
        super().leaveEvent(e)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()

        self.setWindowTitle("ShortsSplit 🐢")
        self.setMinimumSize(540, 480)
        self.setStyleSheet(self.stylesheet())

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Logo in the top-left corner
        header = QHBoxLayout()
        logo_label = QLabel(self)
        logo_pix = QPixmap("path/to/logo.png")  # TODO: replace with your logo path
        logo_pix = logo_pix.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pix)
        header.addWidget(logo_label, alignment=Qt.AlignLeft)
        header.addStretch()
        layout.addLayout(header)

        # Title with fade-in animation
        self.title = QLabel("ShortsSplit")
        self.title.setFont(QFont("Segoe UI", 26, QFont.DemiBold))
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(f"color: {ACCENT}; letter-spacing: 2px;")
        self.apply_shadow(self.title, blur=20)
        self.fade_in(self.title, delay=300)
        layout.addWidget(self.title)

        subtitle = QLabel("Stack your clips. Burn the subs. Split the views.")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {FG};")
        self.fade_in(subtitle, delay=600)
        layout.addWidget(subtitle)

        layout.addWidget(self.divider())

        # Animated buttons
        self.buttons = []
        btn_defs = [
            ("🎥 Load Top Clip", lambda: self.load_file("top")),
            ("📼 Load Bottom Clip", lambda: self.load_file("bottom")),
            ("📁 Set Output File", self.set_output),
            ("⚙️ Create Shorts Video", self.create_short),
            ("🔧 Settings", self.open_settings),
        ]
        for i, (text, slot) in enumerate(btn_defs):
            btn = AnimatedButton(text)
            btn.clicked.connect(slot)
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn)
            self.buttons.append(btn)
            self.fade_in(btn, delay=900 + i*150)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"color: {ACCENT}; font-style: italic;")
        layout.addWidget(self.status_label)

        for clip in ("top", "bottom"):
            if clip_path := self.config.get(f"{clip}_clip"):
                setattr(self, f"{clip}_clip", clip_path)

    # ... other methods unchanged ...

    def stylesheet(self):
        return f"""
        QWidget {{
            background-color: {BG};
            color: {FG};
            font-family: 'Segoe UI', sans-serif;
        }}
        QPushButton {{
            background-color: {BTN_BG};
            color: {FG};
            border: 2px solid transparent;
            border-radius: 20px;
            padding: 14px;
            font-size: 15px;
            transition: transform 200ms ease-in-out;
        }}
        QPushButton:hover {{
            background-color: {BTN_HOVER};
            border-color: {ACCENT};
            transform: scale(1.05);
        }}
        QPushButton:pressed {{
            background-color: {BTN_BG};
            transform: scale(0.98);
        }}
        QLineEdit, QComboBox {{
            background-color: {INPUT_BG};
            color: {INPUT_FG};
            border: 1px solid #555;
            border-radius: 8px;
            padding: 6px 8px;
            font-size: 14px;
            transition: border-color 200ms;
        }}
        QLineEdit:focus, QComboBox:focus {{
            border-color: {ACCENT};
        }}
        QLabel {{
            color: {FG};
            transition: color 200ms;
        }}
        QFrame {{
            margin-top: 12px;
            margin-bottom: 12px;
        }}
        """


def run_app() -> None:
    """Launch the application and show the main window."""
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

# To run the UI manually (if needed):
if __name__ == "__main__":
    run_app()
