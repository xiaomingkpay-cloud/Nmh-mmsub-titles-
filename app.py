import streamlit as st
import os
import pysubs2
import numpy as np
import asyncio
import edge_tts
from datetime import datetime
from streamlit.web.server.websocket_headers import _get_websocket_headers
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip
from PIL import Image, ImageDraw, ImageFont

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
# 🏠 HEADER
# ==========================================
st.title("✨ NMH Pro Creator Mood")
st.markdown("""
**📞 Contact Creator:** Facebook: [NMH Facebook](https://www.facebook.com/share/16pXwBsqte) | Telegram: [@xiaoming2025nmx](https://t.me/xiaoming2025nmx)
""")
st.success("📢 Facebook / TikTok / VPN / Follower နှင့် တခြား Premium Service များလဲ ရသည်!")

# TAB 3 ခု
tab1, tab2, tab3 = st.tabs(["Tab 1: 🌐 Get SRT (Gemini)", "Tab 2: 📝 စာတန်းမြှုပ် (Free)", "Tab 3: 🗣️ အသံထည့် (Pro)"])

# ==========================================
# TAB 1: GEMINI LINK & TEXT TO SRT CONVERTER
# ==========================================
with tab1:
    st.header("အဆင့် ၁ - Gemini မှ SRT စာသားတောင်းယူပါ")
    st.info("အောက်ပါခလုတ်ကို နှိပ်ပြီး Gemini တွင် Video တင်ပါ။ 'Generate Myanmar SRT file' ဟု ရေးပြီး တောင်းပါ။")
    
    # 1. Gemini Link Button
    st.link_button("🚀 Go to Google Gemini App/Web", "https://gemini.google.com/")
    
    st.write("---")
    st.header("အဆင့် ၂ - ရလာသော စာသားကို SRT ဖိုင်ပြောင်းပါ")
    
    # 2. Text Area for Copy-Paste
    srt_text_input = st.text_area("Gemini မှပေးလိုက်သော SRT စာသားများကို ဒီအကွက်ထဲ Paste ချပါ:", height=300)
    
    if srt_text_input and st.button("SRT ဖိုင်အဖြစ် ပြောင်းမည် (Convert Now)"):
        # Clean the text (remove markdown code blocks if present)
        clean_text = srt_text_input.replace("```srt", "").replace("```", "").strip()
        
        output_srt = "manual_converted.srt"
        with open(output_srt, "w", encoding="utf-8") as f:
            f.write(clean_text)
            
        st.success("✅ SRT ဖိုင် ထုတ်လုပ်ပြီးပါပြီ! ဒေါင်းယူနိုင်ပါသည်")
        with open(output_srt, "rb") as f:
            st.download_button("Download SRT File", f.read(), "myanmar_converted.srt", "text/plain")

# ==========================================
# TAB 2: BURN SUBTITLE (HIGH QUALITY)
# ==========================================
with tab2:
    st.header("Tab 2: ရလာသော SRT ကို Video တွင် အသေမြှုပ်ခြင်း")
    
    user_ip = get_remote_ip()
    if user_ip not in usage_data["users"]: usage_data["users"][user_ip] = 0
    usage_left = 3 - usage_data["users"][user_ip]
    
    if usage_left > 0:
        st.info(f"✅ ယနေ့အတွက် လက်ကျန်: {usage_left} ပုဒ်")
    else:
        st.error("⛔ Free Limit ပြည့်သွားပါပြီ! Pro Code ဝယ်ယူပါ။")

    col1, col2 = st.columns(2)
    with col1: v1_file = st.file_uploader("Video ဖိုင်", type=["mp4", "mov", "avi"], key="v1")
    with col2: s1_file = st.file_uploader("SRT ဖိုင်", type=["srt"], key="s1")

    def generate_subtitle_clips(subtitle_path, video_width, video_height, font_path):
        subs = pysubs2.load(subtitle_path, encoding="utf-8")
        subtitle_clips = []
        fontsize = int(video_width / 25)
        try: font = ImageFont.truetype(font_path, fontsize)
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

    if usage_left > 0 and v1_file and s1_file and st.button("စာတန်းမြှုပ်မည် (Start Burning)", key="btn_free"):
        with st.spinner("စာတန်းထည့်နေပါသည် (High Quality Mode)..."):
            vp, sp, fp, op = "temp_v1.mp4", "temp_s1.srt", "myanmar_font.ttf", "output_sub.mp4"
            with open(vp, "wb") as f: f.write(v1_file.getbuffer())
            with open(sp, "wb") as f: f.write(s1_file.getbuffer())
            
            if not os.path.exists(fp): st.error("Font Missing!")
            else:
                try:
                    video = VideoFileClip(vp)
                    sub_clips = generate_subtitle_clips(sp, video.w, video.h, fp)
                    final_video = CompositeVideoClip([video] + sub_clips)
                    
                    # --- HIGH QUALITY SETTINGS ---
                    # preset='fast' (Better compression than ultrafast)
                    # crf=23 (Standard High Quality, not too big)
                    final_video.write_videofile(
                        op, 
                        fps=24, 
                        codec='libx264', 
                        preset='fast', 
                        audio_codec='aac', 
                        threads=4, 
                        ffmpeg_params=["-crf", "23"] 
                    )
                    
                    usage_data["users"][user_ip] += 1
                    st.success("Success! (Quality: Clear & Crisp)")
                    with open(op, "rb") as f: st.download_button("Download Video", f.read(), "subbed_video_hd.mp4", "video/mp4")
                except Exception as e: st.error(f"Error: {e}")
            
            if os.path.exists(vp): os.remove(vp)
            if os.path.exists(sp): os.remove(sp)
            if os.path.exists(op): os.remove(op)

# ==========================================
# TAB 3: PRO VERSION (AI DUBBING - HQ)
# ==========================================
with tab3:
    st.header("Tab 3: Video အသံထည့်ခြင်း (Pro Member)")
    
    if "user_info" not in st.session_state: st.session_state.user_info = None
    
    if st.session_state.user_info is None:
        st.warning("🔒 Feature Locked.")
        col_pass1, _ = st.columns([3, 1])
        with col_pass1: token_input = st.text_input("Pro Access Token:", type="password", key="pro_token")
        
        if st.button("Login"):
            if "users" in st.secrets and token_input in st.secrets["users"]:
                current_ip = get_remote_ip()
                if token_input == "nmh-123": 
                    st.session_state.user_info = st.secrets["users"][token_input]
                    st.rerun()
                else:
                    if token_input not in usage_data["bindings"]:
                        usage_data["bindings"][token_input] = current_ip
                        st.session_state.user_info = st.secrets["users"][token_input]
                        st.rerun()
                    elif usage_data["bindings"][token_input] == current_ip:
                        st.session_state.user_info = st.secrets["users"][token_input]
                        st.rerun()
                    else: st.error("⛔ Device Locked")
            else: st.error("Invalid Code")
        st.stop()

    st.success(f"✅ Welcome {st.session_state.user_info}")
    if "Admin" in st.session_state.user_info:
        if st.button("Reset Locks"):
            usage_data["bindings"] = {}
            st.success("Reset Done!")
    
    if st.button("Logout"):
        st.session_state.user_info = None
        st.rerun()
    st.write("---")
    
    col3, col4 = st.columns(2)
    with col3: v2_file = st.file_uploader("Video (Dub)", type=["mp4", "mov", "avi"], key="v2")
    with col4: s2_file = st.file_uploader("SRT (Dub)", type=["srt"], key="s2")
    
    voice_option = st.selectbox("Voice", ("Female (Thiri)", "Male (Sai Nyi)"))
    VOICE_ID = "my-MM-ThiriNeural" if "Female" in voice_option else "my-MM-SaiNyiNeural"
    keep_original = st.checkbox("Keep Original Audio (Background)", value=False)

    async def generate_voice(text, output_file, voice_id):
        communicate = edge_tts.Communicate(text, voice_id)
        await communicate.save(output_file)

    if v2_file and s2_file and st.button("Start Dubbing", key="btn_pro"):
        with st.spinner("Processing (High Quality)..."):
            vp2, sp2, op2 = "temp_v2.mp4", "temp_s2.srt", "output_dub.mp4"
            with open(vp2, "wb") as f: f.write(v2_file.getbuffer())
            with open(sp2, "wb") as f: f.write(s2_file.getbuffer())
            
            try:
                video = VideoFileClip(vp2)
                subs = pysubs2.load(sp2, encoding="utf-8")
                audio_clips = []
                if keep_original and video.audio is not None:
                    audio_clips.append(video.audio.volumex(0.3))
                
                generated_files, progress_bar = [], st.progress(0)
                for i, line in enumerate(subs):
                    if not line.text.strip(): continue
                    text = line.text.replace("\\N", " ")
                    temp_audio = f"temp_aud_{i}.mp3"
                    asyncio.run(generate_voice(text, temp_audio, VOICE_ID))
                    generated_files.append(temp_audio)
                    if os.path.exists(temp_audio):
                        audioclip = AudioFileClip(temp_audio).set_start(line.start / 1000)
                        audio_clips.append(audioclip)
                    progress_bar.progress((i+1)/len(subs))
            
                final_video = video.set_audio(CompositeAudioClip(audio_clips))
                
                # --- HIGH QUALITY SETTINGS (PRO) ---
                final_video.write_videofile(
                    op2, 
                    fps=24, 
                    codec='libx264', 
                    preset='fast', 
                    audio_codec='aac', 
                    threads=4, 
                    ffmpeg_params=["-crf", "23"]
                )
                
                st.success("Success!")
                with open(op2, "rb") as f: st.download_button("Download Dubbed Video", f.read(), "dubbed_hd.mp4", "video/mp4")
                for f in generated_files: os.remove(f)
            except Exception as e: st.error(f"Error: {e}")
            if os.path.exists(vp2): os.remove(vp2)
            if os.path.exists(sp2): os.remove(sp2)
            if os.path.exists(op2): os.remove(op2)
            
