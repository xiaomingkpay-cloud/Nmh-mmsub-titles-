import streamlit as st
import cv2
import numpy as np
import os
import subprocess
import re
from PIL import Image, ImageDraw, ImageFont
from datetime import timedelta

st.set_page_config(page_title="NMH Pro Creator Tools", layout="wide")
st.title("✨ NMH Pro Creator Tools (Final Fixed)")

# --- SRT Parsing Logic (ပိုမိုကောင်းမွန်အောင် ပြင်ဆင်ထားသည်) ---
def parse_srt(srt_string):
    subs = []
    # SRT format ကို ပိုမိုတိကျစွာ ခွဲခြားခြင်း
    blocks = re.split(r'\n\s*\n', srt_string.strip())
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            time_line = lines[1]
            content = " ".join(lines[2:])
            times = time_line.split(' --> ')
            if len(times) == 2:
                start_time = parse_time(times[0].strip())
                end_time = parse_time(times[1].strip())
                subs.append({'start': start_time, 'end': end_time, 'text': content})
    return subs

def parse_time(time_str):
    # အချိန်ပုံစံ အမျိုးမျိုးကို လက်ခံနိုင်ရန် ပြင်ဆင်ခြင်း
    time_str = time_str.replace(',', '.')
    parts = time_str.split(':')
    if len(parts) == 3:
        h, m, s = parts
        return timedelta(hours=int(h), minutes=int(m), seconds=float(s))
    return timedelta(0)

# --- Video Processing Function ---
def process_srt_video(v_path, srt_text):
    subtitles = parse_srt(srt_text)
    cap = cv2.VideoCapture(v_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    temp_v = "temp_render.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_v, fourcc, fps, (w, h))
    
    font_size = int(h / 15)
    try:
        font = ImageFont.truetype("myanmar_font.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    prog_bar = st.progress(0)
    status_txt = st.empty()

    for i in range(total_frames):
        ret, frame = cap.read()
        if not ret: break
        
        current_sec = i / fps
        active_text = ""
        for s in subtitles:
            if s['start'].total_seconds() <= current_sec <= s['end'].total_seconds():
                active_text = s['text']
                break
        
        if active_text:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img)
            bbox = draw.textbbox((0, 0), active_text, font=font)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            # စာသားကို အလယ်ဗဟို အောက်ခြေတွင် ထားခြင်း
            draw.text(((w - text_w)//2, h - text_h - 60), active_text, font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0,0,0))
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
        out.write(frame)
        if i % 10 == 0: # Update progress every 10 frames to save performance
            prog = (i + 1) / total_frames
            prog_bar.progress(prog)
            status_txt.text(f"Rendering: {int(prog*100)}%")

    cap.release()
    out.release()

    final_v = "NMH_Subtitled_Final.mp4"
    # Audio ပြန်ပေါင်းခြင်း (FFmpeg)
    subprocess.call(['ffmpeg', '-y', '-i', temp_v, '-i', v_path, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-shortest', final_v])
    return final_v

# --- UI Setup ---
tab1, tab2 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (FREE/VIP)"])

with tab2:
    st.header("📝 မြန်မာစာတန်းထိုး Video ထုတ်ယူခြင်း")
    v_up = st.file_uploader("Video တင်ပါ", type=["mp4", "mov"])
    s_up = st.file_uploader("SRT တင်ပါ", type=["srt"])
    
    if v_up and s_up:
        if st.button("🚀 Render Final Video"):
            with open("in.mp4", "wb") as f: 
                f.write(v_up.read())
            srt_content = s_up.read().decode('utf-8', errors='ignore')
            
            result = process_srt_video("in.mp4", srt_content)
            
            st.success("✅ Render အောင်မြင်ပါသည်!")
            st.video(result)
            with open(result, "rb") as f:
                st.download_button("📥 Video ကိုဒေါင်းလုဒ်ဆွဲရန်", f, file_name="NMH_Subtitled.mp4", mime="video/mp4")
                
