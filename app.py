import streamlit as st
import os
import pysubs2
import numpy as np
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="NMH Subtitle Fixer", layout="wide")
st.title("🎬 NMH Pro Vid Mode 🚀 )")
st.write("မြန်မာစာလုံး အမှန်ထွက်ပြီး ပိုမြန်အောင် ပြုလုပ်ထားသော ဗားရှင်း")

# --- UI ---
col1, col2 = st.columns(2)
with col1:
    video_file = st.file_uploader("Video ဖိုင်", type=["mp4", "mov", "avi"])
with col2:
    srt_file = st.file_uploader("SRT ဖိုင်", type=["srt"])

def generate_subtitle_clips(subtitle_path, video_width, video_height, font_path):
    subs = pysubs2.load(subtitle_path, encoding="utf-8")
    subtitle_clips = []
    
    # Font Size (Video အကျယ်ရဲ့ ၂၅ ပုံ ၁ ပုံ)
    fontsize = int(video_width / 25)  
    try:
        font = ImageFont.truetype(font_path, fontsize)
    except:
        font = ImageFont.load_default()

    for line in subs:
        if not line.text.strip():
            continue

        text_w = int(video_width * 0.9)
        text_h = int(video_height * 0.25)
        
        img = Image.new('RGBA', (text_w, text_h), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        text_content = line.text.replace("\\N", "\n")
        
        # စာသားနေရာချခြင်း
        try:
            draw.text((text_w/2, text_h/2), text_content, font=font, fill="white", stroke_width=3, stroke_fill="black", anchor="mm", align="center")
        except:
            draw.text((10, 10), text_content, font=font, fill="white", stroke_width=2, stroke_fill="black")

        clip = ImageClip(np.array(img)).set_start(line.start / 1000).set_duration((line.end - line.start) / 1000)
        # အောက်ခြေနား ကပ်မည်
        clip = clip.set_position(('center', 0.80), relative=True)
        subtitle_clips.append(clip)
        
    return subtitle_clips

# --- Processing ---
if video_file and srt_file:
    if st.button("Start Burning (Turbo Speed)"):
        with st.spinner("Video ကို အမြန်ဆုံးနှုန်းဖြင့် ထုတ်လုပ်နေပါသည်..."):
            
            v_path = "temp_video.mp4"
            s_path = "temp.srt"
            f_path = "myanmar_font.ttf"
            out_path = "final_output.mp4"
            
            with open(v_path, "wb") as f: f.write(video_file.getbuffer())
            with open(s_path, "wb") as f: f.write(srt_file.getbuffer())
            
            if not os.path.exists(f_path):
                st.error("GitHub တွင် 'myanmar_font.ttf' မရှိပါ။ Font ဖိုင် အရင်တင်ပါ။")
                st.stop()
                
            try:
                video = VideoFileClip(v_path)
                
                # Subtitles
                sub_clips = generate_subtitle_clips(s_path, video.w, video.h, f_path)
                
                # Combine
                final_video = CompositeVideoClip([video] + sub_clips)
                
                # --- TURBO SETTINGS ---
                # threads=4 : CPU အကုန်သုံးမည်
                # fps=24 : Frame အရေအတွက် လျှော့ချပြီး မြန်စေမည်
                # preset='ultrafast' : အမြန်ဆုံး Encode နည်းပညာ
                final_video.write_videofile(
                    out_path, 
                    fps=24, 
                    codec='libx264', 
                    preset='ultrafast', 
                    audio_codec='aac', 
                    threads=4
                )
                
                st.success("အောင်မြင်ပါသည်! (ပုံမှန်ထက် ၂ ဆ ပိုမြန်ပါသည်)")
                
                with open(out_path, "rb") as f:
                    st.download_button("Download Video", f.read(), "turbo_subbed_video.mp4", "video/mp4")
                    
            except Exception as e:
                st.error(f"Error: {e}")
            
            # Cleanup
            if os.path.exists(v_path): os.remove(v_path)
            if os.path.exists(s_path): os.remove(s_path)
            if os.path.exists(out_path): os.remove(out_path)
                
