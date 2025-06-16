from pathlib import Path
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
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

from core.whisper_wrapper import transcribe, save_srt
from core.ffmpeg_handler import build_stack


class FileDropEdit(QLineEdit):
    def __init__(self, placeholder: str):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setAcceptDrops(True)

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

    def __init__(self, top: Path, bottom: Path, font_size: int, font_color: str):
        super().__init__()
        self.top = top
        self.bottom = bottom
        self.font_size = font_size
        self.font_color = font_color

    def run(self):
        try:
            self.progress.emit(10)
            lines = transcribe(self.top)
            self.progress.emit(40)
            srt_path = self.top.with_suffix(".srt")
            save_srt(lines, srt_path)
            self.progress.emit(60)
            out_path = self.top.with_name("output.mp4")
            build_stack(self.top, self.bottom, srt_path, out_path, self.font_size, self.font_color)
            self.progress.emit(100)
            self.finished.emit(str(out_path))
        except Exception as exc:
            self.finished.emit(f"Error: {exc}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShortsSplit")

        self.top_edit = FileDropEdit("Drop top clip here")
        self.bottom_edit = FileDropEdit("Drop bottom clip here")
        self.font_size = QComboBox()
        self.font_size.addItems(["24", "30", "36", "48"])
        self.font_color = QComboBox()
        self.font_color.addItems(["white", "yellow", "red", "black"])

        self.run_btn = QPushButton("Create")
        self.theme_btn = QPushButton("Dark Mode")
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.dark = False
        self.run_btn.clicked.connect(self.start_process)
        self.progress = QProgressBar()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Top Clip"))
        layout.addWidget(self.top_edit)
        layout.addWidget(QLabel("Bottom Clip"))
        layout.addWidget(self.bottom_edit)

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

    def start_process(self):
        top = Path(self.top_edit.text())
        bottom = Path(self.bottom_edit.text())
        if not top.exists() or not bottom.exists():
            return
        size = int(self.font_size.currentText())
        color = self.font_color.currentText()
        self.worker = Worker(top, bottom, size, color)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.done)
        self.run_btn.setEnabled(False)
        self.worker.start()

    def done(self, msg: str):
        self.run_btn.setEnabled(True)
        self.statusBar().showMessage(msg, 5000)

    def toggle_theme(self):
        if self.dark:
            self.setStyleSheet("")
            self.theme_btn.setText("Dark Mode")
            self.dark = False
        else:
            self.setStyleSheet("background-color: #333; color: #eee;")
            self.theme_btn.setText("Light Mode")
            self.dark = True


def run_app():
    app = QApplication([])
    win = MainWindow()
    win.resize(400, 300)
    win.show()
    app.exec()
