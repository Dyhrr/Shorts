from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QProgressBar,
    QComboBox,
)

from core.whisper_wrapper import transcribe
from core.ffmpeg_handler import build_stack
from core.subtitle_utils import save_srt
from core.utils import probe_duration


class FileDropEdit(QLineEdit):
    file_dropped = Signal(str)

    def __init__(self, placeholder: str):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setAcceptDrops(True)
        self.textChanged.connect(self._emit_path)

    def _emit_path(self, text: str) -> None:
        if Path(text).exists():
            self.file_dropped.emit(text)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            self.setText(url.toLocalFile())
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


class Worker(QThread):
    progress = Signal(int)
    finished = Signal(str)

    def __init__(self, top: Path, bottom: Path, font_size: int, font_color: str, subtitle: Path | None):
        super().__init__()
        self.top = top
        self.bottom = bottom
        self.font_size = font_size
        self.font_color = font_color
        self.subtitle = subtitle

    def run(self):
        """Generate subtitles if needed and build the stacked video."""
        try:
            srt_path = self._prepare_subtitles()
            self.progress.emit(60)
            out_path = self._create_output(srt_path)
            self.progress.emit(100)
            self.finished.emit(str(out_path))
        except Exception as exc:
            self.finished.emit(f"Error: {exc}")

    def _prepare_subtitles(self) -> Path:
        """Return path to subtitle file, transcribing when necessary."""
        if self.subtitle and self.subtitle.exists():
            return self.subtitle
        self.progress.emit(10)
        lines = transcribe(self.top)
        self.progress.emit(40)
        srt_path = self.top.with_suffix(".srt")
        save_srt(lines, srt_path)
        return srt_path

    def _create_output(self, srt_path: Path) -> Path:
        """Stack the clips and burn in subtitles."""
        out_path = self.top.with_name("output.mp4")
        build_stack(
            self.top,
            self.bottom,
            srt_path,
            out_path,
            self.font_size,
            self.font_color,
        )
        return out_path


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShortsSplit")

        self.top_edit = FileDropEdit("Drop top clip here")
        self.bottom_edit = FileDropEdit("Drop bottom clip here")
        self.subtitle_edit = FileDropEdit("Optional subtitle file")

        self.top_edit.file_dropped.connect(self.update_durations)
        self.bottom_edit.file_dropped.connect(self.update_durations)

        self.top_dur_label = QLabel("")
        self.bottom_dur_label = QLabel("")

        self.font_size = QComboBox()
        self.font_size.addItems(["24", "30", "36", "48"])
        self.font_color = QComboBox()
        self.font_color.addItems(["white", "yellow", "red", "black"])

        self.run_btn = QPushButton("Create")
        self.run_btn.clicked.connect(self.start_process)

        self.theme_btn = QPushButton("Light Mode")
        self.dark = True
        self.toggle_theme()
        self.theme_btn.clicked.connect(self.toggle_theme)

        self.progress = QProgressBar()

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        layout.addWidget(QLabel("Top Clip"))
        layout.addWidget(self.top_edit)
        layout.addWidget(self.top_dur_label)
        layout.addWidget(QLabel("Bottom Clip"))
        layout.addWidget(self.bottom_edit)
        layout.addWidget(self.bottom_dur_label)
        layout.addWidget(QLabel("Subtitle (.srt)"))
        layout.addWidget(self.subtitle_edit)

        opts = QHBoxLayout()
        opts.addWidget(QLabel("Font Size"))
        opts.addWidget(self.font_size)
        opts.addWidget(QLabel("Font Color"))
        opts.addWidget(self.font_color)
        layout.addLayout(opts)

        layout.addWidget(self.run_btn)
        layout.addWidget(self.progress)
        layout.addWidget(self.theme_btn)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_durations(self, _=None):
        top = Path(self.top_edit.text())
        bottom = Path(self.bottom_edit.text())
        if top.exists():
            self.top_dur_label.setText(f"Duration: {probe_duration(top):.1f}s")
        if bottom.exists():
            self.bottom_dur_label.setText(f"Duration: {probe_duration(bottom):.1f}s")

    def start_process(self):
        top = Path(self.top_edit.text())
        bottom = Path(self.bottom_edit.text())
        subtitle = Path(self.subtitle_edit.text()) if self.subtitle_edit.text() else None
        if not top.exists() or not bottom.exists():
            return
        size = int(self.font_size.currentText())
        color = self.font_color.currentText()
        self.worker = Worker(top, bottom, size, color, subtitle)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.done)
        self.run_btn.setEnabled(False)
        self.worker.start()

    def done(self, msg: str):
        self.run_btn.setEnabled(True)
        self.statusBar().showMessage(msg, 5000)

    def toggle_theme(self):
        if self.dark:
            self.setStyleSheet("background-color: #333; color: #eee;")
            self.theme_btn.setText("Light Mode")
            self.dark = False
        else:
            self.setStyleSheet("")
            self.theme_btn.setText("Dark Mode")
            self.dark = True


def run_app():
    app = QApplication([])
    win = MainWindow()
    win.resize(400, 400)
    win.show()
    app.exec()
