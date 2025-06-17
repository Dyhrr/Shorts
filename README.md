# 🐢 ShortsSplit

**ShortsSplit** is a local-first Python tool that slaps together vertical 1080x1920 videos by stacking a *top* clip (with subtitles) and a *bottom* clip (gameplay, memes, chaos — your call). Built for lazy perfectionists who hate editing but love looking good.

It uses [`faster-whisper`](https://github.com/guillaumekln/faster-whisper) for transcription and `ffmpeg` for video slicing and magic. No internet, no nonsense. Just drag, drop, and go.

## ⚙️ Features
- 🖱️ Drag-and-drop PySide6 interface (yes, it actually works)
- 🧠 Top clip gets subtitled using Whisper (GPU if available, otherwise CPU)
- 🪞 Bottom clip loops or trims to match top duration automatically
- 🔊 Audio only from top clip, normalized to not blow ears out
- 🌗 Light/dark mode toggle (for when you're feeling emo)
- 💾 Remembers last used clips and settings
- 🎨 Custom subtitle style options
- 🗄️ Choose output file name and location
- 📣 Simple progress messages while processing
- 🔗 Settings panel for YouTube/TikTok links

## 🧪 Requirements
- Python 3.10+
- FFmpeg (installed and in your PATH — don’t DM me if it’s not)
- Python packages:
  ```bash
  pip install -r requirements.txt
  ```

## 🚀 Usage
Run it like a boss:

```bash
python shortssplit.py
```

Or run it from the terminal with your clips:

```bash
python shortssplit.py top.mp4 bottom.mp4 -o final.mp4
```

The transcriber tries to use your GPU first. If CUDA libraries are missing, it
falls back to CPU automatically. You can force CPU mode by setting:

```bash
set WHISPER_DEVICE=cpu  # Windows
# or
export WHISPER_DEVICE=cpu  # Unix-like
```

Drop your clips into the window:

Top = voice or interview (this gets transcribed)

Bottom = gameplay or background loop

Hit Create and the video is written to your chosen output file (defaults to
`output.mp4` next to the top clip).

## 📑 Function Overview

Below is a quick reference of the main Python functions used by ShortsSplit.

### Fully Working

- `run_app()` – launches the PySide6 interface.
- `generate_short(top, bottom, model_size="base", device="auto", style=None, output_path=None, progress=None)` – handles transcription and video stacking, returning the path to the created video.
- `build_stack(top, bottom, subtitle, out_path)` – calls FFmpeg to stack the clips and burn the subtitles. It tries GPU encoding first and falls back to CPU when necessary.
- `transcribe(path, model_size="base", device="auto")` – uses `faster-whisper` to create short subtitle cues from the audio track.
- `save_ass(cues, out_path, style=None)` – writes subtitle cues to an ASS file with a default style.
- `check_ffmpeg()` – ensures FFmpeg and FFprobe are installed.
- `probe_duration(path)` – retrieves the duration of a media file in seconds.

## 📦 Packaging

Run the included `build_pyinstaller.py` script to produce a standalone
executable:

```bash
python build_pyinstaller.py
```

### Works, but Has Limitations

- The UI mentions a light/dark mode toggle, but the implementation is not present yet.
- GPU encoding and transcription rely on the machine's hardware. If a GPU is unavailable, the process falls back to CPU and may take longer.

## 👤 About the Author

Built by [Nick (a.k.a. Dyhrrr)](https://twitch.tv/dyhrrr) — a Danish service desk agent by day, FPS goblin and tool-forgersmith by night.  
Refuses to manually edit subtitles. Believes in local tools, dumb humor, and caffeinated productivity.  
Currently building an offline Jarvis clone named **Lex** and this is just one piece of the puzzle.

> "If it needs more than one button, it's already too complicated."
