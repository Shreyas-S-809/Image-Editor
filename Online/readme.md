# 🎨 Image Editor — Online (Light Mode)

A clean, lightweight image editor that runs directly in your browser.  
No installation, no login, no API keys — just upload and edit.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)


🔗 **[Open Live App](#)** *((https://image-editor-ys.streamlit.app/))*


---

## ✨ Features

- Upload images (JPG, PNG, WEBP)
- Brightness, Contrast, Saturation, Sharpness sliders
- Crop (numeric input from each edge)
- Resize with aspect ratio lock
- Rotate and Flip (horizontal / vertical)
- Filters: Blur, Sharpen, Emboss, Smooth, Edge Enhance, Detail
- Text overlay with custom position, size, and color
- Before vs After live preview
- 1-step Undo and full Reset
- Download as PNG or JPG with quality control
- No data stored — your images stay private
- All the images which you upload and edit will be stored in cache memory of browser.

---

## 🚀 Quick Start (Local)

If you want to run it locally instead of using the cloud version:

```bash
# 1. Clone the repo
git clone https://github.com/Shreyas-S-809/Image-Editor
cd image-editor/onlne

# 2. Create a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
streamlit run app.py
```

Opens at `http://localhost:8501`.

---

## 📖 Usage

1. **Upload** an image from the sidebar
2. **Edit** using the sidebar tabs — Adjust, Transform, Filters, Text, Export
3. **Preview** changes instantly (Before vs After)
4. **Apply** to bake edits, **Undo** to go back, or **Reset** to start over
5. **Download** your edited image

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Streamlit | Web UI framework |
| Pillow (PIL) | Image processing |

---

## 📁 Project Structure

```
Online/
├── app.py              # Complete application
├── requirements.txt    # Dependencies
└── README.md
```

---

## 📌 Notes

- Designed for **Streamlit Cloud free tier** (low RAM, no GPU)
- Large images are auto-constrained to 1200px width
- No external APIs or AI models used
- Fully stateless — nothing is saved on the server
- Works on any device with a modern browser

---

## 💻 Want More Features?

Check out the **[Offline Advanced Version](../Offline/)** — includes AI background removal, denoising, batch processing, advanced filters, and more.

---

> Built with ❤️ using Python and Streamlit
