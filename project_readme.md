# 🪔 Happy Diwali 2026 - Cinematic Python Animation

A realistic, cinematic Diwali celebration animation written in pure Python using `pygame` and `numpy`. No external assets (images/audio files) are required!

![Diwali Animation](https://img.shields.io/badge/Language-Python3-blue.svg)
![Library-Pygame-green.svg](https://img.shields.io/badge/Library-Pygame-green.svg)

---

## ✨ Features
- **Night Sky & City Skyline:** Amavasya night with twinkling stars and glowing temple shikhara.
- **Dynamic Rangoli Generation:** Procedurally generated rangoli pattern appearing automatically on the floor.
- **Flickering Diyas:** 18 individual diyas lighting up sequentially with realistic flame animations.
- **Realistic Fireworks:** 7 unique types of firework shell blasts (Peony, Chrysanthemum, Willow, Ring, Palm, Crackle, Double-Break).
- **Custom Fireworks Text:** High-definition particle formation spelling **"HAPPY DIWALI ALL OF YOU"**.
- **Real-time Audio Synthesis:** Sound effects generated entirely using `numpy` math (booms, whistles, crackles) with stereo panning.
- **Video Recording Support:** Ability to export animation directly to an MP4 video reel.

---

## 🛠️ Prerequisites & Installation

Make sure you have **Python 3.8+** installed on your system.

Install required dependencies using pip:

```bash
pip install pygame numpy
```

*(Optional) For recording video reels:*
```bash
pip install imageio imageio-ffmpeg
```

---

## 🚀 How to Run

1. Open your terminal / PowerShell.
2. Navigate to your project folder:
   ```bash
   cd path/to/Diwali_Animation_2026
   ```
3. Run the Python script:
   ```bash
   python diwali_2026.py
   ```

---

## 🎮 Controls

| Key | Action |
| :--- | :--- |
| `SPACE` | Restart Animation |
| `R` | Launch Extra Rocket Volley |
| `M` | Mute / Unmute Audio |
| `ESC` | Quit Animation |

---

## 📹 How to Record a Video Reel

To record a 60-second video reel (9:16 aspect ratio):

```bash
python diwali_2026.py --record diwali_reel.mp4 --seconds 60
```

For HD Quality (1080x1920):
```bash
python diwali_2026.py --record diwali_reel.mp4 --w 1080 --h 1920 --seconds 60
```

---

## 👤 Author
* **Coding with Vishesh** - [@codingwithvishesh](https://instagram.com/codingwithvishesh)