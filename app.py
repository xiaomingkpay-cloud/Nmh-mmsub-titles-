import streamlit as st
import os
import pysubs2
import numpy as np
import asyncio
import edge_tts
import google.generativeai as genai
import time
from datetime import datetime
from streamlit.web.server.websocket_headers import _get_websocket_headers
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip
from PIL import Image, ImageDraw, ImageFont

# Website ခေါင်းစဉ်
st.set_page_config(page_title="NMH Pro Creator Mood", layout="wide")

# ==========================================
# 🔑 GEMINI API SETUP
# ==========================================
# ညီကိုပေးသော API Key ကို ထည့်သွင်းထားသည်
GEMINI_API_KEY = "AIzaSyC4OgI6aCHEnP51BuzGr5T3ug8buR4wlsQ"
genai.configure(api_key=GEMINI_API_KEY)

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
tab1, tab2, tab3 = st.tabs(["Tab 1: 🤖 Auto SRT (AI)", "Tab 2: 📝 စာတန်းမြှုပ် (Free)", "Tab 3: 🗣️ အသံထည့် (Pro)"])

# ==========================================
# TAB 1: AUTO SUBTITLE GENERATOR (GEMINI)
# ==========================================
with tab1:
    st.header("🤖 AI ဖြင့် မြန်မာစာတန်း (SRT) အလိုအလျောက်ထုတ်ယူခြင်း")
    st.info("Video တင်လိုက်ပါ၊ AI က စကားပြောများကို နားထောင်ပြီး SRT ဖိုင် ထုတ်ပေးပါမည်။")

    gen_video = st.file_uploader("Video ဖိုင်တင်ပါ (To Generate SRT)", type=["mp4", "mov", "avi"], key="gen_v")

    if gen_video and st.button("Generate Myanmar SRT Now 🚀"):
        with st.spinner("AI သို့ Video ပို့ဆောင်နေပါသည် (ခဏစောင့်ပါ)..."):
            # Save Temp Video
            temp_gen_path = "temp_gen.mp4"
            with open(temp_gen_path, "wb") as f: f.write(gen_video.getbuffer())

            try:
                # 1. Upload to Gemini
                video_file = genai.upload_file(path=temp_gen_path)
                
                # 2. Wait for processing
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)

                if video_file.state.name == "FAILED":
                    st.error("AI မှ Video ကို ဖတ်မရပါ။ Video ဖိုင် ပျက်နေနိုင်ပါသည်။")
                else:
                    # 3. Generate Content
                    st.info("AI မှ Video ကို နားထောင်ပြီး စာရေးနေပါသည်...")
                    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                    
                    prompt = """
                    Listen to the video carefully. Generate a subtitle file in SRT format for the Burmese (Myanmar) speech.
                    Ensure the timestamps are accurate.
                    Do not include any intro or outro text.
                    Output ONLY the SRT content.
                    """
                    
                    response = model.generate_content([video_file, prompt], request_options={"timeout": 600})
                    srt_content = response.text

                    # 4. Save & Download
                    output_srt = "generated_subtitle.srt"
                    # Clean up ```srt markdown if exists
                    srt_content = srt_content.replace("```srt", "").replace("```", "").strip()
                    
                    with open(output_srt, "w", encoding="utf-8") as f:
                        f.write(srt_content)
                    
                    st.success("✅ SRT ဖိုင် ရရှိပါပြီ! အောက်တွင် Download လုပ်ပါ။")
                    with open(output_srt, "rb") as f:
                        st.download_button("Download SRT File", f.read(), "myanmar.srt", "text/plain")
                        
                    # Cleanup Cloud File
                    genai.delete_file(video_file.name)

            except Exception as e:
                st.error(f"Error: {e}")
            
            if os.path.exists(temp_gen_path): os.remove(temp_gen_path)

# ==========================================
# TAB 2: BURN SUBTITLE (FREE LIMIT)
# ==========================================
with tab2:
    st.header("Tab 2: ရလာသော SRT ကို Video တွင် မြန်မာစာတန်းထိုးခြင်း")
    
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

    if usage_left > 0 and v1_file and s1_file and st.button("မြန်မာစာတန်းထိုးမည် (Start Burning)", key="btn_free"):
        with st.spinner("Processing..."):
            vp, sp, fp, op = "temp_v1.mp4", "temp_s1.srt", "myanmar_font.ttf", "output_sub.mp4"
            with open(vp, "wb") as f: f.write(v1_file.getbuffer())
            with open(sp, "wb") as f: f.write(s1_file.getbuffer())
            
            if not os.path.exists(fp): st.error("GitHub တွင် 'myanmar_font.ttf' မရှိပါ။ Font ဖိုင်တင်ပေးပါ။")
            else:
                try:
                    video = VideoFileClip(vp)
                    sub_clips = generate_subtitle_clips(sp, video.w, video.h, fp)
                    final_video = CompositeVideoClip([video] + sub_clips)
                    final_video.write_videofile(op, fps=24, codec='libx264', preset='veryfast', audio_codec='aac', threads=4, ffmpeg_params=["-crf", "28"])
                    
                    usage_data["users"][user_ip] += 1
                    st.success("Success!")
                    with open(op, "rb") as f: st.download_button("Download Video", f.read(), "subbed_video.mp4", "video/mp4")
                except Exception as e: st.error(f"Error: {e}")
            if os.path.exists(vp): os.remove(vp)
            if os.path.exists(sp): os.remove(sp)
            if os.path.exists(op): os.remove(op)

# ==========================================
# TAB 3: PRO VERSION (AI DUBBING)
# ==========================================
with tab3:
    st.header("Tab 3: Video မြန်မာစကား‌ပြောထည့်ခြင်း (Pro Member)")
    
    if "user_info" not in st.session_state: st.session_state.user_info = None
    
    if st.session_state.user_info is None:
        st.warning("🔒 Feature Locked. (1 Code = 1 Device Only)")
        col_pass1, _ = st.columns([3, 1])
        with col_pass1: token_input = st.text_input("Pro Access Token:", type="password", key="pro_token")
        
        if st.button("Login"):
            if "users" in st.secrets and token_input in st.secrets["users"]:
                current_ip = get_remote_ip()
                # Admin Code (No Lock)
                if token_input == "nmh-123": 
                    st.session_state.user_info = st.secrets["users"][token_input]
                    st.rerun()
                # User Code (Device Lock)
                else:
                    if token_input not in usage_data["bindings"]:
                        usage_data["bindings"][token_input] = current_ip
                        st.session_state.user_info = st.secrets["users"][token_input]
                        st.rerun()
                    elif usage_data["bindings"][token_input] == current_ip:
                        st.session_state.user_info = st.secrets["users"][token_input]
                        st.rerun()
                    else: st.error("⛔ This code is locked to another device!")
            else: st.error("Invalid Code")
        st.stop()

    st.success(f"✅ Welcome {st.session_state.user_info}")
    
    # Admin Panel
    if "Admin" in st.session_state.user_info:
        with st.expander("🛠️ Admin Tools"):
            if st.button("Reset All Device Locks"):
                usage_data["bindings"] = {}
                st.success("Locks Reset!")
                st.rerun()
    
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
        with st.spinner("Processing..."):
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
                final_video.write_videofile(op2, fps=24, codec='libx264', preset='veryfast', audio_codec='aac', threads=4, ffmpeg_params=["-crf", "28"])
                st.success("Success!")
                with open(op2, "rb") as f: st.download_button("Download Dubbed Video", f.read(), "dubbed.mp4", "video/mp4")
                for f in generated_files: os.remove(f)
            except Exception as e: st.error(f"Error: {e}")
            if os.path.exists(vp2): os.remove(vp2)
            if os.path.exists(sp2): os.remove(sp2)
            if os.path.exists(op2): os.remove(op2)
                
