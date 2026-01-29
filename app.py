import streamlit as st
import os
import pysubs2
import textwrap
import numpy as np
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

def get_remote_ip():
    try:
        headers = _get_websocket_headers()
        ip = headers.get("X-Forwarded-For")
        if ip: return ip.split(",")[0]
    except: pass
    return "unknown_user"

def check_code_validity(user_value):
    if "|" in user_value:
        try:
            name_part, date_part = user_value.split("|")
            expiry_date = datetime.strptime(date_part.strip(), "%Y-%m-%d").date()
            if datetime.now().date() > expiry_date: 
                return False, name_part.strip(), f"⛔ သက်တမ်းကုန်သွားပါပြီ ({date_part.strip()})"
            return True, name_part.strip(), None
        except: return True, user_value, None
    return True, user_value, None

if "user_info" not in st.session_state:
    st.session_state.user_info = None
    current_ip = get_remote_ip()
    for code, bound_ip in usage_data["bindings"].items():
        if bound_ip == current_ip and code in st.secrets.get("users", {}):
            ok, name, err = check_code_validity(st.secrets["users"][code])
            if ok: st.session_state.user_info = name

def show_login_ui(key):
    st.warning("🔒 VIP ကုဒ် လိုအပ်ပါသည်။")
    tk = st.text_input("Enter Token:", type="password", key=f"tk_{key}")
    if st.button("Login", key=f"ln_{key}"):
        if tk in st.secrets.get("users", {}):
            ok, name, err = check_code_validity(st.secrets["users"][tk])
            if ok:
                usage_data["bindings"][tk] = get_remote_ip()
                st.session_state.user_info = name
                st.rerun()
            else: st.error(err)
        else: st.error("Code မှားယွင်းနေပါသည်။")

# ==========================================
# 🏠 TOP BANNER
# ==========================================
st.title("✨ NMH Pro Creator Tools")
col_h1, col_h2 = st.columns([2, 1.5])
with col_h1:
    st.markdown("### 👨‍💻 Developed by Naing Min Htet")
    st.write("Professional Tools for Content Creators")
with col_h2:
    st.link_button("🔵 Facebook Page", "https://www.facebook.com/share/1aavUJzZ9f/")
    st.link_button("✈️ Telegram Contact", "https://t.me/xiaoming2025nmx")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (FREE/VIP)", "🗣️ အသံထုတ်ရန် (VIP)", "🎬 Video ပေါင်းရန် (VIP)"])

# --- TAB 1 ---
with tab1:
    st.header("Gemini SRT Generator")
    st.markdown("### 📝 SRT ထုတ်ယူပုံ လမ်းညွှန်:")
    st.code("Myanmar စာတန်ထိုး srt ထုတ်ပေးပါ", language=None)
    st.link_button("🚀 Google Gemini သို့သွားရန်", "https://gemini.google.com/")
    srt_ta = st.text_area("Gemini မှ ရလာသော SRT စာသားများကို ဒီမှာထည့်ပါ:", height=200, key="t1_ta")
    if srt_ta and st.button("SRT အဖြစ် ပြောင်းမည်", key="t1_btn"):
        clean = srt_ta.replace("```srt", "").replace("```", "").strip()
        st.success("Done!")
        st.download_button("Download SRT", clean, "myanmar.srt")

# --- TAB 2 (SPEED OPTIMIZED) ---
with tab2:
    st.header("Tab 2: စာတန်းမြှုပ်ခြင်း")
    u_ip = get_remote_ip()
    is_vip = st.session_state.user_info is not None
    if is_vip: st.success(f"🌟 VIP အကောင့်: {st.session_state.user_info}")
    else:
        if u_ip not in usage_data["users"]: usage_data["users"][u_ip] = 0
        left = 3 - usage_data["users"][u_ip]
        if left > 0: st.info(f"✅ Free လက်ကျန်: {left}/3 ပုဒ်")
        else: st.error("⛔ Limit Reached")

    v_file = st.file_uploader("Video တင်ပါ", type=["mp4", "mov"], key="t2_v")
    s_file = st.file_uploader("SRT တင်ပါ", type=["srt"], key="t2_s")

    def make_subs(s_path, v_w, v_h, f_path):
        subs = pysubs2.load(s_path, encoding="utf-8")
        clips = []
        is_v = v_h > v_w
        wrap, pos, f_div = (35, 0.65, 18) if is_v else (50, 0.60, 22)
        font = ImageFont.truetype(f_path, int(v_w / f_div))
        for line in subs:
            if not line.text.strip(): continue
            txt = textwrap.fill(line.text.replace("\\N", " "), width=wrap)
            box_w, box_h = int(v_w * 0.98), int(v_h * 0.60)
            img = Image.new('RGBA', (box_w, box_h), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            bbox = draw.textbbox((box_w/2, box_h/2), txt, font=font, anchor="mm", align="center")
            pad = 18
            draw.rectangle([bbox[0]-pad, bbox[1]-pad, bbox[2]+pad, bbox[3]+pad], fill=(0, 0, 0, 160))
            draw.text((box_w/2, box_h/2), txt, font=font, fill="white", stroke_width=2, stroke_fill="black", anchor="mm", align="center")
            c = ImageClip(np.array(img)).set_start(line.start/1000).set_duration((line.end-line.start)/1000).set_position(('center', pos), relative=True)
            clips.append(c)
        return clips

    if (is_vip or usage_data["users"][u_ip] < 3) and v_file and s_file and st.button("စာတန်းမြှုပ်မည်", key="t2_btn"):
        with st.spinner("မြန်မြန်ဆန်ဆန် ပေါင်းစပ်ပေးနေပါသည်..."):
            with open("t_v.mp4", "wb") as f: f.write(v_file.getbuffer())
            with open("t_s.srt", "wb") as f: f.write(s_file.getbuffer())
            try:
                vid = VideoFileClip("t_v.mp4")
                final = CompositeVideoClip([vid] + make_subs("t_s.srt", vid.w, vid.h, "myanmar_font.ttf"))
                # 🔥 Optimization: threads=4 နှင့် preset='ultrafast' ထည့်သွင်းထားသည်
                final.write_videofile("o.mp4", fps=24, codec='libx264', audio_codec='aac', threads=4, preset='ultrafast')
                if not is_vip: usage_data["users"][u_ip] += 1
                st.success("အောင်မြင်ပါသည်!")
                with open("o.mp4", "rb") as f: st.download_button("Download", f.read(), "subbed.mp4")
            except Exception as e: st.error(str(e))
            for f in ["t_v.mp4", "t_s.srt", "o.mp4"]:
                if os.path.exists(f): os.remove(f)

# --- TAB 3: AUDIO ---
with tab3:
    st.header("Tab 3: အသံထုတ်လုပ်နည်း")
    if not st.session_state.user_info: show_login_ui("t3")
    else:
        st.success(f"✅ VIP အကောင့်: {st.session_state.user_info}")
        col1, col2 = st.columns(2)
        with col1: st.info("**👨 ကျားအသံ:**\n* Charon, Orion, Puck")
        with col2: st.warning("**👩 မအသံ:**\n* Nova, Shimmer, Aoede")
        st.markdown("### 📝 အဆင့်ဆင့်လမ်းညွှန်ချက်:")
        st.markdown("1. AI Studio သွားပါ။\n2. 'Turn text into audio' ရွေးပါ။\n3. Voice Color ရွေးပြီး Generate လုပ်ပါ။")
        st.link_button("🚀 Go to Google AI Studio", "https://aistudio.google.com/")

# --- TAB 4 (SPEED OPTIMIZED) ---
with tab4:
    st.header("Tab 4: Video နှင့် အသံဖိုင် ပေါင်းစပ်ခြင်း")
    if not st.session_state.user_info: show_login_ui("t4")
    else:
        st.success(f"✅ VIP အကောင့်: {st.session_state.user_info}")
        v_in = st.file_uploader("Video ရွေးပါ", type=["mp4", "mov"], key="t4_v")
        a_in = st.file_uploader("Audio ရွေးပါ", type=None, key="t4_a")
        spd = st.select_slider("Speed:", options=["0.9x", "1.0x", "1.1x", "1.2x", "1.3x"], value="1.0x")
        bg = st.checkbox("မူရင်း Background အသံထားမည်", value=True)
        if v_in and a_in and st.button("Merge Now"):
            with st.spinner("Processing..."):
                a_ex = a_in.name.split(".")[-1]
                with open("v.mp4", "wb") as f: f.write(v_in.getbuffer())
                with open(f"a.{a_ex}", "wb") as f: f.write(a_in.getbuffer())
                try:
                    fin_a = f"a.{a_ex}"
                    if spd != "1.0x":
                        subprocess.run(["ffmpeg", "-y", "-i", fin_a, "-filter:a", f"atempo={spd.replace('x','')}", "-vn", "ap.mp3"])
                        fin_a = "ap.mp3"
                    vc = VideoFileClip("v.mp4")
                    ac = AudioFileClip(fin_a)
                    if ac.duration > vc.duration: ac = ac.subclip(0, vc.duration)
                    af = CompositeAudioClip([vc.audio.volumex(0.1), ac]) if bg and vc.audio else ac
                    # 🔥 Optimization: threads=4 နှင့် preset='ultrafast'
                    vc.set_audio(af).write_videofile("o.mp4", fps=24, codec='libx264', audio_codec='aac', threads=4, preset='ultrafast')
                    st.success("Done!")
                    with open("o.mp4", "rb") as f: st.download_button("Download", f.read(), "merged.mp4")
                except Exception as e: st.error(str(e))
                for f in ["v.mp4", f"a.{a_ex}", "ap.mp3", "o.mp4"]:
                    if os.path.exists(f): os.remove(f)
                        
