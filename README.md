# 🎣 FishBot Pro — Pixel Detection Fishing Macro

A lightweight, pixel-detection fishing automation tool for Minecraft (and similar games). Monitors a specific pixel on screen and automatically re-casts your rod when the bobber dips.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)

---

## 📸 Features

- 🖥 **Always-on-top GUI** — stays visible while you watch the game
- 🎯 **3-second countdown** to capture mouse position with one click
- 🎨 **Live colour sampler** — reads the exact pixel colour at your coordinates
- ⚙️ **Adjustable colour tolerance** (±N per RGB channel)
- 📋 **Activity log** with timestamps
- 🛑 **PyAutoGUI FailSafe** — move mouse to top-left corner to emergency stop
- 🧵 **Non-blocking** — macro runs on a background thread; GUI stays responsive

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/fishbot-pro.git
cd fishbot-pro
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
python fishing_macro.py
```

---

## 📖 How to Use

### Step 1 — Find the right pixel

Cast your fishing rod and watch the bobber on screen. Pick a pixel **on or very near the bobber** — ideally one that changes colour noticeably when the bobber dips.

### Step 2 — Capture coordinates

1. Click **"🖱 Get Mouse Position"**
2. You have **3 seconds** — move your cursor over the bobber pixel
3. The X, Y fields are filled automatically

### Step 3 — Sample the target colour

> The bobber is **in the water (not dipped)** at this point.

1. Make sure coordinates are set from Step 2
2. Click **"🎨 Get Colour Under Mouse"**
3. The RGB fields and colour swatch update instantly

### Step 4 — Set tolerance

The default **±15** per channel works for most situations. Increase it if the macro misses dips; decrease it to reduce false triggers.

### Step 5 — Start

1. Cast your rod in-game
2. Click **"▶ START MACRO"**

The macro will now:
1. Watch the pixel every 50 ms
2. When the colour matches → **right-click** (reel in)
3. Wait **0.5 s**
4. **Right-click** again (re-cast)
5. Wait **3 s** (bobber settle cooldown)
6. Repeat

Click **"■ STOP MACRO"** at any time to stop.

---

## ⚠️ Emergency Stop

Move your mouse to the **top-left corner** of your screen. PyAutoGUI's FailSafe will trigger and halt the macro immediately.

---

## 🗂 File Structure

```
fishbot-pro/
├── fishing_macro.py   ← Main script
├── requirements.txt   ← Python dependencies
└── README.md          ← This file
```

---

## 📦 Requirements

| Package      | Purpose                          |
|-------------|----------------------------------|
| `pyautogui` | Mouse clicks & screen pixel read |
| `pillow`    | Screenshot support (pyautogui dep)|
| `tkinter`   | GUI — built into Python ≥ 3.1    |

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| `pip install pyautogui` fails | Try `pip install pyautogui pillow` |
| Macro never triggers | Lower the tolerance or re-sample the colour |
| Macro triggers too often | Raise the tolerance value |
| Screen is black on macOS | Grant **Screen Recording** permission in System Preferences → Privacy |
| `pyautogui.pixel` crashes | Make sure coordinates are inside screen bounds |

---

## 📄 License

MIT — free to use, modify, and share.
