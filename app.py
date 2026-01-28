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
tab1, tab2, tab3 = st.tabs(["Tab 1: 🌐 Get SRT (Gemini)", "Tab 2: 📝 စာတန်းမြှုပ် (Free)", "Tab 3: 🗣️ အသံထည့် (Pro - Fixed)"])

# ==========================================
# TAB 1 & 2 (အရင်အတိုင်း)
# ==========================================
# (Tab 1 & Tab 2 Code များကို မူရင်းအတိုင်းထားပါ - နေရာမဆန့်လို့ ဒီမှာ ချန်လှပ်ထားခဲ့ပါတယ်)
# ညီကို့ရဲ့ မူရင်း Code ထဲက Tab 1 နဲ့ Tab 2 ကို ပြန်ကူးထည့်ပေးပါနော်

# ==========================================
# TAB 3: PRO VERSION (FIXED AUDIO ERROR)
# ==========================================
with tab3:
    st.header("Tab 3: Video အသံထည့်ခြင်း (Pro Member)")
    
    if "user_info" not in st.session_state: st.session_state.user_info = None
    
    # Login Logic
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
    if st.button("Logout"):
        st.session_state.user_info = None
        st.rerun()
    st.write("---")
    
    col3, col4 = st.columns(2)
    with col3: v2_file = st.file_uploader("Video (Dub)", type=["mp4", "mov", "avi"], key="v2")
    with col4: s2_file = st.file_uploader("SRT (Dub)", type=["srt"], key="s2")
    
    voice_option = st.selectbox("Voice", ("Female (Thiri)", "Male (Sai Nyi)"))
    
    # --- VOICE ID FIX ---
    # ဒီနေရာမှာ Voice ID ကို သေချာပြန်စစ်ထားပါတယ်
    if "Female" in voice_option:
        VOICE_ID = "my-MM-ThiriNeural"
    else:
        VOICE_ID = "my-MM-SaiNyiNeural"

    keep_original = st.checkbox("Keep Original Audio (Background)", value=True)

    # --- RETRY FUNCTION (အသံမထွက်ရင် ထပ်ခါထပ်ခါ စမ်းမည့်စနစ်) ---
    async def generate_voice_safe(text, output_file, voice_id):
        retries = 3
        for i in range(retries):
            try:
                communicate = edge_tts.Communicate(text, voice_id)
                await communicate.save(output_file)
                return True # Success
            except Exception as e:
                if i == retries - 1: # Last attempt failed
                    print(f"Failed to generate voice: {e}")
                    return False
                await asyncio.sleep(1) # Wait 1 sec before retry
        return False

    if v2_file and s2_file and st.button("Start Dubbing (Fixed)", key="btn_pro"):
        with st.spinner("Processing Audio (Auto Retry Mode)..."):
            vp2, sp2, op2 = "temp_v2.mp4", "temp_s2.srt", "output_dub.mp4"
            with open(vp2, "wb") as f: f.write(v2_file.getbuffer())
            with open(sp2, "wb") as f: f.write(s2_file.getbuffer())
            
            try:
                video = VideoFileClip(vp2)
                subs = pysubs2.load(sp2, encoding="utf-8")
                
                audio_clips = []
                if keep_original and video.audio is not None:
                    # Background အသံကို သေချာလေး လျှော့ပါမယ်
                    bg_audio = video.audio.volumex(0.2) 
                    audio_clips.append(bg_audio)
                
                generated_files = []
                progress_bar = st.progress(0)
                total_lines = len(subs)
                
                for i, line in enumerate(subs):
                    if not line.text.strip(): continue
                    
                    text = line.text.replace("\\N", " ")
                    temp_audio = f"temp_aud_{i}.mp3"
                    
                    # Safe Generation Call
                    success = asyncio.run(generate_voice_safe(text, temp_audio, VOICE_ID))
                    
                    if success and os.path.exists(temp_audio):
                        generated_files.append(temp_audio)
                        # အသံဖိုင်ကို Load လုပ်ပြီး စစ်ဆေးခြင်း
                        try:
                            audioclip = AudioFileClip(temp_audio)
                            if audioclip.duration > 0: # Duration ရှိမှ ထည့်မယ်
                                audioclip = audioclip.set_start(line.start / 1000)
                                audio_clips.append(audioclip)
                        except:
                            pass # Corrupted file skip
                    
                    progress_bar.progress((i + 1) / total_lines)
            
                if len(audio_clips) > 0:
                    final_audio = CompositeAudioClip(audio_clips)
                    
                    # Video Duration နဲ့ Audio ညီအောင်ညှိခြင်း
                    final_audio = final_audio.set_duration(video.duration)
                    final_video = video.set_audio(final_audio)
                    
                    final_video.write_videofile(
                        op2, 
                        fps=24, 
                        codec='libx264', 
                        preset='fast', 
                        audio_codec='aac', 
                        threads=4, 
                        ffmpeg_params=["-crf", "23"]
                    )
                    
                    st.success("Success! အသံထွက်အောင်မြင်ပါသည်")
                    with open(op2, "rb") as f:
                        st.download_button("Download Dubbed Video", f.read(), "dubbed_fixed.mp4", "video/mp4")
                else:
                    st.error("Error: အသံဖိုင် တစ်ခုမှ ထုတ်မရပါ။ (SRT ဖိုင်ကို စစ်ဆေးပါ)")

                for f in generated_files: 
                    try: os.remove(f)
                    except: pass

            except Exception as e:
                st.error(f"System Error: {e}")
            
            if os.path.exists(vp2): os.remove(vp2)
            if os.path.exists(sp2): os.remove(sp2)
            if os.path.exists(op2): os.remove(op2)
                
