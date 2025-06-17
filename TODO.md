# ✅ ShortSplit TODO – Pre-Launch Checklist

This is the "make it actually usable and slightly less cursed" list for getting ShortSplit to a shareable 1.0 state.

---

## 🧠 Core Functionality

- [ ] Drag-and-drop reliably processes both top and bottom clips
- [ ] Subtitle burning (ASS) into top clip works cleanly with user styling
- [ ] Bottom clip aligns/loops/trims to match top clip duration
- [ ] Audio only comes from top clip and is volume-normalized
- [ ] Output saves correctly and consistently (default + manual paths)
- [ ] GPU fallback to CPU works without crashing
- [ ] FFmpeg errors and subprocess issues are caught and logged

---

## 🖥️ UI/UX Polishing

- [ ] Clear labeling for top (voice) and bottom (visual) clip inputs
- [ ] Progress/status updates shown during processing
- [ ] Light/dark mode toggle (even a dummy one is fine)
- [ ] Remember last used files and settings
- [ ] "Create" button triggers complete render chain, with feedback

---

## ⚙️ Settings and Configuration

- [ ] Optional subtitle styling: font, size, outline
- [ ] Whisper model size + device setting visible/configurable
- [ ] (Optional) Output resolution toggle or presets

---

## 🚨 Error Handling

- [ ] Missing FFmpeg = helpful error message
- [ ] No GPU = fallback to CPU without tears
- [ ] Empty top audio = warning but still renders (with empty subs?)
- [ ] File type validation for dropped inputs

---

## 📦 Packaging and Delivery

- [ ] `requirements.txt` is accurate and up-to-date
- [ ] README includes simple usage guide (drag-drop > click > profit)
- [ ] CLI option documented for terminal enjoyers
- [ ] PyInstaller build script for lazy end users (optional but nice)
- [ ] Version tag (0.9 or 1.0 depending on confidence)

---

## 🎨 Flavor and Personality
- [ ] loading animation or quote-of-the-day just for vibe

---

Built by Dyhrrr at 2 a.m. and morally supported by existential dread and caffeine.

