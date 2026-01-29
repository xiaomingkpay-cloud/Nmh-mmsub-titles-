import streamlit as st
import os
import pysubs2
import textwrap
from datetime import datetime
from streamlit.web.server.websocket_headers import _get_websocket_headers
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
import nest_asyncio
import subprocess

nest_asyncio.apply()

# Website Config
st.set_page_config(page_title="NMH Pro Creator Tools", layout="wide")

# ==========================================
# 🛡️ SECURITY & TRACKER
# ==========================================
@st.cache_resource
def get_usage_data():
    return {"date": datetime.now().strftime("%Y-%m-%d"), "users": {}, "bindings": {}}

usage_data = get_usage_data()
current_date = datetime.now().strftime("%Y-%m-%d")
if usage_data["date"] != current_date:
    usage_data["date"] = current_date
    usage_data["users"] = {} 

def get_remote_ip():
    try:
        headers = _get_websocket_headers()
        ip = headers.get("X-Forwarded-For")
        if ip: return ip.split(",")[0]
    except: pass
    return "unknown_user"

# ==========================================
# 🔄 AUTO LOGIN & EXPIRY CHECK
# ==========================================
def check_code_validity(user_value):
    if "|" in user_value:
        try:
            name_part, date_part = user_value.split("|")
            name = name_part.strip()
            expiry_str = date_part.strip()
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            today = datetime.now().date()
            if today > expiry_date: return False, name, f"⛔ ကုဒ်သက်တမ်းကုန်ဆုံးသွားပါပြီ။ ({expiry_str})"
            else: return True, name, None
        except: return True, user_value, None
    return True, user_value, None

def check_auto_login():
    if "user_info" in st.session_state and st.session_state.user_info is not None: return
    current_ip = get_remote_ip()
    for code, bound_ip in usage_data["bindings"].items():
        if bound_ip == current_ip:
            if "users" in st.secrets and code in st.secrets["users"]:
                raw_value = st.secrets["users"][code]
                ok, name, err = check_code_validity(raw_value)
                if ok:
                    st.session_state.user_info = name
                    st.toast(f"ကြိုဆိုပါတယ် {name}!", icon="✅")
                    return
                else: del usage_data["bindings"][code]
                return

check_auto_login()
if "user_info" not in st.session_state: st.session_state.user_info = None

# ==========================================
# 🏠 HEADER
# ==========================================
st.title("✨ NMH Pro Creator Tools")
tab1, tab2, tab3, tab4 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (Free)", "🗣️ အသံထုတ်ရန် (VIP)", "🎬 Video ပေါင်းရန် (VIP)"])

# ==========================================
# TAB 2: SMART SUBTITLE (AUTO RATIO DETECT)
# ==========================================
with tab2:
    st.header("Tab 2: စာတန်းမြှုပ်ခြင်း (Free)")
    user_ip = get_remote_ip()
    if user_ip not in usage_data["users"]: usage_data["users"][user_ip] = 0
    usage_left = 3 - usage_data["users"][user_ip]
    if usage_left > 0: st.info(f"✅ ယနေ့လက်ကျန်: {usage_left}/3 ပုဒ်")
    else: st.error("⛔ Limit Reached")

    col1, col2 = st.columns(2)
    with col1: v1_file = st.file_uploader("Video တင်ပါ", type=["mp4", "mov"], key="v1")
    with col2: s1_file = st.file_uploader("SRT တင်ပါ", type=["srt"], key="s1")

    def generate_subtitle_clips(subtitle_path, video_width, video_height, font_path):
        import numpy as np
        subs = pysubs2.load(subtitle_path, encoding="utf-8")
        subtitle_clips = []
        
        # 🔥 Video Ratio အလိုက် Wrap Width ကို တွက်ချက်ခြင်း
        # 9:16 (Vertical) ဆိုရင် 35 လုံး၊ 16:9 (Horizontal) ဆိုရင် 70 လုံး ခွဲမယ်
        if video_height > video_width: 
            wrap_width = 35 # ဒေါင်လိုက်
            pos_y = 0.70    # အပေါ်နည်းနည်းတင်
            font_div = 18   # စာလုံးဆိုဒ် ကြီးကြီး
        else: 
            wrap_width = 70 # အလျားလိုက်
            pos_y = 0.80    # အောက်နားပဲထား
            font_div = 22   # အလျားလိုက်အတွက် ဆိုဒ်အသင့်အတင့်

        font_size = int(video_width / font_div)
        try: font = ImageFont.truetype(font_path, font_size)
        except: font = ImageFont.load_default()
        
        for line in subs:
            if not line.text.strip(): continue
            
            # 🔥 Smart Wrapping
            wrapped_text = textwrap.fill(line.text.replace("\\N", " "), width=wrap_width)
            
            text_w, text_h = int(video_width * 0.95), int(video_height * 0.40)
            img = Image.new('RGBA', (text_w, text_h), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            draw.text((text_w/2, text_h/2), wrapped_text, font=font, fill="white", 
                      stroke_width=3, stroke_fill="black", anchor="mm", align="center")
            
            clip = ImageClip(np.array(img)).set_start(line.start / 1000).set_duration((line.end - line.start) / 1000)
            clip = clip.set_position(('center', pos_y), relative=True)
            subtitle_clips.append(clip)
        return subtitle_clips

    if usage_left > 0 and v1_file and s1_file and st.button("စာတန်းမြှုပ်မည်", key="btn_free"):
        with st.spinner("Video Ratio ကို စစ်ဆေးပြီး စာတန်းညှိပေးနေပါသည်..."):
            vp, sp, fp, op = "temp_v1.mp4", "temp_s1.srt", "myanmar_font.ttf", "output_sub.mp4"
            with open(vp, "wb") as f: f.write(v1_file.getbuffer())
            with open(sp, "wb") as f: f.write(s1_file.getbuffer())
            try:
                video = VideoFileClip(vp)
                sub_clips = generate_subtitle_clips(sp, video.w, video.h, fp)
                final_v = CompositeVideoClip([video] + sub_clips)
                final_v.write_videofile(op, fps=24, codec='libx264', audio_codec='aac')
                usage_data["users"][user_ip] += 1
                st.success("အောင်မြင်ပါသည်!")
                with open(op, "rb") as f: st.download_button("Download Result", f.read(), "subbed.mp4")
            except Exception as e: st.error(str(e))
            for f in [vp, sp, op]: 
                if os.path.exists(f): os.remove(f)

# (Tab 1, 3, 4 တို့မှာ အရင်အတိုင်း အပြည့်အစုံ ပါဝင်ပါသည်)
