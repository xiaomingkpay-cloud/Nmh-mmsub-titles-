import os
# ImageMagick policy ကို Cloud ပေါ်မှာ အလုပ်လုပ်အောင် သတ်မှတ်ခြင်း (Security Error ရှင်းရန်)
os.environ["MAGICK_CONFIGURE_PATH"] = os.getcwd()

import streamlit as st
import textwrap
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip

# Page configuration
st.set_page_config(page_title="NMH Pro Creator Tools", layout="wide")

# Header Section
st.title("✨ NMH Pro Creator Tools")
st.markdown("### 👨‍💻 Developed by Naing Min Htet")

tab1, tab2, tab3, tab4 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (FREE/VIP)", "🗣️ အသံထုတ်ရန် (VIP)", "🎬 Video ပေါင်းရန် (VIP)"])

# --- Tab 2: SRT file ကို Video ပေါ်စာတန်းထိုးခြင်း ---
def wrap_text(text, width):
    return textwrap.fill(text, width=width)

def create_subtitle_generator(video_width, video_height, is_portrait):
    char_limit = 35 if is_portrait else 50
    margin_pct = 0.40 if is_portrait else 0.30
    bottom_pos = video_height * (1 - margin_pct)

    def gen(txt):
        wrapped_txt = wrap_text(txt, char_limit)
        return TextClip(
            wrapped_txt,
            font='myanmar_font.ttf', # font နာမည်မှန်ပါစေ
            fontsize=35 if is_portrait else 45,
            color='white',
            bg_color='black', 
            method='caption',
            size=(video_width * 0.85, None)
        ).set_position(('center', bottom_pos))
    return gen

with tab2:
    st.header("📝 မြန်မာစာတန်းထိုး Video ထုတ်ယူခြင်း")
    v_file = st.file_uploader("ဗီဒီယိုဖိုင် တင်ပါ", type=["mp4", "mov"], key="v2_up")
    s_file = st.file_uploader("SRT ဖိုင် တင်ပါ", type=["srt"], key="s2_up")

    if v_file and s_file:
        if st.button("🚀 Render Video"):
            try:
                with st.spinner('ဗီဒီယိုကို ဖန်တီးနေသည်... ခေတ္တစောင့်ပါ'):
                    with open("temp_v.mp4", "wb") as f: f.write(v_file.read())
                    with open("temp_s.srt", "wb") as f: f.write(s_file.read())
                    
                    clip = VideoFileClip("temp_v.mp4")
                    is_portrait = clip.w < clip.h
                    sub_gen = create_subtitle_generator(clip.w, clip.h, is_portrait)
                    
                    subtitles = SubtitlesClip("temp_s.srt", sub_gen)
                    final_video = CompositeVideoClip([clip, subtitles])
                    
                    output_path = "NMH_Subtitled.mp4"
                    final_video.write_videofile(output_path, fps=clip.fps, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True)
                    
                    st.success("အောင်မြင်ပါသည်!")
                    st.video(output_path)
            except Exception as e:
                st.error(f"Error: {str(e)}")
                
