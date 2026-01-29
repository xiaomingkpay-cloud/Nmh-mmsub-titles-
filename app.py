import streamlit as st
import cv2
import numpy as np
import os
import subprocess
import re
import textwrap
from PIL import Image, ImageDraw, ImageFont
from datetime import timedelta

st.set_page_config(page_title="NMH Pro Creator Tools", layout="wide")
st.title("✨ NMH Pro Creator Tools")

# Tab များသတ်မှတ်ခြင်း
tab1, tab2 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (FREE/VIP)"])

# --- Tab 1: SRT Helper ---
with tab1:
    st.header("🌐 Gemini မှတစ်ဆင့် SRT ထုတ်ယူခြင်း")
    st.info("ဒီဗီဒီယိုအတွက် မြန်မာ SRT ထုတ်ပေးပါ")
    st.link_button("🤖 Gemini သို့သွားရန်", "https://gemini.google.com/")
    srt_input = st.text_area("Gemini မှရလာသော SRT စာသားများကို ဒီမှာ Paste လုပ်ပါ", height=150)
    if srt_input:
        st.download_button("📥 SRT ဖိုင်အဖြစ် ဒေါင်းလုဒ်ဆွဲရန်", srt_input, file_name="subtitle.srt")

# --- SRT Parsing Logic ---
def parse_srt(srt_string):
    subs = []
    blocks = re.split(r'\n\s*\n', srt_string.strip())
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            time_line = lines[1]
            content = " ".join(lines[2:])
            times = time_line.split(' --> ')
            if len(times) == 2:
                try:
                    start_time = parse_time(times[0].strip())
                    end_time = parse_time(times[1].strip())
                    subs.append({'start': start_time, 'end': end_time, 'text': content})
                except: continue
    return subs

def parse_time(time_str):
    time_str = time_str.replace(',', '.')
    parts = time_str.split(':')
    return timedelta(hours=int(parts[0]), minutes=int(parts[1]), seconds=float(parts[2]))

# --- Video Processing Function ---
def process_srt_video(v_path, srt_text):
    subtitles = parse_srt(srt_text)
    cap = cv2.VideoCapture(v_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    is_landscape = w > h # 16:9
    
    temp_v = "temp_render.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_v, fourcc, fps, (w, h))
    
    # Font ချိန်ညှိခြင်း
    font_size = int(h / 18) if is_landscape else int(h / 25)
    try:
        font = ImageFont.truetype("myanmar_font.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    prog_bar = st.progress(0)
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
            # စာလုံးအရေအတွက်အလိုက် စာကြောင်းဖြတ်ခြင်း (Landscape: 60, Portrait: 40)
            char_limit = 60 if is_landscape else 40
            wrapped_text = "\n".join(textwrap.wrap(active_text, width=char_limit))
            
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img)
            
            # စာသားနေရာချခြင်း (Landscape: 20% from bottom, Portrait: 40% from bottom)
            margin_pct = 0.20 if is_landscape else 0.40
            
            bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            text_x = (w - text_w) // 2
            text_y = h - int(h * margin_pct) - text_h
            
            # အမည်းရောင်နောက်ခံဘောင် (Opacity ထည့်ထားသည်)
            padding = 15
            overlay = Image.new('RGBA', img.size, (0,0,0,0))
            draw_ov = ImageDraw.Draw(overlay)
            draw_ov.rectangle([text_x - padding, text_y - padding, text_x + text_w + padding, text_y + text_h + padding], fill=(0, 0, 0, 160))
            img = Image.alpha_composite(img.convert('RGBA'), overlay)
            
            # စာသားပြန်ရေးခြင်း
            draw_final = ImageDraw.Draw(img)
            draw_final.multiline_text((text_x, text_y), wrapped_text, font=font, fill=(255, 255, 255), align="center")
            frame = cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2BGR)
            
        out.write(frame)
        if i % 20 == 0: prog_bar.progress((i + 1) / total_frames)

    cap.release()
    out.release()
    
    final_v = "NMH_Final_Video.mp4"
    subprocess.call(['ffmpeg', '-y', '-i', temp_v, '-i', v_path, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-shortest', final_v])
    return final_v

with tab2:
    st.header("📝 မြန်မာစာတန်းထိုး Video ထုတ်ယူခြင်း")
    v_up = st.file_uploader("Video တင်ပါ", type=["mp4", "mov"])
    s_up = st.file_uploader("SRT တင်ပါ", type=["srt"])
    if v_up and s_up:
        if st.button("🚀 Render Final Video"):
            with open("in.mp4", "wb") as f: f.write(v_up.read())
            srt_content = s_up.read().decode('utf-8', errors='ignore')
            res = process_srt_video("in.mp4", srt_content)
            st.success("✅ Render အောင်မြင်ပါသည်!")
            st.video(res)
            st.download_button("📥 Video ကိုဒေါင်းလုဒ်ဆွဲရန်", open(res, "rb"), file_name="NMH_Subtitled.mp4")
            
