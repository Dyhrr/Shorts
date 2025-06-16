# ShortsSplit

ShortsSplit is a local-only Python application for creating 1080x1920 vertical videos by stacking a top clip (with subtitles) and a bottom clip. It uses faster-whisper for speech-to-text and ffmpeg for video processing.

## Features
- Drag-and-drop interface built with PySide6
- Top clip is transcribed and subtitles are burned into the top half
- Bottom clip is trimmed or looped to match the top clip duration
- Audio comes from the top clip and is normalized
- Simple light/dark mode toggle

## Requirements
- Python 3.10+
- FFmpeg installed and available in PATH
- Install Python dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## Usage
Run the application:
```bash
python shortssplit.py
```
Drop your top and bottom clips into the window and press **Create**. The output `output.mp4` will appear in the same directory as the top clip.
