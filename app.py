import streamlit as st
import os
import pysubs2
from datetime import datetime
from streamlit.web.server.websocket_headers import _get_websocket_headers
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import nest_asyncio

nest_asyncio.apply()

# Website ခေါင်းစဉ်
st.set_page_config(page_title="NMH Pro Creator Mood", layout="wide")

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
# 📅 EXPIRY CHECK SYSTEM (NEW)
# ==========================================
def check_code_validity(user_value):
    """
    Return: (is_valid, user_name, error_msg)
    Input Format: "Name | YYYY-MM-DD" or just "Name"
    """
    if "|" in user_value:
        try:
            name_part, date_part = user_value.split("|")
            name = name_part.strip()
            expiry_str = date_part.strip()
            
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            today = datetime.now().date()
            
            if today > expiry_date:
                return False, name, f"⛔ Code သက်တမ်းကုန်ဆုံးသွားပါပြီ။ (Expired on: {expiry_str})"
            else:
                return True, name, None
        except:
            return True, user_value, None # Format မှားနေရင် ရက်စွဲမစစ်ဘဲ ပေးဝင်မည်
    else:
        # ရက်စွဲမပါရင် Life Time ဟုသတ်မှတ်သည်
        return True, user_value, None

# ==========================================
# 🔄 AUTO LOGIN (WITH EXPIRY CHECK)
# ==========================================
def check_auto_login():
    if "user_info" in st.session_state and st.session_state.user_info is not None:
        return

    current_ip = get_remote_ip()
    
    # Check Bindings
    for code, bound_ip in usage_data["bindings"].items():
        if bound_ip == current_ip:
            if "users" in st.secrets and code in st.secrets["users"]:
                raw_value = st.secrets["users"][code]
                
                # Check Expiry
                is_valid, user_name, error_msg = check_code_validity(raw_value)
                
                if is_valid:
                    st.session_state.user_info = user_name
                    st.toast(f"Welcome back, {user_name}!", icon="✅")
                    return
                else:
                    # Expired ဖြစ်နေရင် Binding ဖျက်လိုက်မည်
                    del usage_data["bindings"][code]
                    return

check_auto_login()

if "user_info" not in st.session_state:
    st.session_state.user_info = None

# ==========================================
# 🏠 HEADER
# ==========================================
st.title("✨ NMH Pro Creator Mood")
st.success("📢 Manual Workflow: Error Free & High Quality Audio")

tab1, tab2, tab3, tab4 = st.tabs([
    "Tab 1: 🌐 Get SRT", 
    "Tab 2: 📝 Burn Sub (Free)", 
    "Tab 3: 🗣️ Get Audio (VIP)", 
    "Tab 4: 🎬 Merge Tool (VIP)"
])

# ==========================================
# TAB 1 & 2 (NORMAL)
# ==========================================
with tab1:
    st.header("Gemini SRT Generator")
    st.link_button("🚀 Go to Google Gemini Chat", "https://gemini.google.com/")
    srt_text_input = st.text_area("Paste SRT Content Here:", height=300)
    if srt_text_input and st.button("Convert to SRT File"):
        clean_text = srt_text_input.replace("```srt", "").replace("```", "").strip()
        output_srt = "manual_converted.srt"
        with open(output_srt, "w", encoding="utf-8") as f: f.write(clean_text)
        with open(output_srt, "rb") as f: st.download_button("Download SRT", f.read(), "myanmar.srt", "text/plain")

with tab2:
    st.header("Subtitle Burner (Free)")
    user_ip = get_remote_ip()
    if user_ip not in usage_data["users"]: usage_data["users"][user_ip] = 0
    usage_left = 3 - usage_data["users"][user_ip]
    if usage_left > 0: st.info(f"✅ Free Limit: {usage_left}/3 left")
    else: st.error("⛔ Limit Reached")

    col1, col2 = st.columns(2)
    with col1: v1_file = st.file_uploader("Video", type=["mp4", "mov"], key="v1")
    with col2: s1_file = st.file_uploader("SRT", type=["srt"], key="s1")

    # (Helper function abbreviated)
    def generate_subtitle_clips(subtitle_path, video_width, video_height, font_path):
        subs = pysubs2.load(subtitle_path, encoding="utf-8")
        subtitle_clips = []
        try: font = ImageFont.truetype(font_path, int(video_width/25))
        except: font = ImageFont.load_default()
        for line in subs:
            if not line.text.strip(): continue
            text_w, text_h = int(video_width * 0.9), int(video_height * 0.25)
            img = Image.new('RGBA', (text_w, text_h), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            text_content = line.text.replace("\\N", "\n")
            try: draw.text((text_w/2, text_h/2), text_content, font=font, fill="white", stroke_width=3, stroke_fill="black", anchor="mm", align="center")
            except: draw.text((10, 10), text_content, font=font, fill="white", stroke_width=2, stroke_fill="black")
            clip = ImageClip(np.array(img)).set_start(line.start / 1000).set_duration((line.end - line.start) / 1000)
            clip = clip.set_position(('center', 0.80), relative=True)
            subtitle_clips.append(clip)
        return subtitle_clips

    if usage_left > 0 and v1_file and s1_file and st.button("Start Burning", key="btn_free"):
        with st.spinner("Processing..."):
            vp, sp, fp, op = "temp_v1.mp4", "temp_s1.srt", "myanmar_font.ttf", "output_sub.mp4"
            with open(vp, "wb") as f: f.write(v1_file.getbuffer())
            with open(sp, "wb") as f: f.write(s1_file.getbuffer())
            if not os.path.exists(fp): st.error("Font Missing!")
            else:
                try:
                    video = VideoFileClip(vp)
                    sub_clips = generate_subtitle_clips(sp, video.w, video.h, fp)
                    final_video = CompositeVideoClip([video] + sub_clips)
                    final_video.write_videofile(op, fps=24, codec='libx264', preset='fast', audio_codec='aac', threads=4, ffmpeg_params=["-crf", "23"])
                    usage_data["users"][user_ip] += 1
                    st.success("Success!")
                    with open(op, "rb") as f: st.download_button("Download Video", f.read(), "subbed.mp4", "video/mp4")
                except Exception as e: st.error(f"Error: {e}")
            if os.path.exists(vp): os.remove(vp)
            if os.path.exists(sp): os.remove(sp)
            if os.path.exists(op): os.remove(op)

# ==========================================
# HELPER: LOGIN UI (WITH EXPIRY CHECK)
# ==========================================
def show_login_ui(key_suffix):
    st.warning("🔒 ဤနေရာကို ဝင်ရောက်ရန် VIP Code လိုအပ်ပါသည်။")
    col_pass1, _ = st.columns([3, 1])
    with col_pass1: 
        token_input = st.text_input("VIP Access Token:", type="password", key=f"pro_token_{key_suffix}")
    
    if st.button("Login to VIP Mode", key=f"btn_login_{key_suffix}"):
        if "users" in st.secrets and token_input in st.secrets["users"]:
            raw_value = st.secrets["users"][token_input]
            
            # --- Check Expiry Date ---
            is_valid, user_name, error_msg = check_code_validity(raw_value)
            
            if not is_valid:
                st.error(error_msg) # Show Expiry Error
                return

            # --- Proceed if Valid ---
            current_ip = get_remote_ip()
            if token_input == "nmh-123": 
                st.session_state.user_info = user_name
                st.rerun()
            else:
                if token_input not in usage_data["bindings"]:
                    usage_data["bindings"][token_input] = current_ip
                    st.session_state.user_info = user_name
                    st.rerun()
                elif usage_data["bindings"][token_input] == current_ip:
                    st.session_state.user_info = user_name
                    st.rerun()
                else: 
                    st.error("⛔ Device Locked: This code is used on another device.")
        else: 
            st.error("Code Invalid")

# ==========================================
# TAB 3: GOOGLE AI STUDIO (VIP)
# ==========================================
with tab3:
    st.header("Tab 3: Audio Generation")
    if st.session_state.user_info is None:
        show_login_ui("t3")
    else:
        st.success(f"✅ VIP Access Granted: {st.session_state.user_info}")
        st.info("Click below to generate audio using Google AI Studio.")
        st.link_button("🚀 Go to Google AI Studio", "https://aistudio.google.com/")

# ==========================================
# TAB 4: MANUAL MERGE (VIP)
# ==========================================
with tab4:
    st.header("Tab 4: Merge Video & Audio")
    if st.session_state.user_info is None:
        show_login_ui("t4")
    else:
        st.success(f"✅ VIP Access Granted: {st.session_state.user_info}")
        if st.button("Logout", key="out_t4"):
            st.session_state.user_info = None
            st.rerun()
        st.write("---")

        col_v, col_a = st.columns(2)
        with col_v: video_input = st.file_uploader("1. Select Video", type=["mp4", "mov"], key="vid_merge")
        with col_a: audio_input = st.file_uploader("2. Select Audio (MP3/WAV)", type=["mp3", "wav", "m4a"], key="aud_merge")

        keep_bg = st.checkbox("Keep Original Background Audio", value=True, key="bg_t4")

        if video_input and audio_input and st.button("Merge Now", key="btn_merge"):
            with st.spinner("Merging..."):
                ext = audio_input.name.split(".")[-1]
                t_vid, t_aud, t_out = "temp_v.mp4", f"temp_a.{ext}", "out.mp4"
                with open(t_vid, "wb") as f: f.write(video_input.getbuffer())
                with open(t_aud, "wb") as f: f.write(audio_input.getbuffer())
                
                try:
                    vc = VideoFileClip(t_vid)
                    ac = AudioFileClip(t_aud)
                    if ac.duration > vc.duration: ac = ac.subclip(0, vc.duration)
                    
                    final_audio = CompositeAudioClip([vc.audio.volumex(0.1), ac]) if keep_bg and vc.audio else ac
                    final_video = vc.set_audio(final_audio)
                    
                    final_video.write_videofile(t_out, fps=24, codec='libx264', preset='fast', audio_codec='aac', threads=4, ffmpeg_params=["-crf", "23"])
                    st.success("Done!")
                    with open(t_out, "rb") as f: st.download_button("Download Video", f.read(), "merged.mp4", "video/mp4")
                except Exception as e: st.error(str(e))
                if os.path.exists(t_vid): os.remove(t_vid)
                if os.path.exists(t_aud): os.remove(t_aud)
                if os.path.exists(t_out): os.remove(t_out)
                    
