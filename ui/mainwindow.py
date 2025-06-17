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
from PySide6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QRect,
    QTimer,
    QThread,
    QObject,
    Signal,
    Slot,
)
from PySide6.QtGui import QFont, QColor, QPixmap
import random
from pathlib import Path

from core import generate_short, load_config, save_config
from core.subtitle_utils import DEFAULT_STYLE

THEMES = {
    "dark": {
        "ACCENT": "#00BCD4",
        "BG": "#212121",
        "FG": "#E0E0E0",
        "BTN_BG": "#424242",
        "BTN_HOVER": "#616161",
        "INPUT_BG": "#2E2E2E",
        "INPUT_FG": "#FFFFFF",
    },
    "light": {
        "ACCENT": "#0078D4",
        "BG": "#FFFFFF",
        "FG": "#000000",
        "BTN_BG": "#E0E0E0",
        "BTN_HOVER": "#CCCCCC",
        "INPUT_BG": "#FFFFFF",
        "INPUT_FG": "#000000",
    },
}

SHADOW_COLOR = "#000000"

QUOTES = [
    "Stay hydrated!",
    "Keep it simple.",
    "Move fast and break things.",
    "Another day, another short.",
]

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


class Worker(QObject):
    """Background worker to run ``generate_short`` in a thread."""

    progress = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, top: str, bottom: str, out: str | None, res: tuple[int, int]):
        super().__init__()
        self.top = top
        self.bottom = bottom
        self.out = out
        self.res = res

    @Slot()
    def run(self) -> None:
        try:
            generate_short(
                self.top,
                self.bottom,
                output_path=self.out,
                progress=self.progress.emit,
                resolution=self.res,
            )
            self.finished.emit(True, "")
        except Exception as exc:  # pragma: no cover - runtime feedback
            self.finished.emit(False, str(exc))

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()

        self.theme = self.config.get("theme", "dark")
        self.colors = THEMES.get(self.theme, THEMES["dark"])
        self.resolution = self.config.get("resolution", "1080x1920")

        self.setAcceptDrops(True)
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
        logo_path = Path(__file__).with_name("Logo.png")
        logo_pix = QPixmap(str(logo_path))
        logo_pix = logo_pix.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pix)
        header.addWidget(logo_label, alignment=Qt.AlignLeft)
        header.addStretch()
        layout.addLayout(header)

        # Title with fade-in animation
        self.title = QLabel("ShortsSplit")
        self.title.setFont(QFont("Segoe UI", 26, QFont.DemiBold))
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(
            f"color: {self.colors['ACCENT']}; letter-spacing: 2px;"
        )
        self.apply_shadow(self.title, blur=20)
        self.fade_in(self.title, delay=300)
        layout.addWidget(self.title)

        subtitle = QLabel("Stack your clips. Burn the subs. Split the views.")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {self.colors['FG']};")
        self.fade_in(subtitle, delay=600)
        layout.addWidget(subtitle)

        quote = QLabel(random.choice(QUOTES))
        quote.setAlignment(Qt.AlignCenter)
        quote.setStyleSheet(
            f"color: {self.colors['ACCENT']}; font-style: italic;"
        )
        self.fade_in(quote, delay=700)
        layout.addWidget(quote)

        layout.addWidget(self.divider())

        # Animated buttons
        self.buttons = []
        self.create_btn = None
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
            if text == "⚙️ Create Shorts Video":
                self.create_btn = btn
            self.fade_in(btn, delay=900 + i*150)

        self.top_label = QLabel("Top clip: none")
        self.top_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.top_label)

        self.bottom_label = QLabel("Bottom clip: none")
        self.bottom_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.bottom_label)

        self.output_label = QLabel("Output file: none")
        self.output_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.output_label)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            f"color: {self.colors['ACCENT']}; font-style: italic;"
        )
        layout.addWidget(self.status_label)

        for clip in ("top", "bottom"):
            if clip_path := self.config.get(f"{clip}_clip"):
                setattr(self, f"{clip}_clip", clip_path)
                label = self.top_label if clip == "top" else self.bottom_label
                label.setText(f"{clip.capitalize()} clip: {clip_path}")

        if out_path := self.config.get("output_path"):
            self.output_path = out_path
            self.output_label.setText(f"Output file: {out_path}")

    def load_file(self, which: str) -> None:
        path, _ = QFileDialog.getOpenFileName(self, f"Select {which} clip")
        if not path:
            return
        setattr(self, f"{which}_clip", path)
        label = self.top_label if which == "top" else self.bottom_label
        label.setText(f"{which.capitalize()} clip: {path}")
        self.config[f"{which}_clip"] = path
        save_config(self.config)

    def set_output(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Select output file", "output.mp4", "MP4 files (*.mp4)"
        )
        if path:
            self.output_path = path
            self.output_label.setText(f"Output file: {path}")
            self.config["output_path"] = path
            save_config(self.config)

    def update_status(self, msg: str) -> None:
        self.status_label.setText(msg)
        QApplication.processEvents()

    def create_short(self) -> None:
        top = getattr(self, "top_clip", None)
        bottom = getattr(self, "bottom_clip", None)
        if not top or not bottom:
            QMessageBox.warning(self, "Missing clips", "Load both clips first")
            return
        out = getattr(self, "output_path", None)

        if self.create_btn is not None:
            self.create_btn.setEnabled(False)

        self.thread = QThread(self)
        self.worker = Worker(top, bottom, out, self._resolution_tuple())
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.update_status)
        self.worker.finished.connect(self._on_thread_finished)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def _on_thread_finished(self, success: bool, error: str) -> None:
        if success:
            QMessageBox.information(self, "Done", "Short created successfully")
        else:
            QMessageBox.critical(self, "Error", error)
        self.status_label.setText("")
        if self.create_btn is not None:
            self.create_btn.setEnabled(True)

    def open_settings(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Theme"))
        theme_box = QComboBox()
        theme_box.addItems(THEMES.keys())
        theme_box.setCurrentText(self.theme)
        layout.addWidget(theme_box)

        layout.addWidget(QLabel("Resolution"))
        res_box = QComboBox()
        res_box.addItems(["1080x1920", "720x1280"])
        res_box.setCurrentText(self.resolution)
        layout.addWidget(res_box)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        def accept() -> None:
            self.theme = theme_box.currentText()
            self.colors = THEMES[self.theme]
            self.setStyleSheet(self.stylesheet())
            self.config["theme"] = self.theme
            self.resolution = res_box.currentText()
            self.config["resolution"] = self.resolution
            save_config(self.config)
            dialog.accept()

        buttons.accepted.connect(accept)
        buttons.rejected.connect(dialog.reject)

        dialog.exec()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = [u.toLocalFile() for u in event.mimeData().urls()]
        files = [p for p in urls if p]
        if not files:
            return
        if len(files) >= 1:
            self.top_clip = files[0]
            self.top_label.setText(f"Top clip: {files[0]}")
            self.config["top_clip"] = files[0]
        if len(files) >= 2:
            self.bottom_clip = files[1]
            self.bottom_label.setText(f"Bottom clip: {files[1]}")
            self.config["bottom_clip"] = files[1]
        save_config(self.config)

    def _resolution_tuple(self) -> tuple[int, int]:
        try:
            w, h = self.resolution.lower().split("x")
            return int(w), int(h)
        except Exception:
            return 1080, 1920

    def divider(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def fade_in(self, widget: QWidget, delay: int = 0) -> None:
        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setDuration(300)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        if delay:
            QTimer.singleShot(delay, anim.start)
        else:
            anim.start()
        widget._fade_anim = anim  # keep reference

    def apply_shadow(self, widget: QWidget, *, blur: int = 10) -> None:
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(SHADOW_COLOR))
        widget.setGraphicsEffect(shadow)

    def stylesheet(self):
        c = self.colors
        return f"""
        QWidget {{
            background-color: {c['BG']};
            color: {c['FG']};
            font-family: 'Segoe UI', sans-serif;
        }}
        QPushButton {{
            background-color: {c['BTN_BG']};
            color: {c['FG']};
            border: 2px solid transparent;
            border-radius: 20px;
            padding: 14px;
            font-size: 15px;
            transition: transform 200ms ease-in-out;
        }}
        QPushButton:hover {{
            background-color: {c['BTN_HOVER']};
            border-color: {c['ACCENT']};
            transform: scale(1.05);
        }}
        QPushButton:pressed {{
            background-color: {c['BTN_BG']};
            transform: scale(0.98);
        }}
        QLineEdit, QComboBox {{
            background-color: {c['INPUT_BG']};
            color: {c['INPUT_FG']};
            border: 1px solid #555;
            border-radius: 8px;
            padding: 6px 8px;
            font-size: 14px;
            transition: border-color 200ms;
        }}
        QLineEdit:focus, QComboBox:focus {{
            border-color: {c['ACCENT']};
        }}
        QLabel {{
            color: {c['FG']};
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
