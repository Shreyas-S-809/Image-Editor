# 🎨 AI Image Editor (Offline)

A lightweight, privacy-friendly image editor built with Streamlit and Python.  
Edit images directly in your browser — no login, no API keys, no data collection.

---

## ✨ Features

- Upload and edit images (JPG, PNG, WEBP)
- Brightness, Contrast, Saturation, Sharpness controls
- Crop, Resize, Rotate, Flip
- Filters: Blur, Sharpen, Emboss, Smooth, and more
- Text overlay with custom font, position, and color
- Before vs After live preview
- Undo & Reset support
- Download edited images (PNG / JPG)
- **Offline AI tools**: Background removal, Denoising, Edge detection
- No internet needed (offline version)
- No API keys required
- Works on low-resource machines

---

## 🌐 Online Version (Light Mode)

> Best for quick edits — runs in your browser via Streamlit Cloud.


- Lightweight and fast
- Basic editing: adjust, transform, filter, text overlay
- No installation required
- Works on any device with a browser

🔗 **[Open Live App](#)** *((https://image-editor-ys.streamlit.app/))*

---

## 💻 Offline Version (Advanced Mode)

> Full-featured editor with AI tools — runs locally on your machine.

Everything in the online version, plus:

- **AI Background Removal** (rembg / U2Net)
- **Image Denoising** (OpenCV)
- **Edge Detection** (Canny)
- **Advanced Filters**: Vintage, Cartoon, Sketch, Stylize, Auto Enhance
- **Multi-step Undo** (up to 10 steps)
- **Histogram Visualization**
- **Batch Processing** (edit multiple images at once)
- **Drawing Tool** with brush size and color

No internet connection required. All processing happens on your machine.

---

## 🚀 Installation (Offline Version)

### Prerequisites

- Python 3.9 or higher
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Shreyas-S-809/Image-Editor
cd image-editor/offline

# 2. Create a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 📖 Usage

1. **Upload** an image using the sidebar
2. **Edit** using the tabbed controls (Adjust, Transform, Filters, etc.)
3. **Preview** changes in real-time (Before vs After)
4. **Apply** to bake edits, or **Undo** / **Reset** anytime
5. **Download** the edited image in PNG or JPG

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Streamlit | Web UI framework |
| Pillow (PIL) | Image processing |
| OpenCV | Advanced filters & AI effects |
| NumPy | Array operations |
| rembg | AI background removal |

---

## 📁 Project Structure

```
Image Editor/
├── Offline/                # Offline (Advanced) version
│   ├── app.py
│   └── requirements.txt
└── README.md
```

---

## 📌 Important Notes

- **No API keys** needed — everything runs locally
- **No data leaves your machine** in offline mode
- **Optimized** for systems with 8 GB RAM or less
- Large images are **auto-downscaled** to prevent crashes
- AI model (U2Net) downloads once on first use, then works offline

---
> Built with ❤️ using Python and Streamlit
