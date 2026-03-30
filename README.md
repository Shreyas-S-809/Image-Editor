# 🎨 AI Image Editor

[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Pillow](https://img.shields.io/badge/Pillow-Image_Processing-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python-pillow.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![NumPy](https://img.shields.io/badge/NumPy-Scientific_Computing-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org)
[![rembg](https://img.shields.io/badge/rembg-Background_Removal-00C7B7?style=for-the-badge)](https://github.com/danielgatis/rembg)

A Streamlit-based image editor available in two modes — a lightweight online version for quick browser-based edits, and a powerful offline version with AI features that runs entirely on your local machine.

No login. No API keys. No data collection.

---

## 🌐 Online Version — Light Mode

Runs in the browser via Streamlit Cloud. No installation needed.

**Features:** Upload images · Brightness / Contrast / Saturation / Sharpness · Crop · Resize · Rotate · Flip · Filters · Text overlay · Undo & Reset · Download PNG/JPG

🔗 **[Open Live App](#)** *((https://image-editor-ys.streamlit.app/))*
📂 [`Onlne/`](./Online/)

---

## 💻 Offline Version — Advanced Mode

Runs locally with no internet required. Includes everything in the online version plus:

**AI Tools:** Background removal (rembg) · Denoising (OpenCV) · Edge detection (Canny)  
**Extra Features:** Cartoon / Sketch / Stylize effects · Vintage & High Contrast filters · Auto Enhance · Multi-step undo · Histogram · Batch processing · Drawing tool

📂 [`Offline/`](./Offline/)

### Quick Start

```bash

git clone https://github.com/Shreyas-S-809/Image-Editor
cd offline
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
streamlit run app.py
```

---

## 📁 Project Structure

```
Image Editor/
├── onlne/              # Online (Light) version
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
├── offline/            # Offline (Advanced) version
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
└── README.md
```

---

## 🛠️ Tech Stack

Streamlit · Pillow · OpenCV · NumPy · rembg

---

## 📄 License

Open source under the [MIT License](LICENSE).

## End Note


- Cold start for online version : 
- Since it has been deployed in streamlit if there are no active users for more than 15 minutes
- It will go to sleep.
- So for stability, go with offline version it works better.
- If you found any issues, happy to hear it from PR
- Thank you.