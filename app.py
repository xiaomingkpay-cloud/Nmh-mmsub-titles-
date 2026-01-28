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
# 🎨 BACKGROUND SYSTEM (RAW GITHUB LINK)
# ==========================================
# ညီကို့ပုံရဲ့ Raw Link အမှန်
bg_url = "https://raw.githubusercontent.com/xiaomingkpay-cloud/Nmh-mmsub-titles-/main/IMG_20260128_234239_629.jpg"

st.markdown(
    f"""
    <style>
    .stApp {{
        /* ပုံကို အနောက်မှာ ထားခြင်း */
        background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), url("{bg_url}");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 🛡️ HARD LIMIT SYSTEM
# ==========================================
@st.cache_resource
def get_usage_tracker():
    return {"date": datetime.now().strftime("%Y-%m-%d"), "users": {}}

usage_tracker = get_usage_tracker()

current_date = datetime.now().strftime("%Y-%m-%d")
if usage_tracker["date"] != current_date:
    usage_tracker["date"] = current_date
    usage_tracker["users"] = {} 

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

tab1, tab2 = st.tabs(["Option 1: စာတန်းထိုး (Free - 3 Files/Day) 🆓", "Option 2: အသံထည့် (Pro Version) 🔐"])

# ==========================================
# OPTION 1: FREE VERSION
# ==========================================
with tab1:
    st.header("Option 1: Video ထဲသို့ မြန်မာစာတန်း အသေမြှုပ်ခြင်း (Free)")
    
    user_ip = get_remote_ip()
    if user_ip not in usage_tracker["users"]: usage_tracker["users"][user_ip] = 0
    usage_left = 3 - usage_tracker["users"][user_ip]
    
    if usage_left > 0:
        st.info(f"✅ ယနေ့အတွက် လက်ကျန်: {usage_left} ပုဒ် (Used: {usage_tracker['users'][user_ip]}/3)")
        st.caption(f"Your ID: {user_ip}")
    else:
        st.error("⛔ ယနေ့အတွက် Free Limit ပြည့်သွားပါပြီ! Pro Code ဝယ်ယူပါ။")

    col1, col2 = st.columns(2)
    with col1: v1_file = st.file_uploader("Video ဖိုင် (Sub)", type=["mp4", "mov", "avi"], key="v1")
    with col2: s1_file = st.file_uploader("SRT ဖိုင် (Sub)", type=["srt"], key="s1")

    def generate_subtitle_clips(subtitle_path, video_width, video_height, font_path):
        subs = pysubs2.load(subtitle_path, encoding="utf-8")
        subtitle_clips = []
        fontsize = int(video_width / 25)
        try: font = ImageFont.truetype(font_path, fontsize)
        except: font = ImageFont.load_default()

        for line in subs:
            if not line.text.strip(): continue
            text_w = int(video_width * 0.9)
            text_h = int(video_height * 0.25)
            img = Image.new('RGBA', (text_w, text_h), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            text_content = line.text.replace("\\N", "\n")
            try: draw.text((text_w/2, text_h/2), text_content, font=font, fill="white", stroke_width=3, stroke_fill="black", anchor="mm", align="center")
            except: draw.text((10, 10), text_content, font=font, fill="white", stroke_width=2, stroke_fill="black")
            clip = ImageClip(np.array(img)).set_start(line.start / 1000).set_duration((line.end - line.start) / 1000)
            clip = clip.set_position(('center', 0.80), relative=True)
            subtitle_clips.append(clip)
        return subtitle_clips

    if usage_left > 0:
        if v1_file and s1_file and st.button("စာတန်းမြှုပ်မည် (Start Burning)", key="btn_free"):
            with st.spinner("စာတန်းထည့်ပြီး ဖိုင်ချုံ့နေပါသည်..."):
                vp, sp, fp, op = "temp_v1.mp4", "temp_s1.srt", "myanmar_font.ttf", "output_sub.mp4"
                with open(vp, "wb") as f: f.write(v1_file.getbuffer())
                with open(sp, "wb") as f: f.write(s1_file.getbuffer())
                
                if not os.path.exists(fp):
                    st.error("GitHub တွင် 'myanmar_font.ttf' မရှိပါ။")
                else:
                    try:
                        video = VideoFileClip(vp)
                        sub_clips = generate_subtitle_clips(sp, video.w, video.h, fp)
                        final_video = CompositeVideoClip([video] + sub_clips)
                        
                        final_video.write_videofile(
                            op, fps=24, codec='libx264', preset='veryfast', 
                            audio_codec='aac', threads=4, ffmpeg_params=["-crf", "28"] 
                        )
                        
                        usage_tracker["users"][user_ip] += 1
                        st.success(f"ပြီးပါပြီ!")
                        with open(op, "rb") as f: st.download_button("Download Video", f.read(), "subbed_video.mp4", "video/mp4")
                    except Exception as e: st.error(f"Error: {e}")
                
                if os.path.exists(vp): os.remove(vp)
                if os.path.exists(sp): os.remove(sp)
                if os.path.exists(op): os.remove(op)
    else:
        st.warning("⛔ Limit ပြည့်သွားပါပြီ။")

# ==========================================
# OPTION 2: PRO VERSION
# ==========================================
with tab2:
    st.header("Option 2: Video အသံထည့်ခြင်း (Pro Member Only)")
    
    if "user_info" not in st.session_state: st.session_state.user_info = None
    if st.session_state.user_info is None:
        st.warning("🔒 Pro Code လိုအပ်ပါသည်။")
        col_pass1, _ = st.columns([3, 1])
        with col_pass1: token_input = st.text_input("Pro Access Token:", type="password", key="pro_token")
        if st.button("Login to Pro Mode"):
            if "users" in st.secrets and token_input in st.secrets["users"]:
                st.session_state.user_info = st.secrets["users"][token_input]
                st.rerun()
            else: st.error("Code မှားယွင်းနေပါသည်။")
        st.stop()

    st.success(f"✅ Pro Mode Active: {st.session_state.user_info}")
    if st.button("Logout"):
        st.session_state.user_info = None
        st.rerun()
    st.write("---")
    
    col3, col4 = st.columns(2)
    with col3: v2_file = st.file_uploader("Video ဖိုင် (Dub)", type=["mp4", "mov", "avi"], key="v2")
    with col4: s2_file = st.file_uploader("SRT ဖိုင် (Dub)", type=["srt"], key="s2")
    
    voice_option = st.selectbox("အသံရွေးချယ်ပါ", ("Female (Thiri)", "Male (Sai Nyi)"))
    VOICE_ID = "my-MM-ThiriNeural" if "Female" in voice_option else "my-MM-SaiNyiNeural"
    keep_original = st.checkbox("မူရင်း Video အသံကို မဖျက်ဘဲထားမည်", value=False)

    async def generate_voice(text, output_file, voice_id):
        communicate = edge_tts.Communicate(text, voice_id)
        await communicate.save(output_file)

    if v2_file and s2_file and st.button("အသံထည့်မည် (Start Dubbing)", key="btn_pro"):
        with st.spinner(f"အသံထည့်ပြီး ဖိုင်ချုံ့နေပါသည်..."):
            vp2, sp2, op2 = "temp_v2.mp4", "temp_s2.srt", "output_dub.mp4"
            with open(vp2, "wb") as f: f.write(v2_file.getbuffer())
            with open(sp2, "wb") as f: f.write(s2_file.getbuffer())
            
            try:
                video = VideoFileClip(vp2)
                subs = pysubs2.load(sp2, encoding="utf-8")
                audio_clips = []
                if keep_original and video.audio is not None:
                    audio_clips.append(video.audio.volumex(0.3))
                
                generated_files = []
                progress_bar = st.progress(0)
                for i, line in enumerate(subs):
                    if not line.text.strip(): continue
                    text = line.text.replace("\\N", " ")
                    temp_audio = f"temp_aud_{i}.mp3"
                    asyncio.run(generate_voice(text, temp_audio, VOICE_ID))
                    generated_files.append(temp_audio)
                    if os.path.exists(temp_audio):
                        audioclip = AudioFileClip(temp_audio).set_start(line.start / 1000)
                        audio_clips.append(audioclip)
                    progress_bar.progress((i + 1) / len(subs))
            
                final_video = video.set_audio(CompositeAudioClip(audio_clips))
                final_video.write_videofile(
                    op2, fps=24, codec='libx264', preset='veryfast', 
                    audio_codec='aac', threads=4, ffmpeg_params=["-crf", "28"]
                )
                
                st.success("ပြီးပါပြီ!")
                with open(op2, "rb") as f: st.download_button("Download Video", f.read(), "myanmar_dubbed.mp4", "video/mp4")
                for f in generated_files: os.remove(f)
            except Exception as e: st.error(f"Error: {e}")
            if os.path.exists(vp2): os.remove(vp2)
            if os.path.exists(sp2): os.remove(sp2)
            if os.path.exists(op2): os.remove(op2)
            
