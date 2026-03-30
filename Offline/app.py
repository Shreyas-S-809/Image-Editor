import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
from io import BytesIO
import numpy as np
import cv2

# ════════════════════════════════════════════════
# Page Configuration
# ════════════════════════════════════════════════
st.set_page_config(page_title="Image Editor · Offline", page_icon="🎨", layout="wide")

# ════════════════════════════════════════════════
# Constants
# ════════════════════════════════════════════════
MAX_WIDTH = 1500
MAX_PIXELS = 1500 * 1500  # safety cap for AI ops
SUPPORTED_FORMATS = ["jpg", "jpeg", "png", "webp"]
FILTER_LIST = ["None", "Blur", "Sharpen", "Emboss", "Smooth", "Edge Enhance", "Detail"]
MAX_UNDO = 10


# ════════════════════════════════════════════════
# Utility helpers
# ════════════════════════════════════════════════
def constrain_image(img, max_width=MAX_WIDTH):
    """Down-scale if wider than max_width, keep aspect ratio."""
    if img.width > max_width:
        ratio = max_width / img.width
        return img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    return img.copy()


def pil_to_cv(img):
    """PIL Image → OpenCV BGR numpy array."""
    if img.mode == "RGBA":
        arr = np.array(img.convert("RGB"))
    else:
        arr = np.array(img.convert("RGB"))
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def cv_to_pil(arr):
    """OpenCV BGR array → PIL RGB Image."""
    return Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))


def safe_downscale(img, max_pixels=MAX_PIXELS):
    """Downscale for heavy ops if image exceeds pixel budget."""
    w, h = img.size
    if w * h > max_pixels:
        ratio = (max_pixels / (w * h)) ** 0.5
        new_w, new_h = int(w * ratio), int(h * ratio)
        return img.resize((new_w, new_h), Image.LANCZOS), True
    return img, False


def get_image_bytes(img, fmt="PNG", quality=95):
    buf = BytesIO()
    if fmt == "JPEG":
        img = img.convert("RGB")
        img.save(buf, format="JPEG", quality=quality)
    else:
        img.save(buf, format="PNG")
    buf.seek(0)
    return buf


# ════════════════════════════════════════════════
# Image processing functions
# ════════════════════════════════════════════════
def apply_adjustments(img, brightness, contrast, saturation, sharpness):
    if brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brightness)
    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    if saturation != 1.0:
        img = ImageEnhance.Color(img).enhance(saturation)
    if sharpness != 1.0:
        img = ImageEnhance.Sharpness(img).enhance(sharpness)
    return img


def apply_filter(img, filter_name):
    filters = {
        "Blur": ImageFilter.GaussianBlur(2),
        "Sharpen": ImageFilter.SHARPEN,
        "Emboss": ImageFilter.EMBOSS,
        "Smooth": ImageFilter.SMOOTH_MORE,
        "Edge Enhance": ImageFilter.EDGE_ENHANCE,
        "Detail": ImageFilter.DETAIL,
    }
    f = filters.get(filter_name)
    if f is None:
        return img
    if img.mode == "RGBA":
        rgb = img.convert("RGB").filter(f)
        r, g, b = rgb.split()
        return Image.merge("RGBA", (r, g, b, img.split()[3]))
    return img.filter(f)


def draw_text_on_image(img, text, x, y, size, color):
    overlay = img.copy()
    draw = ImageDraw.Draw(overlay)
    try:
        font = ImageFont.truetype("arial.ttf", size)
    except OSError:
        font = ImageFont.load_default()
    draw.text((x, y), text, fill=color, font=font)
    return overlay


# ── OpenCV-based effects ──
def cv_denoise(img, strength=10):
    arr = pil_to_cv(img)
    denoised = cv2.fastNlMeansDenoisingColored(arr, None, strength, strength, 7, 21)
    return cv_to_pil(denoised)


def cv_canny_edges(img, low=50, high=150):
    arr = pil_to_cv(img)
    gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, low, high)
    return Image.fromarray(edges)


def cv_cartoon(img):
    arr = pil_to_cv(img)
    gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(arr, 9, 300, 300)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cv_to_pil(cartoon)


def cv_sketch(img):
    arr = pil_to_cv(img)
    gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    inv = 255 - gray
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blur, scale=256)
    return Image.fromarray(sketch)


def cv_stylize(img):
    arr = pil_to_cv(img)
    stylized = cv2.stylization(arr, sigma_s=60, sigma_r=0.07)
    return cv_to_pil(stylized)


def auto_enhance(img):
    """Smart auto-enhancement: histogram equalize via OpenCV then sharpen."""
    arr = pil_to_cv(img)
    lab = cv2.cvtColor(arr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    pil_img = cv_to_pil(result)
    pil_img = ImageEnhance.Sharpness(pil_img).enhance(1.3)
    return pil_img


def vintage_filter(img):
    arr = np.array(img.convert("RGB")).astype(np.float64)
    # sepia matrix
    sepia = np.array([[0.393, 0.769, 0.189],
                      [0.349, 0.686, 0.168],
                      [0.272, 0.534, 0.131]])
    result = arr @ sepia.T
    result = np.clip(result, 0, 255).astype(np.uint8)
    return Image.fromarray(result)


def high_contrast(img):
    arr = pil_to_cv(img)
    lab = cv2.cvtColor(arr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.equalizeHist(l)
    lab = cv2.merge([l, a, b])
    return cv_to_pil(cv2.cvtColor(lab, cv2.COLOR_LAB2BGR))


def grayscale_intensity(img, intensity=1.0):
    gray = img.convert("L")
    if intensity >= 1.0:
        return gray.convert(img.mode)
    return Image.blend(img.convert("RGB"), gray.convert("RGB"), intensity)


# ── Background Removal (lazy-loaded) ──
@st.cache_resource(show_spinner=False)
def load_rembg_session():
    """Load rembg session once and cache it."""
    from rembg import new_session
    return new_session("u2net")


def remove_background(img):
    from rembg import remove
    session = load_rembg_session()
    return remove(img, session=session)


# ────────────────────────────────────────────────────
# Histogram helper
# ────────────────────────────────────────────────────
def compute_histogram_image(img, width=300, height=200):
    """Render an RGB histogram as a PIL image (lightweight, no matplotlib)."""
    arr = np.array(img.convert("RGB"))
    hist_img = Image.new("RGB", (width, height), (30, 30, 30))
    draw = ImageDraw.Draw(hist_img)
    colors = [(220, 60, 60), (60, 180, 60), (60, 100, 220)]
    for ch, color in enumerate(colors):
        hist = cv2.calcHist([arr], [ch], None, [256], [0, 256]).flatten()
        max_val = hist.max() if hist.max() > 0 else 1
        hist = hist / max_val * (height - 10)
        step = width / 256
        for i in range(1, 256):
            x0 = int((i - 1) * step)
            y0 = height - int(hist[i - 1])
            x1 = int(i * step)
            y1 = height - int(hist[i])
            draw.line([(x0, y0), (x1, y1)], fill=color, width=1)
    return hist_img


# ════════════════════════════════════════════════
# Session state
# ════════════════════════════════════════════════
DEFAULTS = {
    "brightness": 1.0, "contrast": 1.0, "saturation": 1.0, "sharpness": 1.0,
    "rotation": 0, "flip_h": False, "flip_v": False, "filter_name": "None",
    "crop_left": 0, "crop_top": 0, "crop_right": 0, "crop_bottom": 0,
    "resize_w": 0, "resize_h": 0, "lock_aspect": True,
    "txt": "", "txt_x": 10, "txt_y": 10, "txt_size": 24, "txt_color": "#FFFFFF",
    "adv_filter": "None",
    "gray_intensity": 1.0,
    "denoise_strength": 10,
    "canny_low": 50, "canny_high": 150,
    "draw_points": [],
    "draw_color": "#FF0000",
    "draw_size": 5,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

if "original" not in st.session_state:
    st.session_state.original = None
if "undo_stack" not in st.session_state:
    st.session_state.undo_stack = []
if "_fname" not in st.session_state:
    st.session_state._fname = ""
if "ai_result" not in st.session_state:
    st.session_state.ai_result = None
if "ai_action" not in st.session_state:
    st.session_state.ai_action = None


def push_undo(img):
    stack = st.session_state.undo_stack
    # Keep thumbnails to save RAM
    thumb = img.copy()
    if thumb.width > 800:
        ratio = 800 / thumb.width
        thumb = thumb.resize((800, int(thumb.height * ratio)), Image.LANCZOS)
    stack.append(thumb)
    if len(stack) > MAX_UNDO:
        stack.pop(0)


def pop_undo():
    if st.session_state.undo_stack:
        return st.session_state.undo_stack.pop()
    return None


def reset_controls():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v
    if st.session_state.original:
        st.session_state.resize_w = st.session_state.original.width
        st.session_state.resize_h = st.session_state.original.height
    st.session_state.ai_result = None
    st.session_state.ai_action = None


# ════════════════════════════════════════════════
# Build edited image pipeline
# ════════════════════════════════════════════════
def build_edited(src):
    img = src.copy()
    w, h = img.size

    # Crop
    cl, ct, cr, cb = (st.session_state.crop_left, st.session_state.crop_top,
                       st.session_state.crop_right, st.session_state.crop_bottom)
    if cl + cr < w and ct + cb < h:
        img = img.crop((cl, ct, w - cr, h - cb))

    # Resize
    rw, rh = st.session_state.resize_w, st.session_state.resize_h
    if rw > 0 and rh > 0 and (rw, rh) != img.size:
        img = img.resize((rw, rh), Image.LANCZOS)

    # Rotate
    if st.session_state.rotation:
        fill = (0, 0, 0, 0) if img.mode == "RGBA" else (0, 0, 0)
        img = img.rotate(st.session_state.rotation, expand=True, fillcolor=fill)

    # Flip
    if st.session_state.flip_h:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if st.session_state.flip_v:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

    # Adjustments
    img = apply_adjustments(img, st.session_state.brightness, st.session_state.contrast,
                            st.session_state.saturation, st.session_state.sharpness)

    # Basic filter
    img = apply_filter(img, st.session_state.filter_name)

    # Advanced filter
    adv = st.session_state.adv_filter
    if adv == "Vintage":
        img = vintage_filter(img)
    elif adv == "High Contrast":
        img = high_contrast(img)
    elif adv == "Grayscale":
        img = grayscale_intensity(img, st.session_state.gray_intensity)
    elif adv == "Cartoon":
        img = cv_cartoon(img)
    elif adv == "Sketch":
        img = cv_sketch(img)
    elif adv == "Stylize":
        img = cv_stylize(img)
    elif adv == "Auto Enhance":
        img = auto_enhance(img)

    # Text overlay
    txt = st.session_state.txt.strip()
    if txt:
        img = draw_text_on_image(img, txt, st.session_state.txt_x,
                                  st.session_state.txt_y, st.session_state.txt_size,
                                  st.session_state.txt_color)

    # Simple drawing (points list)
    if st.session_state.draw_points:
        draw = ImageDraw.Draw(img)
        r = st.session_state.draw_size
        clr = st.session_state.draw_color
        for px, py in st.session_state.draw_points:
            draw.ellipse([px - r, py - r, px + r, py + r], fill=clr)

    return img


# ════════════════════════════════════════════════
# Sidebar
# ════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🎨 Image Editor")
    st.markdown("---")

    uploaded = st.file_uploader("Upload Image", type=SUPPORTED_FORMATS)

    if uploaded:
        if uploaded.name != st.session_state._fname:
            img = constrain_image(Image.open(uploaded))
            st.session_state.original = img
            st.session_state._fname = uploaded.name
            st.session_state.undo_stack = []
            reset_controls()

        orig = st.session_state.original

        # Metadata
        with st.expander("📋 Image Info", expanded=False):
            st.write(f"**Size:** {orig.width} × {orig.height} px")
            st.write(f"**Mode:** {orig.mode}")
            st.write(f"**File:** {uploaded.name}")
            pixels = orig.width * orig.height
            st.write(f"**Pixels:** {pixels:,}")
            if pixels > MAX_PIXELS:
                st.warning("Large image — AI tools will auto-downscale.")

        # ── Tabs ──
        tab_adj, tab_trans, tab_filt, tab_draw, tab_ai, tab_exp = st.tabs(
            ["⚙ Adjust", "🔄 Transform", "✨ Filters", "✏ Draw/Text", "🤖 AI Tools", "💾 Export"]
        )

        # ── Adjustments ──
        with tab_adj:
            st.session_state.brightness = st.slider("Brightness", 0.2, 3.0, st.session_state.brightness, 0.05)
            st.session_state.contrast = st.slider("Contrast", 0.2, 3.0, st.session_state.contrast, 0.05)
            st.session_state.saturation = st.slider("Saturation", 0.0, 3.0, st.session_state.saturation, 0.05)
            st.session_state.sharpness = st.slider("Sharpness", 0.0, 3.0, st.session_state.sharpness, 0.05)

        # ── Transform ──
        with tab_trans:
            st.session_state.rotation = st.slider("Rotate (°)", -180, 180, st.session_state.rotation, 1)
            c1, c2 = st.columns(2)
            st.session_state.flip_h = c1.checkbox("Flip H", st.session_state.flip_h)
            st.session_state.flip_v = c2.checkbox("Flip V", st.session_state.flip_v)

            st.markdown("##### ✂ Crop (px from edge)")
            ow, oh = orig.size
            c1, c2 = st.columns(2)
            st.session_state.crop_left = c1.number_input("Left", 0, ow - 1, st.session_state.crop_left, key="cl")
            st.session_state.crop_right = c2.number_input("Right", 0, ow - 1, st.session_state.crop_right, key="cr")
            st.session_state.crop_top = c1.number_input("Top", 0, oh - 1, st.session_state.crop_top, key="ct")
            st.session_state.crop_bottom = c2.number_input("Bottom", 0, oh - 1, st.session_state.crop_bottom, key="cb")

            st.markdown("##### 📐 Resize")
            st.session_state.lock_aspect = st.checkbox("Lock aspect ratio", st.session_state.lock_aspect)
            new_w = st.number_input("Width", 1, 4096, st.session_state.resize_w, key="rw")
            if st.session_state.lock_aspect and new_w != st.session_state.resize_w and st.session_state.resize_w > 0:
                ratio = new_w / st.session_state.resize_w
                st.session_state.resize_h = max(1, int(st.session_state.resize_h * ratio))
            st.session_state.resize_w = new_w
            st.session_state.resize_h = st.number_input("Height", 1, 4096, st.session_state.resize_h, key="rh")

        # ── Filters ──
        with tab_filt:
            st.markdown("**Basic Filters**")
            st.session_state.filter_name = st.radio(
                "Basic", FILTER_LIST,
                index=FILTER_LIST.index(st.session_state.filter_name), label_visibility="collapsed"
            )
            st.markdown("---")
            st.markdown("**Advanced Filters**")
            adv_list = ["None", "Vintage", "High Contrast", "Grayscale", "Cartoon", "Sketch", "Stylize", "Auto Enhance"]
            st.session_state.adv_filter = st.radio(
                "Advanced", adv_list,
                index=adv_list.index(st.session_state.adv_filter), label_visibility="collapsed"
            )
            if st.session_state.adv_filter == "Grayscale":
                st.session_state.gray_intensity = st.slider("Intensity", 0.0, 1.0, st.session_state.gray_intensity, 0.05)

        # ── Drawing & Text ──
        with tab_draw:
            st.markdown("**Text Overlay**")
            st.session_state.txt = st.text_input("Text", st.session_state.txt)
            c1, c2 = st.columns(2)
            st.session_state.txt_x = c1.number_input("X", 0, 4096, st.session_state.txt_x, key="tx")
            st.session_state.txt_y = c2.number_input("Y", 0, 4096, st.session_state.txt_y, key="ty")
            st.session_state.txt_size = st.slider("Font size", 8, 120, st.session_state.txt_size)
            st.session_state.txt_color = st.color_picker("Text color", st.session_state.txt_color)

            st.markdown("---")
            st.markdown("**Drawing**")
            st.session_state.draw_color = st.color_picker("Brush color", st.session_state.draw_color, key="dc")
            st.session_state.draw_size = st.slider("Brush size", 1, 30, st.session_state.draw_size)
            c1, c2 = st.columns(2)
            dx = c1.number_input("Point X", 0, 4096, 0, key="dx")
            dy = c2.number_input("Point Y", 0, 4096, 0, key="dy")
            if st.button("Add point", use_container_width=True):
                st.session_state.draw_points.append((dx, dy))
                st.rerun()
            if st.button("Clear drawing", use_container_width=True):
                st.session_state.draw_points = []
                st.rerun()

        # ── AI Tools ──
        with tab_ai:
            st.markdown("**AI-Powered Tools** (runs locally)")
            ai_choice = st.radio(
                "Select tool", ["None", "Remove Background", "Denoise", "Edge Detection"],
                key="ai_radio"
            )

            if ai_choice == "Denoise":
                st.session_state.denoise_strength = st.slider("Denoise strength", 1, 30, st.session_state.denoise_strength)

            if ai_choice == "Edge Detection":
                st.session_state.canny_low = st.slider("Low threshold", 10, 200, st.session_state.canny_low)
                st.session_state.canny_high = st.slider("High threshold", 50, 300, st.session_state.canny_high)

            if ai_choice != "None":
                if st.button(f"▶ Run {ai_choice}", use_container_width=True):
                    st.session_state.ai_action = ai_choice

        # ── Export ──
        with tab_exp:
            dl_fmt = st.selectbox("Format", ["PNG", "JPEG"])
            dl_quality = 95
            if dl_fmt == "JPEG":
                dl_quality = st.slider("Quality", 10, 100, 95, 5)

        # ── Action buttons ──
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("↩ Undo", use_container_width=True):
                prev = pop_undo()
                if prev is not None:
                    st.session_state.original = prev
                    reset_controls()
                    st.rerun()
        with c2:
            if st.button("🔄 Reset", use_container_width=True):
                reset_controls()
                st.rerun()
        with c3:
            if st.button("✅ Apply", use_container_width=True, help="Bake edits into image"):
                push_undo(st.session_state.original)
                st.session_state.original = build_edited(st.session_state.original)
                reset_controls()
                st.rerun()

        # Undo stack info
        stack_len = len(st.session_state.undo_stack)
        if stack_len:
            st.caption(f"Undo history: {stack_len} step{'s' if stack_len > 1 else ''}")

    # ── Batch processing ──
    st.markdown("---")
    with st.expander("📦 Batch Processing", expanded=False):
        batch_files = st.file_uploader("Upload multiple images", type=SUPPORTED_FORMATS,
                                        accept_multiple_files=True, key="batch")
        if batch_files:
            batch_fmt = st.selectbox("Batch format", ["PNG", "JPEG"], key="b_fmt")
            batch_q = 95
            if batch_fmt == "JPEG":
                batch_q = st.slider("Batch quality", 10, 100, 95, 5, key="b_q")
            batch_action = st.selectbox("Batch action", ["Auto Enhance", "Grayscale", "Vintage", "Denoise"], key="b_act")

            if st.button("Process batch", use_container_width=True):
                st.session_state._batch_results = []
                progress = st.progress(0)
                for idx, bf in enumerate(batch_files):
                    bimg = constrain_image(Image.open(bf))
                    if batch_action == "Auto Enhance":
                        bimg = auto_enhance(bimg)
                    elif batch_action == "Grayscale":
                        bimg = bimg.convert("L").convert("RGB")
                    elif batch_action == "Vintage":
                        bimg = vintage_filter(bimg)
                    elif batch_action == "Denoise":
                        bimg = cv_denoise(bimg)
                    buf = get_image_bytes(bimg, batch_fmt, batch_q)
                    ext = "png" if batch_fmt == "PNG" else "jpg"
                    st.session_state._batch_results.append((f"{bf.name.rsplit('.', 1)[0]}_edited.{ext}", buf, ext))
                    progress.progress((idx + 1) / len(batch_files))
                st.success(f"Processed {len(batch_files)} images!")

            if "_batch_results" in st.session_state and st.session_state._batch_results:
                for fname, buf, ext in st.session_state._batch_results:
                    st.download_button(f"⬇ {fname}", buf, file_name=fname,
                                        mime=f"image/{ext}", key=f"dl_{fname}")


# ════════════════════════════════════════════════
# Main area
# ════════════════════════════════════════════════
st.markdown(
    "<h2 style='text-align:center;'>🖼️ Image Editor "
    "<span style='font-size:0.5em;color:#888;'>Offline · Advanced</span></h2>",
    unsafe_allow_html=True,
)

if st.session_state.original is None:
    st.markdown("---")
    st.info("👈 Upload an image from the sidebar to get started.")
else:
    # ── Run AI action if requested ──
    if st.session_state.ai_action:
        action = st.session_state.ai_action
        st.session_state.ai_action = None
        work_img = build_edited(st.session_state.original)
        work_img, was_scaled = safe_downscale(work_img)

        with st.spinner(f"Running {action}..."):
            if action == "Remove Background":
                result = remove_background(work_img)
            elif action == "Denoise":
                result = cv_denoise(work_img, st.session_state.denoise_strength)
            elif action == "Edge Detection":
                result = cv_canny_edges(work_img, st.session_state.canny_low, st.session_state.canny_high)
            else:
                result = work_img

        st.session_state.ai_result = result
        if was_scaled:
            st.warning("Image was downscaled for processing to save memory.")

    edited = build_edited(st.session_state.original)

    # Before / After
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Original**")
        st.image(st.session_state.original)
    with col_b:
        st.markdown("**Edited**")
        st.image(edited)

    # AI result display
    if st.session_state.ai_result is not None:
        st.markdown("---")
        st.markdown("**🤖 AI Result**")
        ai_c1, ai_c2 = st.columns([3, 1])
        with ai_c1:
            st.image(st.session_state.ai_result)
        with ai_c2:
            if st.button("✅ Use AI result as image", use_container_width=True):
                push_undo(st.session_state.original)
                ai_img = st.session_state.ai_result
                if ai_img.mode == "L":
                    ai_img = ai_img.convert("RGB")
                st.session_state.original = ai_img
                st.session_state.ai_result = None
                reset_controls()
                st.rerun()
            if st.button("❌ Discard AI result", use_container_width=True):
                st.session_state.ai_result = None
                st.rerun()

    # Histogram
    st.markdown("---")
    with st.expander("📊 Histogram", expanded=False):
        hist_img = compute_histogram_image(edited)
        st.image(hist_img, caption="RGB Histogram")

    # Download
    st.markdown("---")
    dc1, dc2 = st.columns([1, 2])
    with dc1:
        d_fmt = st.selectbox("Download as", ["PNG", "JPEG"], key="d_fmt")
        d_q = 95
        if d_fmt == "JPEG":
            d_q = st.slider("JPG quality", 10, 100, 95, 5, key="d_q")
    with dc2:
        buf = get_image_bytes(edited, d_fmt, d_q)
        ext = "png" if d_fmt == "PNG" else "jpg"
        st.download_button(f"⬇ Download .{ext}", buf, file_name=f"edited.{ext}",
                            mime=f"image/{ext}", use_container_width=True)
