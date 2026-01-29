import os
import sys

# --- EMERGENCY POLICY FIX (Re-deploy မလုပ်ဘဲ Error ရှင်းရန်) ---
def fix_policy():
    try:
        policy_path = "/etc/ImageMagick-6/policy.xml"
        if os.path.exists(policy_path):
            with open(policy_path, 'r') as f:
                content = f.read()
            # စာသားထုတ်ခွင့်ကို အတင်းဖွင့်ပေးခြင်း
            new_content = content.replace('rights="none" pattern="PDF"', 'rights="read|write" pattern="PDF"')
            new_content = new_content.replace('rights="none" pattern="LABEL"', 'rights="read|write" pattern="LABEL"')
            # သီးသန့် နေရာတစ်ခုတွင် သိမ်းဆည်းပြီး စနစ်ကို ညွှန်ကြားခြင်း
            with open("policy.xml", "w") as f:
                f.write(new_content)
            os.environ["MAGICK_CONFIGURE_PATH"] = os.getcwd()
    except:
        pass

fix_policy()

import streamlit as st
import textwrap
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip

# NMH PRO CREATOR TOOLS UI
st.set_page_config(page_title="NMH Pro Creator Tools", layout="wide")
st.title("✨ NMH Pro Creator Tools")

tab1, tab2, tab3, tab4 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (FREE/VIP)", "🗣️ အသံထုတ်ရန် (VIP)", "🎬 Video ပေါင်းရန် (VIP)"])

# --- Tab 1: SRT Helper (ပြန်ထည့်ပေးထားသည်) ---
with tab1:
    st.header("🌐 Gemini မှတစ်ဆင့် SRT ထုတ်ယူခြင်း")
    st.info("ဒီဗီဒီယိုအတွက် မြန်မာ SRT ထုတ်ပေးပါ")
    st.link_button("🤖 Gemini သို့သွားရန်", "https://gemini.google.com/")
    srt_content = st.text_area("SRT Paste Here", height=150)
    if srt_content:
        st.download_button("📥 Download SRT", srt_content, file_name="subtitle.srt")

# --- Tab 2: စာတန်းမြှုပ်ခြင်း (Improved Logic) ---
def create_subtitle_generator(video_width, video_height, is_portrait):
    char_limit = 35 if is_portrait else 50
    margin_pct = 0.40 if is_portrait else 0.30
    bottom_pos = video_height * (1 - margin_pct)

    def gen(txt):
        wrapped_txt = textwrap.fill(txt, width=char_limit)
        return TextClip(
            wrapped_txt,
            font='myanmar_font.ttf', 
            fontsize=35 if is_portrait else 45,
            color='white',
            bg_color='black', 
            method='caption',
            size=(video_width * 0.85, None)
        ).set_position(('center', bottom_pos))
    return gen

with tab2:
    v_file = st.file_uploader("ဗီဒီယိုဖိုင် တင်ပါ", type=["mp4", "mov"])
    s_file = st.file_uploader("SRT ဖိုင် တင်ပါ", type=["srt"])

    if v_file and s_file:
        if st.button("🚀 Render Video"):
            try:
                with st.spinner('Render လုပ်နေသည်...'):
                    with open("temp_v.mp4", "wb") as f: f.write(v_file.read())
                    with open("temp_s.srt", "wb") as f: f.write(s_file.read())
                    
                    clip = VideoFileClip("temp_v.mp4")
                    sub_gen = create_subtitle_generator(clip.w, clip.h, clip.w < clip.h)
                    
                    subtitles = SubtitlesClip("temp_s.srt", sub_gen)
                    final_video = CompositeVideoClip([clip, subtitles])
                    
                    output = "NMH_Result.mp4"
                    final_video.write_videofile(output, fps=clip.fps, codec="libx264", audio_codec="aac")
                    st.video(output)
                    st.download_button("📥 Download Result", open(output, "rb"), file_name="NMH_Subtitled.mp4")
            except Exception as e:
                st.error(f"Render Error: {str(e)}")

