import streamlit as st
import os
import pysubs2
from datetime import datetime
from streamlit.web.server.websocket_headers import _get_websocket_headers
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip
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
st.success("📢 Manual Workflow: Error Free & High Quality Audio")

# TAB 4 ခု (ညီကိုလိုချင်တဲ့ ပုံစံအတိုင်း)
tab1, tab2, tab3, tab4 = st.tabs([
    "Tab 1: 🌐 Get SRT", 
    "Tab 2: 📝 Burn Sub (Free)", 
    "Tab 3: 🗣️ Get Audio (Google Studio)", 
    "Tab 4: 🎬 Merge Video & Audio (Final)"
])

# ==========================================
# TAB 1: GEMINI SRT (TEXT ONLY)
# ==========================================
with tab1:
    st.header("အဆင့် ၁ - Gemini မှ SRT စာသားတောင်းယူပါ")
    st.link_button("🚀 Go to Google Gemini Chat", "https://gemini.google.com/")
    st.info("Prompt: 'Generate Myanmar SRT file for this video...'")
    srt_text_input = st.text_area("Gemini မှပေးလိုက်သော SRT စာသားများကို ဒီအကွက်ထဲ Paste ချပါ:", height=300)
    if srt_text_input and st.button("SRT ဖိုင်အဖြစ် ပြောင်းမည်"):
        clean_text = srt_text_input.replace("```srt", "").replace("```", "").strip()
        output_srt = "manual_converted.srt"
        with open(output_srt, "w", encoding="utf-8") as f: f.write(clean_text)
        st.success("✅ SRT ဖိုင် ရရှိပါပြီ!")
        with open(output_srt, "rb") as f: st.download_button("Download SRT", f.read(), "myanmar.srt", "text/plain")

# ==========================================
# TAB 2: BURN SUBTITLE (FREE)
# ==========================================
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

    # Simple Subtitle Logic
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
            
            if not os.path.exists(fp): st.error("Font Missing! (myanmar_font.ttf)")
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
# TAB 3: GOOGLE AI STUDIO LINK (MANUAL AUDIO)
# ==========================================
with tab3:
    st.header("Tab 3: အသံဖိုင်ထုတ်လုပ်ရန် (Audio Generation)")
    st.info("အောက်ပါခလုတ်ကို နှိပ်ပြီး Google AI Studio တွင် စာရိုက်ထည့်ကာ အသံဖိုင်ဒေါင်းယူပါ။")
    
    # Direct Link to Google AI Studio
    # AI Studio တွင် Text to Speech နေရာသို့ တန်းရောက်မည့် Link
    st.link_button("🚀 Go to Google AI Studio (Speech Tool)", "https://aistudio.google.com/")
    
    st.markdown("""
    **လုပ်ဆောင်ရမည့်အဆင့်များ:**
    1. အပေါ်က ခလုတ်ကို နှိပ်ပါ။
    2. Google AI Studio တွင် **"Speech"** သို့မဟုတ် **"Generate Audio"** ကိုရွေးပါ။
    3. SRT ထဲမှ စာများကို Copy ကူးထည့်ပါ။
    4. Voice နေရာတွင် **Zephyr** သို့မဟုတ် **Charon** (ကြိုက်နှစ်သက်ရာ) ကိုရွေးပါ။
    5. **Download** လုပ်ပြီး ရလာတဲ့ အသံဖိုင်ကို **Tab 4** တွင် သုံးပါ။
    """)

# ==========================================
# TAB 4: MANUAL MERGE (VIDEO + AUDIO)
# ==========================================
with tab4:
    st.header("Tab 4: Video နှင့် အသံဖိုင် ပေါင်းစပ်ခြင်း (Final Step)")
    
    if "user_info" not in st.session_state: st.session_state.user_info = None
    
    # --- LOGIN SYSTEM ---
    if st.session_state.user_info is None:
        st.warning("🔒 Pro Feature Locked.")
        col_pass1, _ = st.columns([3, 1])
        with col_pass1: token_input = st.text_input("Pro Access Token:", type="password", key="pro_token_t4")
        
        if st.button("Login to Pro Mode", key="btn_login_t4"):
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
    if st.button("Logout", key="out_t4"):
        st.session_state.user_info = None
        st.rerun()
    st.write("---")

    col_v, col_a = st.columns(2)
    with col_v:
        video_input = st.file_uploader("၁။ Video ဖိုင် ရွေးပါ", type=["mp4", "mov", "avi"], key="vid_merge")
    with col_a:
        audio_input = st.file_uploader("၂။ အသံဖိုင် (Tab 3 မှ ဒေါင်းလာသောဖိုင်)", type=["mp3", "wav", "m4a"], key="aud_merge")

    keep_original_bg = st.checkbox("မူရင်း Video အသံကို မဖျက်ဘဲထားမည် (Background အသံအဖြစ်)", value=True, key="bg_check_t4")

    if video_input and audio_input and st.button("Video နှင့် အသံ ပေါင်းမည် (Merge)", key="btn_merge"):
        with st.spinner("Processing..."):
            t4_vid = "temp_merge_v.mp4"
            t4_aud = "temp_merge_a.mp3"
            t4_out = "output_merged.mp4"

            with open(t4_vid, "wb") as f: f.write(video_input.getbuffer())
            with open(t4_aud, "wb") as f: f.write(audio_input.getbuffer())

            try:
                video_clip = VideoFileClip(t4_vid)
                new_audio_clip = AudioFileClip(t4_aud)
                
                # အသံဖိုင် Duration ကို Video နဲ့ ညီအောင်ညှိခြင်း
                if new_audio_clip.duration > video_clip.duration:
                    new_audio_clip = new_audio_clip.subclip(0, video_clip.duration)

                final_audio = None
                if keep_original_bg and video_clip.audio is not None:
                    # မူရင်းအသံကို ၁၀% လျှော့
                    bg_audio = video_clip.audio.volumex(0.1)
                    final_audio = CompositeAudioClip([bg_audio, new_audio_clip])
                else:
                    final_audio = new_audio_clip

                final_video = video_clip.set_audio(final_audio)
                
                final_video.write_videofile(
                    t4_out, 
                    fps=24, 
                    codec='libx264', 
                    preset='fast', 
                    audio_codec='aac', 
                    threads=4, 
                    ffmpeg_params=["-crf", "23"]
                )

                st.success("✅ အောင်မြင်ပါသည်!")
                with open(t4_out, "rb") as f:
                    st.download_button("Download Final Video", f.read(), "merged_video.mp4", "video/mp4")

            except Exception as e: st.error(f"Error: {e}")
            
            if os.path.exists(t4_vid): os.remove(t4_vid)
            if os.path.exists(t4_aud): os.remove(t4_aud)
            if os.path.exists(t4_out): os.remove(t4_out)

