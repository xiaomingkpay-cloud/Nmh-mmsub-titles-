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

# --- LOGIN GATE (Database မလိုသောနည်းလမ်း) ---
# Secrets ထဲမှ VIP Keys များကို ဖတ်ယူခြင်း
all_vip_keys = st.secrets.get("vip_keys", {}).values()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'last_render' not in st.session_state:
    st.session_state.last_render = 0

# Key မရိုက်မချင်း Website ကို မပြပါ
if not st.session_state.authenticated:
    st.title("🔐 NMH Pro Tools - Login")
    user_key = st.text_input("ဝင်ရောက်ရန် VIP Key ရိုက်ထည့်ပါ", type="password")
    if st.button("Login"):
        if user_key in all_vip_keys:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Key မှားယွင်းနေပါသည်။")
    st.stop()

# --- MAIN APP UI ---
st.title("✨ NMH Pro Creator Tools")

# --- PROCESSING FUNCTIONS ---
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
                subs.append({'start': parse_time(times[0].strip()), 'end': parse_time(times[1].strip()), 'text': " ".join(lines[2:])})
            except: continue
    return subs

def process_srt_video(v_path, srt_text, pos_pct):
    subtitles = parse_srt(srt_text)
    cap = cv2.VideoCapture(v_path)
    
    # Original Resolution ယူခြင်း
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # ဖိုင်ဆိုဒ်ကြီး၍ Render မနိုင်ခြင်းကို ကာကွယ်ရန် (1280px ထက်ကြီးလျှင် လျှော့ချမည်)
    if w > 1280:
        scale = 1280 / w
        w = 1280
        h = int(h * scale)
    
    out = cv2.VideoWriter("temp_render.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
    
    # စာလုံးဆိုဒ်ကို ဗီဒီယိုအမြင့်နှင့် ချိန်ညှိခြင်း
    font_size = int(h / 18 if w > h else h / 25)
    font = ImageFont.truetype("myanmar_font.ttf", font_size)
    
    total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    prog = st.progress(0)
    
    for i in range(total_f):
        ret, frame = cap.read()
        if not ret: break
        
        # Frame ဆိုဒ်ကို ပြန်ညှိခြင်း
        frame = cv2.resize(frame, (w, h))
        
        cur_sec = i / fps
        active_txt = next((s['text'] for s in subtitles if s['start'].total_seconds() <= cur_sec <= s['end'].total_seconds()), "")
        
        if active_txt:
            wrap_limit = 60 if w > h else 30
            wrapped = "\n".join(textwrap.wrap(active_txt, width=wrap_limit))
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img)
            
            bbox = draw.multiline_textbbox((0, 0), wrapped, font=font)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            tx, ty = (w - text_w) // 2, h - int(h * (pos_pct / 100)) - text_h
            
            # စာတန်းနောက်ခံ Box ထည့်ခြင်း
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            ImageDraw.Draw(overlay).rectangle([tx-15, ty-15, tx+text_w+15, ty+text_h+15], fill=(0, 0, 0, 160))
            img = Image.alpha_composite(img.convert('RGBA'), overlay)
            
            # စာတန်းရေးခြင်း
            ImageDraw.Draw(img).multiline_text((tx, ty), wrapped, font=font, fill=(255, 255, 255), align="center")
            frame = cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2BGR)
            
        out.write(frame)
        if i % 25 == 0: 
            prog.progress((i + 1) / total_f)
            
    cap.release()
    out.release()
    
    # FFmpeg ဖြင့် အသံပြန်ပေါင်းခြင်း
    subprocess.call(['ffmpeg', '-y', '-i', 'temp_render.mp4', '-i', v_path, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-shortest', 'NMH_Final.mp4'])
    return 'NMH_Final.mp4'

# --- TABS ---
tab1, tab2 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ်"])

with tab1:
    st.header("🌐 Gemini မှတစ်ဆင့် SRT ထုတ်ယူခြင်း")
    st.info("အောက်ပါစာသားကို Copy ယူပြီး Gemini တွင် SRT ထုတ်ခိုင်းပါ")
    st.code("ဒီဗီဒီယိုအတွက် မြန်မာ SRT ထုတ်ပေးပါ", language=None)
    st.link_button("🤖 Gemini သို့သွားရန်", "https://gemini.google.com/")
    srt_input = st.text_area("Gemini မှရလာသော SRT ကို ဒီမှာ Paste လုပ်ပါ", height=150)
    if srt_input:
        st.download_button("📥 SRT သိမ်းရန်", srt_input, file_name="subtitle.srt")

with tab2:
    st.header("📝 မြန်မာစာတန်းထိုး Video ထုတ်ယူခြင်း")
    
    # အလွန်အကျွံဝင်သုံးခြင်းကို တားဆီးရန် ၁၅ မိနစ် စောင့်ခိုင်းခြင်း
    elapsed = time.time() - st.session_state.last_render
    wait_time = 900 # 15 မိနစ်
    
    if elapsed < wait_time and st.session_state.last_render != 0:
        st.warning(f"⏳ ဗီဒီယိုတစ်ခု ထုတ်ပြီးတိုင်း ၁၅ မိနစ် စောင့်ရပါမည်။ ကျန်ရှိချိန်: {int((wait_time - elapsed) // 60)} မိနစ်")
    else:
        v_up = st.file_uploader("Video တင်ပါ (Limit: 500MB)", type=["mp4", "mov"])
        s_up = st.file_uploader("SRT တင်ပါ", type=["srt"])
        pos = st.selectbox("စာတန်းနေရာ (%)", [10, 20, 30], index=1)
        
        if v_up and s_up:
            if st.button("🚀 Render Final Video"):
                with st.spinner("ဗီဒီယိုထုတ်နေပါသည်... ခဏစောင့်ပေးပါ..."):
                    with open("in.mp4", "wb") as f: 
                        f.write(v_up.read())
                    
                    try:
                        res = process_srt_video("in.mp4", s_up.read().decode('utf-8', errors='ignore'), pos)
                        st.session_state.last_render = time.time()
                        st.success("✅ အောင်မြင်စွာ ထုတ်ယူပြီးပါပြီ!")
                        st.video(res)
                        st.download_button("📥 Video ဒေါင်းရန်", open(res, "rb"), file_name="NMH_Subtitled.mp4")
                    except Exception as e:
                        st.error(f"❌ Error ဖြစ်သွားပါသည်: {e}")
                        
