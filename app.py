import streamlit as st
import os
import pysubs2
import numpy as np
import google.generativeai as genai
from datetime import datetime
from streamlit.web.server.websocket_headers import _get_websocket_headers
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from pydub import AudioSegment

# Website ခေါင်းစဉ်
st.set_page_config(page_title="NMH Pro Creator Mood", layout="wide")

# ==========================================
# 🔑 GEMINI API (Tab 1)
# ==========================================
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY" # ညီကို့ Key ထည့်ပါ
if GEMINI_API_KEY != "YOUR_GEMINI_API_KEY":
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

tab1, tab2, tab3 = st.tabs(["Tab 1: 🌐 Get SRT (Gemini)", "Tab 2: 📝 စာတန်းမြှုပ် (Free)", "Tab 3: 🗣️ အသံထည့် (Turbo Voice)"])

# ==========================================
# TAB 1 & 2 (ပုံမှန်အတိုင်း)
# ==========================================
with tab1:
    st.header("အဆင့် ၁ - Gemini မှ SRT စာသားတောင်းယူပါ")
    st.link_button("🚀 Go to Google Gemini App/Web", "https://gemini.google.com/")
    st.write("Gemini တွင် 'Generate Myanmar SRT file for this video' ဟု ရေးပြီး တောင်းပါ။")
    st.write("---")
    st.header("အဆင့် ၂ - ရလာသော စာသားကို SRT ဖိုင်ပြောင်းပါ")
    srt_text_input = st.text_area("Gemini မှပေးလိုက်သော SRT စာသားများကို ဒီအကွက်ထဲ Paste ချပါ:", height=300)
    
    if srt_text_input and st.button("SRT ဖိုင်အဖြစ် ပြောင်းမည်"):
        clean_text = srt_text_input.replace("```srt", "").replace("```", "").strip()
        output_srt = "manual_converted.srt"
        with open(output_srt, "w", encoding="utf-8") as f: f.write(clean_text)
        st.success("✅ SRT ဖိုင် ရရှိပါပြီ!")
        with open(output_srt, "rb") as f: st.download_button("Download SRT", f.read(), "myanmar.srt", "text/plain")

with tab2:
    st.header("Tab 2: စာတန်းမြှုပ်ခြင်း (Free)")
    user_ip = get_remote_ip()
    if user_ip not in usage_data["users"]: usage_data["users"][user_ip] = 0
    usage_left = 3 - usage_data["users"][user_ip]
    if usage_left > 0: st.info(f"✅ Free Limit: {usage_left}/3 left")
    else: st.error("⛔ Limit Reached")

    col1, col2 = st.columns(2)
    with col1: v1_file = st.file_uploader("Video", type=["mp4", "mov"], key="v1")
    with col2: s1_file = st.file_uploader("SRT", type=["srt"], key="s1")

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

    if usage_left > 0 and v1_file and s1_file and st.button("စာတန်းမြှုပ်မည်", key="btn_free"):
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
# TAB 3: PRO VERSION (TURBO GOOGLE VOICE)
# ==========================================
with tab3:
    st.header("Tab 3: Video အသံထည့်ခြင်း (Pro - Turbo Speed)")
    
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
            else: st.error("Code Invalid")
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
    with col3: v2_file = st.file_uploader("Video (Dub)", type=["mp4", "mov"], key="v2")
    with col4: s2_file = st.file_uploader("SRT (Dub)", type=["srt"], key="s2")
    
    # Speed Control
    speed_option = st.select_slider("စကားပြောနှုန်း ရွေးချယ်ပါ (Voice Speed)", 
                                    options=["Normal (1.0x)", "Fast (1.25x)", "Super Fast (1.5x)"], 
                                    value="Fast (1.25x)")
    
    keep_original = st.checkbox("Keep Original Audio (Background)", value=True)

    # --- TURBO VOICE FUNCTION ---
    def generate_turbo_voice(text, output_file, speed_mode):
        try:
            # 1. Generate Normal Google Voice
            temp_slow = "temp_slow.mp3"
            tts = gTTS(text=text, lang='my')
            tts.save(temp_slow)
            
            # 2. Speed It Up using Pydub
            sound = AudioSegment.from_file(temp_slow)
            
            if speed_mode == "Fast (1.25x)":
                # Speed up by 1.25 times
                sound = sound.speedup(playback_speed=1.25)
            elif speed_mode == "Super Fast (1.5x)":
                sound = sound.speedup(playback_speed=1.5)
            
            # 3. Export Final
            sound.export(output_file, format="mp3")
            
            if os.path.exists(temp_slow): os.remove(temp_slow)
            return True
        except Exception as e:
            print(f"Turbo Error: {e}")
            return False

    if v2_file and s2_file and st.button("Start Dubbing (Turbo Mode)", key="btn_pro"):
        with st.spinner("အသံသွင်းနေပါသည် (Turbo Mode - No Error)..."):
            vp2, sp2, op2 = "temp_v2.mp4", "temp_s2.srt", "output_dub.mp4"
            with open(vp2, "wb") as f: f.write(v2_file.getbuffer())
            with open(sp2, "wb") as f: f.write(s2_file.getbuffer())
            
            try:
                video = VideoFileClip(vp2)
                subs = pysubs2.load(sp2, encoding="utf-8")
                
                audio_clips = []
                if keep_original and video.audio is not None:
                    # မူရင်းအသံကို ၁၀% ထိ လျှော့ချခြင်း
                    bg_audio = video.audio.volumex(0.1)
                    audio_clips.append(bg_audio)
                
                generated_files = []
                progress_bar = st.progress(0)
                total_lines = len(subs)
                success_count = 0

                for i, line in enumerate(subs):
                    if not line.text.strip(): continue
                    
                    text = line.text.replace("\\N", " ").replace('"', '')
                    temp_audio = f"temp_aud_{i}.mp3"
                    
                    # Call Turbo Function
                    is_success = generate_turbo_voice(text, temp_audio, speed_option)
                    
                    if is_success and os.path.exists(temp_audio):
                        generated_files.append(temp_audio)
                        try:
                            audioclip = AudioFileClip(temp_audio)
                            audioclip = audioclip.set_start(line.start / 1000)
                            audio_clips.append(audioclip)
                            success_count += 1
                        except: pass
                    
                    progress_bar.progress((i + 1) / total_lines)
            
                if success_count > 0:
                    final_audio = CompositeAudioClip(audio_clips)
                    
                    # Video Duration ထက် မပိုစေရန် ဖြတ်တောက်ခြင်း
                    if final_audio.duration > video.duration:
                        final_audio = final_audio.subclip(0, video.duration)
                    else:
                        final_audio = final_audio.set_duration(video.duration)
                        
                    final_video = video.set_audio(final_audio)
                    
                    final_video.write_videofile(
                        op2, fps=24, codec='libx264', preset='fast', 
                        audio_codec='aac', threads=4, ffmpeg_params=["-crf", "23"]
                    )
                    
                    st.success(f"Success! (Created {success_count} lines with {speed_option})")
                    with open(op2, "rb") as f: st.download_button("Download Dubbed Video", f.read(), "dubbed_turbo.mp4", "video/mp4")
                else:
                    st.error("Error: SRT ဖိုင်တွင် စာသားမရှိပါ သို့မဟုတ် ဖတ်မရပါ။")

                for f in generated_files: 
                    if os.path.exists(f): os.remove(f)

            except Exception as e: st.error(f"System Error: {e}")
            
            if os.path.exists(vp2): os.remove(vp2)
            if os.path.exists(sp2): os.remove(sp2)
            if os.path.exists(op2): os.remove(op2)
                        
