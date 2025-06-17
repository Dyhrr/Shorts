import PyInstaller.__main__
import os
import sys
from pathlib import Path

# Define paths
base_dir = Path(__file__).resolve().parent
entry_point = "shortssplit.py"
name = "ShortsSplit"
logo = Path("ui/Logo.png")

# Build command
PyInstaller.__main__.run([
    str(base_dir / entry_point),
    "--name", name,
    "--onefile",
    "--noconfirm",
    "--clean",  # 🧼 Removes old build cache
    f"--add-data={logo.as_posix()}{os.pathsep}ui",
    "--hidden-import=shiboken6",  # 🧠 Just in case
    "--hidden-import=PySide6.QtCore",
    "--hidden-import=PySide6.QtGui",
    "--hidden-import=PySide6.QtWidgets",
])
