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

def check_code_validity(user_value):
    if "|" in user_value:
        try:
            name_part, date_part = user_value.split("|")
            name = name_part.strip()
            expiry_str = date_part.strip()
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            if datetime.now().date() > expiry_date: return False, name, f"⛔ ကုဒ်သက်တမ်းကုန်ဆုံးသွားပါပြီ။ ({expiry_str})"
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
# 🏠 MAIN TABS UI
# ==========================================
st.title("✨ NMH Pro Creator Tools")

# Tab တွေကို ဒီမှာ တစ်ပြိုင်နက် ဖန်တီးလိုက်ပါတယ်
tab1, tab2, tab3, tab4 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (Free)", "🗣️ အသံထုတ်ရန် (VIP)", "🎬 Video ပေါင်းရန် (VIP)"])

# ------------------------------------------
# TAB 1: SRT GENERATOR
# ------------------------------------------
with tab1:
    st.header("Gemini SRT Generator")
    st.link_button("🚀 Google Gemini သို့သွားရန်", "https://gemini.google.com/")
    srt_text_input = st.text_area("Gemini မှ စာသားများကို ဒီမှာထည့်ပါ:", height=200, key="srt_ta")
    if srt_text_input and st.button("SRT အဖြစ် ပြောင်းမည်", key="srt_btn"):
        clean_text = srt_text_input.replace("```srt", "").replace("```", "").strip()
        with open("manual_converted.srt", "w", encoding="utf-8") as f: f.write(clean_text)
        st.success("အောင်မြင်ပါသည်!")
        with open("manual_converted.srt", "rb") as f: st.download_button("Download SRT", f.read(), "myanmar.srt")

# ------------------------------------------
# TAB 2: SUBTITLE BURNER
# ------------------------------------------
with tab2:
    st.header("Tab 2: စာတန်းမြှုပ်ခြင်း (Free)")
    user_ip = get_remote_ip()
    if user_ip not in usage_data["users"]: usage_data["users"][user_ip] = 0
    usage_left = 3 - usage_data["users"][user_ip]
    if usage_left > 0: st.info(f"✅ ယနေ့လက်ကျန်: {usage_left}/3 ပုဒ်")
    else: st.error("⛔ Limit Reached")

    col1, col2 = st.columns(2)
    with col1: v1_file = st.file_uploader("Video တင်ပါ", type=["mp4", "mov"], key="v1_up")
    with col2: s1_file = st.file_uploader("SRT တင်ပါ", type=["srt"], key="s1_up")

    def generate_subtitle_clips(subtitle_path, video_width, video_height, font_path):
        subs = pysubs2.load(subtitle_path, encoding="utf-8")
        subtitle_clips = []
        if video_height > video_width: wrap_w, pos_y, f_div = 35, 0.70, 18
        else: wrap_w, pos_y, f_div = 70, 0.80, 22
        font_size = int(video_width / f_div)
        try: font = ImageFont.truetype(font_path, font_size)
        except: font = ImageFont.load_default()
        for line in subs:
            if not line.text.strip(): continue
            wrapped_text = textwrap.fill(line.text.replace("\\N", " "), width=wrap_w)
            text_w, text_h = int(video_width * 0.95), int(video_height * 0.40)
            img = Image.new('RGBA', (text_w, text_h), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            draw.text((text_w/2, text_h/2), wrapped_text, font=font, fill="white", stroke_width=3, stroke_fill="black", anchor="mm", align="center")
            clip = ImageClip(np.array(img)).set_start(line.start / 1000).set_duration((line.end - line.start) / 1000)
            clip = clip.set_position(('center', pos_y), relative=True)
            subtitle_clips.append(clip)
        return subtitle_clips

    if usage_left > 0 and v1_file and s1_file and st.button("စာတန်းမြှုပ်မည်", key="burn_btn"):
        with st.spinner("Processing..."):
            vp, sp, fp, op = "t_v1.mp4", "t_s1.srt", "myanmar_font.ttf", "out_sub.mp4"
            with open(vp, "wb") as f: f.write(v1_file.getbuffer())
            with open(sp, "wb") as f: f.write(s1_file.getbuffer())
            try:
                video = VideoFileClip(vp)
                sub_clips = generate_subtitle_clips(sp, video.w, video.h, fp)
                final_v = CompositeVideoClip([video] + sub_clips)
                final_v.write_videofile(op, fps=24, codec='libx264', audio_codec='aac')
                usage_data["users"][user_ip] += 1
                st.success("Done!")
                with open(op, "rb") as f: st.download_button("Download Result", f.read(), "subbed.mp4")
            except Exception as e: st.error(str(e))
            for f in [vp, sp, op]: 
                if os.path.exists(f): os.remove(f)

# ------------------------------------------
# HELPER: LOGIN UI (VIP ဧရိယာအတွက်)
# ------------------------------------------
def show_login_ui(key_id):
    st.warning("🔒 VIP ကုဒ် လိုအပ်ပါသည်။")
    token = st.text_input("Enter Token:", type="password", key=f"tk_{key_id}")
    if st.button("Login", key=f"btn_ln_{key_id}"):
        if "users" in st.secrets and token in st.secrets["users"]:
            val = st.secrets["users"][token]
            ok, name, err = check_code_validity(val)
            if ok:
                current_ip = get_remote_ip()
                if token not in usage_data["bindings"] or usage_data["bindings"][token] == current_ip:
                    usage_data["bindings"][token] = current_ip
                    st.session_state.user_info = name
                    st.rerun()
                else: st.error("Device Locked")
            else: st.error(err)
        else: st.error("Code မှားယွင်းနေပါသည်။")

# ------------------------------------------
# TAB 3: AUDIO GUIDE
# ------------------------------------------
with tab3:
    st.header("Tab 3: အသံထုတ်လုပ်နည်း")
    if st.session_state.user_info is None:
        show_login_ui("t3_login")
    else:
        st.success(f"✅ VIP အကောင့်: {st.session_state.user_info}")
        col_m, col_f = st.columns(2)
        with col_m: st.info("**👨 ကျားအသံ:**\n* Charon, Orion, Puck")
        with col_f: st.warning("**👩 မအသံ:**\n* Nova, Shimmer, Aoede")
        st.write("၁။ Google AI Studio သို့ သွားပါ။ ၂။ 'Turn text into audio' ကို နှိပ်ပြီး အသံထုတ်ပါ။")
        st.link_button("🚀 Go to Google AI Studio", "https://aistudio.google.com/")

# ------------------------------------------
# TAB 4: VIDEO MERGE
# ------------------------------------------
with tab4:
    st.header("Tab 4: Video နှင့် အသံဖိုင် ပေါင်းစပ်ခြင်း")
    if st.session_state.user_info is None:
        show_login_ui("t4_login")
    else:
        st.success(f"✅ VIP အကောင့်: {st.session_state.user_info}")
        if st.button("Logout", key="logout_btn"):
            st.session_state.user_info = None
            st.rerun()
        
        col_v, col_a = st.columns(2)
        with col_v: v_in = st.file_uploader("Video ရွေးပါ", type=["mp4", "mov"], key="vm_up")
        with col_a: a_in = st.file_uploader("Audio ရွေးပါ", type=["mp3", "wav", "m4a"], key="am_up")
        
        speed = st.select_slider("အသံ အနှေး/အမြန်:", options=["0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"], value="1.0x")
        keep_bg = st.checkbox("မူရင်း Background အသံထားမည်", value=True, key="bg_cb")

        if v_in and a_in and st.button("Merge Now", key="m_btn"):
            with st.spinner("Processing..."):
                t_v, t_a, t_o = "t_v.mp4", "t_a.mp3", "merged_out.mp4"
                with open(t_v, "wb") as f: f.write(v_in.getbuffer())
                with open(t_a, "wb") as f: f.write(a_in.getbuffer())
                try:
                    final_a = t_a
                    if speed != "1.0x":
                        rate = speed.replace("x", "")
                        subprocess.run(["ffmpeg", "-y", "-i", t_a, "-filter:a", f"atempo={rate}", "-vn", "t_proc.mp3"])
                        final_a = "t_proc.mp3"
                    vc = VideoFileClip(t_v)
                    ac = AudioFileClip(final_a)
                    if ac.duration > vc.duration: ac = ac.subclip(0, vc.duration)
                    audio_final = CompositeAudioClip([vc.audio.volumex(0.1), ac]) if keep_bg and vc.audio else ac
                    final_vid = vc.set_audio(audio_final)
                    final_vid.write_videofile(t_o, fps=24, codec='libx264', audio_codec='aac')
                    st.success("အောင်မြင်ပါသည်!")
                    with open(t_o, "rb") as f: st.download_button("Download Result", f.read(), "final_video.mp4")
                except Exception as e: st.error(str(e))
                for f in [t_v, t_a, t_o, "t_proc.mp3"]:
                    if os.path.exists(f): os.remove(f)
                        
