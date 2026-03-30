import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
from io import BytesIO

st.set_page_config(page_title="Image Editor", page_icon="\U0001F3A8", layout="wide")

MAX_WIDTH = 1200
SUPPORTED_FORMATS = ["jpg", "jpeg", "png", "webp"]
FILTER_LIST = ["None", "Blur", "Sharpen", "Emboss", "Smooth", "Edge Enhance", "Detail"]


def constrain_image(img, max_width=MAX_WIDTH):
    if img.width > max_width:
        ratio = max_width / img.width
        return img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    return img.copy()


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


def get_image_bytes(img, fmt="PNG", quality=95):
    buf = BytesIO()
    if fmt == "JPEG":
        img = img.convert("RGB")
        img.save(buf, format="JPEG", quality=quality)
    else:
        img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def draw_text_on_image(img, text, x, y, size, color):
    overlay = img.copy()
    draw = ImageDraw.Draw(overlay)
    try:
        font = ImageFont.truetype("arial.ttf", size)
    except OSError:
        font = ImageFont.load_default()
    draw.text((x, y), text, fill=color, font=font)
    return overlay


# Session state defaults
DEFAULTS = {
    "brightness": 1.0, "contrast": 1.0, "saturation": 1.0, "sharpness": 1.0,
    "rotation": 0, "flip_h": False, "flip_v": False, "filter_name": "None",
    "crop_left": 0, "crop_top": 0, "crop_right": 0, "crop_bottom": 0,
    "resize_w": 0, "resize_h": 0, "lock_aspect": True,
    "txt": "", "txt_x": 10, "txt_y": 10, "txt_size": 24, "txt_color": "#FFFFFF",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v
for k in ["original", "undo_img"]:
    if k not in st.session_state:
        st.session_state[k] = None
if "_fname" not in st.session_state:
    st.session_state._fname = ""


def reset_controls():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v
    if st.session_state.original:
        st.session_state.resize_w = st.session_state.original.width
        st.session_state.resize_h = st.session_state.original.height
    st.session_state.undo_img = None


def build_edited(src):
    img = src.copy()
    w, h = img.size
    cl, ct, cr, cb = st.session_state.crop_left, st.session_state.crop_top, st.session_state.crop_right, st.session_state.crop_bottom
    if cl + cr < w and ct + cb < h:
        img = img.crop((cl, ct, w - cr, h - cb))
    rw, rh = st.session_state.resize_w, st.session_state.resize_h
    if rw > 0 and rh > 0 and (rw, rh) != img.size:
        img = img.resize((rw, rh), Image.LANCZOS)
    if st.session_state.rotation:
        fill = (0, 0, 0, 0) if img.mode == "RGBA" else (0, 0, 0)
        img = img.rotate(st.session_state.rotation, expand=True, fillcolor=fill)
    if st.session_state.flip_h:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if st.session_state.flip_v:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img = apply_adjustments(img, st.session_state.brightness, st.session_state.contrast, st.session_state.saturation, st.session_state.sharpness)
    img = apply_filter(img, st.session_state.filter_name)
    txt = st.session_state.txt.strip()
    if txt:
        img = draw_text_on_image(img, txt, st.session_state.txt_x, st.session_state.txt_y, st.session_state.txt_size, st.session_state.txt_color)
    return img


# ── Sidebar ──
with st.sidebar:
    st.markdown("## \U0001F3A8 Image Editor")
    st.markdown("---")
    uploaded = st.file_uploader("Upload Image", type=SUPPORTED_FORMATS)

    if uploaded:
        if uploaded.name != st.session_state._fname:
            img = constrain_image(Image.open(uploaded))
            st.session_state.original = img
            st.session_state._fname = uploaded.name
            reset_controls()

        orig = st.session_state.original
        with st.expander("\U0001F4CB Image Info", expanded=False):
            st.write(f"**Size:** {orig.width} \u00d7 {orig.height} px")
            st.write(f"**Mode:** {orig.mode}")
            st.write(f"**File:** {uploaded.name}")

        tab_adj, tab_trans, tab_filt, tab_text, tab_exp = st.tabs(["\u2699 Adjust", "\U0001F504 Transform", "\u2728 Filters", "\u270F Text", "\U0001F4BE Export"])

        with tab_adj:
            st.session_state.brightness = st.slider("Brightness", 0.2, 3.0, st.session_state.brightness, 0.05)
            st.session_state.contrast = st.slider("Contrast", 0.2, 3.0, st.session_state.contrast, 0.05)
            st.session_state.saturation = st.slider("Saturation", 0.0, 3.0, st.session_state.saturation, 0.05)
            st.session_state.sharpness = st.slider("Sharpness", 0.0, 3.0, st.session_state.sharpness, 0.05)

        with tab_trans:
            st.session_state.rotation = st.slider("Rotate (\u00b0)", -180, 180, st.session_state.rotation, 1)
            c1, c2 = st.columns(2)
            st.session_state.flip_h = c1.checkbox("Flip H", st.session_state.flip_h)
            st.session_state.flip_v = c2.checkbox("Flip V", st.session_state.flip_v)
            st.markdown("##### \u2702 Crop (px from edge)")
            ow, oh = orig.size
            c1, c2 = st.columns(2)
            st.session_state.crop_left = c1.number_input("Left", 0, ow - 1, st.session_state.crop_left, key="cl")
            st.session_state.crop_right = c2.number_input("Right", 0, ow - 1, st.session_state.crop_right, key="cr")
            st.session_state.crop_top = c1.number_input("Top", 0, oh - 1, st.session_state.crop_top, key="ct")
            st.session_state.crop_bottom = c2.number_input("Bottom", 0, oh - 1, st.session_state.crop_bottom, key="cb")
            st.markdown("##### \U0001F4D0 Resize")
            st.session_state.lock_aspect = st.checkbox("Lock aspect ratio", st.session_state.lock_aspect)
            new_w = st.number_input("Width", 1, 4096, st.session_state.resize_w, key="rw")
            if st.session_state.lock_aspect and new_w != st.session_state.resize_w and st.session_state.resize_w > 0:
                ratio = new_w / st.session_state.resize_w
                st.session_state.resize_h = max(1, int(st.session_state.resize_h * ratio))
            st.session_state.resize_w = new_w
            st.session_state.resize_h = st.number_input("Height", 1, 4096, st.session_state.resize_h, key="rh")

        with tab_filt:
            st.session_state.filter_name = st.radio("Select filter", FILTER_LIST, index=FILTER_LIST.index(st.session_state.filter_name))

        with tab_text:
            st.session_state.txt = st.text_input("Text", st.session_state.txt)
            c1, c2 = st.columns(2)
            st.session_state.txt_x = c1.number_input("X", 0, 4096, st.session_state.txt_x, key="tx")
            st.session_state.txt_y = c2.number_input("Y", 0, 4096, st.session_state.txt_y, key="ty")
            st.session_state.txt_size = st.slider("Font size", 8, 120, st.session_state.txt_size)
            st.session_state.txt_color = st.color_picker("Color", st.session_state.txt_color)

        with tab_exp:
            dl_fmt = st.selectbox("Format", ["PNG", "JPEG"])
            dl_quality = 95
            if dl_fmt == "JPEG":
                dl_quality = st.slider("Quality", 10, 100, 95, 5)

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("\u21A9 Undo", width='stretch'):
                if st.session_state.undo_img is not None:
                    st.session_state.original = st.session_state.undo_img
                    reset_controls()
                    st.rerun()
        with c2:
            if st.button("\U0001F504 Reset", width='stretch'):
                reset_controls()
                st.rerun()
        with c3:
            if st.button("\u2705 Apply", width='stretch', help="Bake current edits into the image"):
                st.session_state.undo_img = st.session_state.original.copy()
                st.session_state.original = build_edited(st.session_state.original)
                reset_controls()
                st.rerun()

# ── Main area ──
st.markdown("<h2 style='text-align:center;'>\U0001F5BC\uFE0F Image Editor <span style='font-size:0.5em;color:#888;'></span></h2>", unsafe_allow_html=True)

if st.session_state.original is None:
    st.markdown("---")
    st.info("\U0001F448 Upload an image from the sidebar to get started.")
else:
    edited = build_edited(st.session_state.original)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Original**")
        st.image(st.session_state.original, width='stretch')
    with col_b:
        st.markdown("**Edited**")
        st.image(edited, width='stretch')

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
        st.download_button(f"\u2B07 Download .{ext}", buf, file_name=f"edited.{ext}", mime=f"image/{ext}", width='stretch')
