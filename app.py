import streamlit as st
import cv2
import numpy as np
import os
import subprocess
import re
import textwrap
import time
from PIL import Image, ImageDraw, ImageFont
from datetime import timedelta

# UI Configuration
st.set_page_config(page_title="NMH Pro Creator Tools", layout="wide")
st.title("✨ NMH Pro Creator Tools (Stable Version)")

# --- VIP & LIMIT SYSTEM INITIALIZATION ---
if 'user_type' not in st.session_state:
    st.session_state.user_type = "Free"
if 'daily_count' not in st.session_state:
    st.session_state.daily_count = 0
if 'last_render_time' not in st.session_state:
    st.session_state.last_render_time = 0

# --- VIP KEYS CHECK ---
# Streamlit Secrets ထဲက vip_keys စာရင်းကို ဖတ်ယူခြင်း
all_vip_keys = st.secrets.get("vip_keys", {}).values()

with st.sidebar:
    st.header("🔑 Member Login")
    user_key_input = st.text_input("သီးသန့် VIP Key ကို ရိုက်ထည့်ပါ", type="password")
    
    if user_key_input in all_vip_keys:
        st.session_state.user_type = "VIP"
        st.success("🌟 VIP Member အဖြစ် ဝင်ရောက်ထားသည်။")
    elif user_key_input == "":
        st.session_state.user_type = "Free"
        st.info("🆓 Free User အဖြစ် အသုံးပြုနေသည်။")
    else:
        st.session_state.user_type = "Free"
        st.error("❌ Key မှားယွင်းနေပါသည်။")
    
    st.divider()
    st.write(f"📊 ယနေ့ထုတ်ပြီးသမျှ: {st.session_state.daily_count} ပုဒ်")
    st.write(f"👤 အမျိုးအစား: {st.session_state.user_type}")

# --- LIMIT CHECK FUNCTION ---
def check_limits():
    current_time = time.time()
    wait_time = 1800  # နာရီဝက် (၁၈၀၀ စက္ကန့်)
    max_daily = 3 if st.session_state.user_type == "Free" else 10
    
    if st.session_state.daily_count >= max_daily:
        return False, f"❌ သင်၏ တစ်နေ့တာ ဗီဒီယိုထုတ်ယူခွင့် ({max_daily} ပုဒ်) ပြည့်သွားပါပြီ။"
    
    elapsed = current_time - st.session_state.last_render_time
    if elapsed < wait_time:
        rem_min = int((wait_time - elapsed) // 60)
        return False, f"⏳ နောက်ထပ် ဗီဒီယိုထုတ်ရန် မိနစ် {rem_min} စောင့်ပေးပါ။"
    
    return True, ""

# --- SRT & VIDEO PROCESSING FUNCTIONS ---
def parse_time(time_str):
    time_str = time_str.replace(',', '.')
    parts = time_str.split(':')
    return timedelta(hours=int(parts[0]), minutes=int(parts[1]), seconds=float(parts[2]))

def parse_srt(srt_string):
    subs = []
    blocks = re.split(r'\n\s*\n', srt_string.strip())
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            try:
                times = lines[1].split(' --> ')
                start_t = parse_time(times[0].strip())
                end_t = parse_time(times[1].strip())
                subs.append({'start': start_t, 'end': end_t, 'text': " ".join(lines[2:])})
            except: continue
    return subs

def process_srt_video(v_path, srt_text, pos_pct):
    subtitles = parse_srt(srt_text)
    cap = cv2.VideoCapture(v_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    is_landscape = w > h
    temp_v = "temp_render.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_v, fourcc, fps, (w, h))
    
    font_size = int(h / 18) if is_landscape else int(h / 25)
    font = ImageFont.truetype("myanmar_font.ttf", font_size)
    
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
            char_limit = 60 if is_landscape else 30
            wrapped_text = "\n".join(textwrap.wrap(active_text, width=char_limit))
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img)
            
            margin_pct = pos_pct / 100
            bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            text_x, text_y = (w - text_w) // 2, h - int(h * margin_pct) - text_h
            
            padding = 15
            overlay = Image.new('RGBA', img.size, (0,0,0,0))
            draw_ov = ImageDraw.Draw(overlay)
            draw_ov.rectangle([text_x - padding, text_y - padding, text_x + text_w + padding, text_y + text_h + padding], fill=(0, 0, 0, 160))
            img = Image.alpha_composite(img.convert('RGBA'), overlay)
            
            draw_final = ImageDraw.Draw(img)
            draw_final.multiline_text((text_x, text_y), wrapped_text, font=font, fill=(255, 255, 255), align="center")
            frame = cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2BGR)
            
        out.write(frame)
        if i % 20 == 0: prog_bar.progress((i + 1) / total_frames)

    cap.release()
    out.release()
    
    final_v = "NMH_Final.mp4"
    subprocess.call(['ffmpeg', '-y', '-i', temp_v, '-i', v_path, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-shortest', final_v])
    return final_v

# --- TABS UI ---
tab1, tab2 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (FREE/VIP)"])

with tab1:
    st.header("🌐 Gemini မှတစ်ဆင့် SRT ထုတ်ယူခြင်း")
    prompt_text = "ဒီဗီဒီယိုအတွက် မြန်မာ SRT ထုတ်ပေးပါ"
    col1, col2 = st.columns([3, 1])
    with col1: st.code(prompt_text, language=None)
    with col2: st.write("Copy ယူပါ ☝️")
    st.divider()
    st.link_button("🤖 Gemini သို့သွားရန်", "https://gemini.google.com/")
    srt_input = st.text_area("Gemini မှရလာသော SRT ကို ဒီမှာ Paste လုပ်ပါ", height=150)
    if srt_input:
        st.download_button("📥 SRT သိမ်းရန်", srt_input, file_name="subtitle.srt")

with tab2:
    st.header("📝 မြန်မာစာတန်းထိုး Video ထုတ်ယူခြင်း")
    v_up = st.file_uploader("Video တင်ပါ", type=["mp4"])
    s_up = st.file_uploader("SRT တင်ပါ", type=["srt"])
    pos_choice = st.selectbox("စာတန်းနေရာ (%)", [10, 20, 30], index=1)

    if v_up and s_up:
        can_run, msg = check_limits()
        if not can_run:
            st.error(msg)
        else:
            if st.button("🚀 Render Final Video"):
                with open("in.mp4", "wb") as f: f.write(v_up.read())
                srt_content = s_up.read().decode('utf-8', errors='ignore')
                res = process_srt_video("in.mp4", srt_content, pos_choice)
                
                st.session_state.daily_count += 1
                st.session_state.last_render_time = time.time()
                
                st.success("✅ အောင်မြင်စွာ ထုတ်ယူပြီးပါပြီ!")
                st.video(res)
                st.download_button("📥 Video ဒေါင်းရန်", open(res, "rb"), file_name="NMH_Subtitled.mp4")
                
