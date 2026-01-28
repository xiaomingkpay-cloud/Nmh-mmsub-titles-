import streamlit as st
import os
import pysubs2
import numpy as np
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="NMH Subtitle Fixer", layout="wide")
st.title("🎬 NMH Pro Video Subtitler (Myanmar Layout Fix)")
st.write("စာလုံးကွဲပြဿနာကို ဖြေရှင်းထားသော စနစ်သစ်")

# --- UI ---
col1, col2 = st.columns(2)
with col1:
    video_file = st.file_uploader("Video ဖိုင်", type=["mp4", "mov", "avi"])
with col2:
    srt_file = st.file_uploader("SRT ဖိုင်", type=["srt"])

def generate_subtitle_clips(subtitle_path, video_width, video_height, font_path):
    subs = pysubs2.load(subtitle_path, encoding="utf-8")
    subtitle_clips = []
    
    # Font Size ကို Video အရွယ်အစားပေါ်မူတည်ပြီး ချိန်ညှိခြင်း
    fontsize = int(video_width / 20)  
    try:
        font = ImageFont.truetype(font_path, fontsize)
    except:
        st.error("Font file loading failed. Using default.")
        font = ImageFont.load_default()

    for line in subs:
        # စာသားမရှိရင် ကျော်သွားမယ်
        if not line.text.strip():
            continue

        # 1. စာသားအတွက် ပုံရိပ် (Image) တစ်ခု ဖန်တီးမယ် (Transparent Background)
        # စာသားအရှည်ပေါ်မူတည်ပြီး ပုံအရွယ်အစား ခန့်မှန်းမယ်
        text_w = int(video_width * 0.9)
        text_h = int(video_height * 0.2)
        
        # PIL Image ဖန်တီးခြင်း
        img = Image.new('RGBA', (text_w, text_h), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # စာသား ရေးဆွဲခြင်း (Outline ပါထည့်ပေးမယ် ထင်းအောင်လို့)
        text_content = line.text.replace("\\N", "\n") # Line break တွေကို ပြင်မယ်
        
        # စာသားအလယ်တည့်တည့်ကျအောင် တွက်ချက်ခြင်း (Simple calculation)
        # PIL မှာ textbbox က အတိအကျရပေမယ့် version ပေါ်မူတည်လို့ anchor='mm' သုံးပါမယ်
        try:
            draw.text((text_w/2, text_h/2), text_content, font=font, fill="white", stroke_width=3, stroke_fill="black", anchor="mm", align="center")
        except:
            # Anchor မရတဲ့ PIL version အဟောင်းတွေအတွက်
            draw.text((10, 10), text_content, font=font, fill="white", stroke_width=2, stroke_fill="black")

        # 2. MoviePy ImageClip အဖြစ် ပြောင်းလဲခြင်း
        # np.array သုံးပြီး PIL image ကို MoviePy နားလည်အောင် ပြောင်းမယ်
        clip = ImageClip(np.array(img)).set_start(line.start / 1000).set_duration((line.end - line.start) / 1000)
        
        # 3. နေရာချခြင်း (အောက်ခြေနား)
        clip = clip.set_position(('center', 0.85), relative=True)
        subtitle_clips.append(clip)
        
    return subtitle_clips

# --- Processing ---
if video_file and srt_file:
    if st.button("Start Burning (စာတန်းကပ်မည်)"):
        with st.spinner("Video ကို Frame တစ်ခုချင်းစီ စီစစ်ပြီး စာတန်းကပ်နေပါသည် (အချိန်အနည်းငယ် ကြာနိုင်ပါသည်)..."):
            
            # Save Temp Files
            v_path = "temp_video.mp4"
            s_path = "temp.srt"
            f_path = "myanmar_font.ttf"
            out_path = "final_output.mp4"
            
            with open(v_path, "wb") as f: f.write(video_file.getbuffer())
            with open(s_path, "wb") as f: f.write(srt_file.getbuffer())
            
            # Font Check
            if not os.path.exists(f_path):
                st.error("GitHub တွင် 'myanmar_font.ttf' မရှိပါ။ Font ဖိုင် အရင်တင်ပါ။")
                st.stop()
                
            try:
                # Video Load
                video = VideoFileClip(v_path)
                
                # Subtitles Generate
                st.info("စာတန်းများကို ပုံဖော်နေပါသည်...")
                sub_clips = generate_subtitle_clips(s_path, video.w, video.h, f_path)
                
                # Combine
                st.info("Video နှင့် ပေါင်းစပ်နေပါသည်...")
                final_video = CompositeVideoClip([video] + sub_clips)
                
                # Write File
                # fps=24 သို့မဟုတ် video.fps (မြန်အောင် preset='ultrafast' သုံးထားသည်)
                final_video.write_videofile(out_path, fps=video.fps or 24, codec='libx264', preset='ultrafast', audio_codec='aac')
                
                st.success("အောင်မြင်ပါသည်!")
                
                with open(out_path, "rb") as f:
                    st.download_button("Download Video", f.read(), "mm_sub_fixed.mp4", "video/mp4")
                    
            except Exception as e:
                st.error(f"Error: {e}")
            
            # Cleanup
            if os.path.exists(v_path): os.remove(v_path)
            if os.path.exists(s_path): os.remove(s_path)
            if os.path.exists(out_path): os.remove(out_path)

