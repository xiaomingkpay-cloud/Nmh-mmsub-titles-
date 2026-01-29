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
            if today > expiry_date:
                return False, name, f"⛔ ကုဒ်သက်တမ်းကုန်ဆုံးသွားပါပြီ။ (Expired on: {expiry_str})"
            else: return True, name, None
        except: return True, user_value, None
    else: return True, user_value, None

def check_auto_login():
    if "user_info" in st.session_state and st.session_state.user_info is not None: return
    current_ip = get_remote_ip()
    for code, bound_ip in usage_data["bindings"].items():
        if bound_ip == current_ip:
            if "users" in st.secrets and code in st.secrets["users"]:
                raw_value = st.secrets["users"][code]
                is_valid, user_name, error_msg = check_code_validity(raw_value)
                if is_valid:
                    st.session_state.user_info = user_name
                    st.toast(f"ကြိုဆိုပါတယ် {user_name}!", icon="✅")
                    return
                else:
                    del usage_data["bindings"][code]
                    return
check_auto_login()
if "user_info" not in st.session_state: st.session_state.user_info = None

# ==========================================
# 🏠 HEADER
# ==========================================
st.title("✨ NMH Pro Creator Tools")
tab1, tab2, tab3, tab4 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (Free)", "🗣️ အသံထုတ်ရန် (VIP)", "🎬 Video ပေါင်းရန် (VIP)"])

# ==========================================
# TAB 1: SRT GENERATOR
# ==========================================
with tab1:
    st.header("Gemini SRT Generator")
    st.link_button("🚀 Gemini သို့သွားရန်", "https://gemini.google.com/")
    srt_text_input = st.text_area("Gemini မှ စာသားများကို ဒီမှာထည့်ပါ:", height=200)
    if srt_text_input and st.button("SRT အဖြစ် ပြောင်းမည်"):
        clean_text = srt_text_input.replace("```srt", "").replace("```", "").strip()
        with open("manual_converted.srt", "w", encoding="utf-8") as f: f.write(clean_text)
        st.success("အောင်မြင်ပါသည်!")
        with open("manual_converted.srt", "rb") as f: st.download_button("SRT ဖိုင်ဒေါင်းရန်", f.read(), "myanmar.srt")

# ==========================================
# TAB 2: SUBTITLE BURNER (BIGGER & HIGHER)
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
        
        # 🔥 FIX: စာလုံးဆိုဒ်ကို ပိုကြီးအောင် ပြင်လိုက်ပါတယ် (/18)
        font_size = int(video_width / 18)
        try: font = ImageFont.truetype(font_path, font_size)
        except: font = ImageFont.load_default()
        
        for line in subs:
            if not line.text.strip(): continue
            
            # စာသားကို အကြောင်းခွဲခြင်း
            original_text = line.text.replace("\\N", " ").replace("\n", " ")
            wrapped_text = textwrap.fill(original_text, width=35) 
            
            # စာတန်းပုံရိပ် တည်ဆောက်ခြင်း
            text_w, text_h = int(video_width * 0.95), int(video_height * 0.40)
            img = Image.new('RGBA', (text_w, text_h), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # စာသားရေးဆွဲခြင်း
            draw.text((text_w/2, text_h/2), wrapped_text, font=font, fill="white", 
                      stroke_width=3, stroke_fill="black", anchor="mm", align="center")
            
            clip = ImageClip(np.array(img)).set_start(line.start / 1000).set_duration((line.end - line.start) / 1000)
            
            # 🔥 FIX: စာတန်းနေရာကို အပေါ်နည်းနည်း ပိုတက်အောင် ပြင်လိုက်ပါတယ် (0.70)
            clip = clip.set_position(('center', 0.70), relative=True)
            subtitle_clips.append(clip)
        return subtitle_clips

    if usage_left > 0 and v1_file and s1_file and st.button("စာတန်းမြှုပ်မည်", key="btn_free"):
        with st.spinner("စာတန်းများကို ဆိုဒ်ကြီးပြီး အပေါ်တင်ပေးနေပါသည်..."):
            vp, sp, fp, op = "temp_v1.mp4", "temp_s1.srt", "myanmar_font.ttf", "output_sub.mp4"
            with open(vp, "wb") as f: f.write(v1_file.getbuffer())
            with open(sp, "wb") as f: f.write(s1_file.getbuffer())
            
            try:
                video = VideoFileClip(vp)
                sub_clips = generate_subtitle_clips(sp, video.w, video.h, fp)
                final_video = CompositeVideoClip([video] + sub_clips)
                final_video.write_videofile(op, fps=24, codec='libx264', preset='fast', audio_codec='aac', threads=4, ffmpeg_params=["-crf", "23"])
                usage_data["users"][user_ip] += 1
                st.success("အောင်မြင်ပါသည်!")
                with open(op, "rb") as f: st.download_button("Video ဒေါင်းရန်", f.read(), "subbed.mp4", "video/mp4")
            except Exception as e: st.error(f"Error: {e}")
            if os.path.exists(vp): os.remove(vp)
            if os.path.exists(sp): os.remove(sp)
            if os.path.exists(op): os.remove(op)

# ==========================================
# TAB 3 & 4 (VIP)
# ==========================================
def show_login_ui(key_suffix):
    st.warning("🔒 ဝင်ရောက်ရန် VIP ကုဒ် လိုအပ်ပါသည်။")
    token_input = st.text_input("VIP Access Token:", type="password", key=f"pro_token_{key_suffix}")
    if st.button("VIP အကောင့်ဝင်မည်", key=f"btn_login_{key_suffix}"):
        if "users" in st.secrets and token_input in st.secrets["users"]:
            raw_value = st.secrets["users"][token_input]
            is_valid, user_name, error_msg = check_code_validity(raw_value)
            if not is_valid: st.error(error_msg)
            else:
                current_ip = get_remote_ip()
                if token_input not in usage_data["bindings"] or usage_data["bindings"][token_input] == current_ip:
                    usage_data["bindings"][token_input] = current_ip
                    st.session_state.user_info = user_name
                    st.rerun()
                else: st.error("⛔ Device Locked")
        else: st.error("Code မှားယွင်းနေပါသည်။")

with tab3:
    st.header("Tab 3: အသံထုတ်လုပ်နည်း")
    if st.session_state.user_info is None: show_login_ui("t3")
    else:
        st.success(f"✅ VIP အကောင့်: {st.session_state.user_info}")
        st.info("Charon, Nova, Orion စသည့် အသံများကို Google AI Studio တွင် ထုတ်ယူပါ။")
        st.link_button("🚀 Google AI Studio သို့ သွားရန်", "https://aistudio.google.com/")

with tab4:
    st.header("Tab 4: Video နှင့် အသံဖိုင် ပေါင်းခြင်း")
    if st.session_state.user_info is None: show_login_ui("t4")
    else:
        st.success(f"✅ VIP အကောင့်: {st.session_state.user_info}")
        if st.button("Logout", key="out_t4"):
            st.session_state.user_info = None
            st.rerun()
        
        col_v, col_a = st.columns(2)
        with col_v: video_in = st.file_uploader("Video ရွေးပါ", type=["mp4", "mov"], key="vid_merge")
        with col_a: audio_in = st.file_uploader("Audio ရွေးပါ", type=["mp3", "wav", "m4a"], key="aud_merge")
        
        speed = st.select_slider("အသံ အနှေး/အမြန်:", options=["0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"], value="1.0x")
        keep_bg = st.checkbox("မူရင်း Video နောက်ခံအသံ ထားမည်", value=True)

        if video_in and audio_in and st.button("ပေါင်းစပ်မည်"):
            with st.spinner("လုပ်ဆောင်နေပါသည်..."):
                t_vid, t_aud, t_out = "t_v.mp4", "t_a.mp3", "out.mp4"
                with open(t_vid, "wb") as f: f.write(video_in.getbuffer())
                with open(t_aud, "wb") as f: f.write(audio_in.getbuffer())
                
                try:
                    # FFmpeg Speed Change (if needed)
                    final_aud = t_aud
                    if speed != "1.0x":
                        rate = speed.replace("x", "")
                        subprocess.run(["ffmpeg", "-y", "-i", t_aud, "-filter:a", f"atempo={rate}", "-vn", "t_proc.mp3"])
                        final_aud = "t_proc.mp3"

                    vc = VideoFileClip(t_vid)
                    ac = AudioFileClip(final_aud)
                    if ac.duration > vc.duration: ac = ac.subclip(0, vc.duration)
                    
                    audio_final = CompositeAudioClip([vc.audio.volumex(0.1), ac]) if keep_bg and vc.audio else ac
                    final_vid = vc.set_audio(audio_final)
                    final_vid.write_videofile(t_out, fps=24, codec='libx264', audio_codec='aac')
                    
                    st.success("အောင်မြင်ပါသည်!")
                    with open(t_out, "rb") as f: st.download_button("ဒေါင်းလုဒ်ဆွဲရန်", f.read(), "merged.mp4")
                except Exception as e: st.error(str(e))
                for f in [t_vid, t_aud, t_out, "t_proc.mp3"]:
                    if os.path.exists(f): os.remove(f)
                        
