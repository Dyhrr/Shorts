# 🐢 ShortsSplit

**ShortsSplit** is a local-first Python tool that slaps together vertical 1080x1920 videos by stacking a *top* clip (with subtitles) and a *bottom* clip (gameplay, memes, chaos — your call). Built for lazy perfectionists who hate editing but love looking good.

It uses [`faster-whisper`](https://github.com/guillaumekln/faster-whisper) for transcription and `ffmpeg` for video slicing and magic. No internet, no nonsense. Just drag, drop, and go.

## ⚙️ Features
- 🖱️ Drag-and-drop PySide6 interface (yes, it actually works)
- 🧠 Top clip gets subtitled using Whisper (GPU or CPU, your funeral)
- 🪞 Bottom clip loops or trims to match top duration automatically
- 🔊 Audio only from top clip, normalized to not blow ears out
- 🌗 Light/dark mode toggle (for when you're feeling emo)

## 🧪 Requirements
- Python 3.10+
- FFmpeg (installed and in your PATH — don’t DM me if it’s not)
- Python packages:
  ```bash
  pip install -r requirements.txt
🚀 Usage
Run it like a boss:

bash
Copy
Edit
python shortssplit.py
Drop your clips into the window:

Top = voice or interview (this gets transcribed)

Bottom = gameplay or background loop

Hit Create, and you’ll get output.mp4 in the same folder as the top clip.
