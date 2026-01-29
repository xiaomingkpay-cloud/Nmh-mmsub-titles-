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

# --- SRT Parsing Logic ---
def parse_srt(srt_string):
    subs = []
    pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n((?:.*\n?)*?)(?=\n\n|\Z)'
    matches = re.findall(pattern, srt_string)
    for m in matches:
        start_time = parse_time(m[1])
        end_time = parse_time(m[2])
        subs.append({'start': start_time, 'end': end_time, 'text': m[3].strip()})
    return subs

def parse_time(time_str):
    h, m, s = time_str.replace(',', ':').split(':')
    return timedelta(hours=int(h), minutes=int(m), seconds=int(s)/1000 + int(s.split('.')[0] if '.' in s else s))

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
    
    # Video အမြင့်ပေါ်မူတည်ပြီး Font size ချိန်ခြင်း
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
            # စာသားနေရာ ချိန်ညှိခြင်း (ဗဟိုအောက်ခြေ)
            bbox = draw.textbbox((0, 0), active_text, font=font)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            # Stroke (စာသားဘောင်အနက်) ထည့်ခြင်း
            draw.text(((w - text_w)//2, h - text_h - 60), active_text, font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0,0,0))
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
        out.write(frame)
        prog_bar.progress((i + 1) / total_frames)
        status_txt.text(f"Rendering: {int(((i+1)/total_frames)*100)}%")

    cap.release()
    out.release()

    # Audio ပြန်ပေါင်းခြင်း (Final Output)
    final_v = "NMH_Subtitled_Final.mp4"
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
            # SRT ဖိုင်ကို Text အဖြစ်ဖတ်ခြင်း
            srt_content = s_up.read().decode('utf-8')
            
            result = process_srt_video("in.mp4", srt_content)
            
            st.success("✅ Render အောင်မြင်ပါသည်!")
            st.video(result)
            with open(result, "rb") as f:
                st.download_button("📥 Video ကိုဒေါင်းလုဒ်ဆွဲရန်", f, file_name="NMH_Subtitled.mp4", mime="video/mp4")
                
