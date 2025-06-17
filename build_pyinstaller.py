import PyInstaller.__main__

PyInstaller.__main__.run([
    "shortssplit.py",
    "--onefile",
    "--add-data=ui/Logo.png:ui",
    "--name=ShortsSplit",
])
