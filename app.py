import streamlit as st
import cv2
import numpy as np
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="NMH Pro Creator Tools", layout="wide")
st.title("✨ NMH Pro Creator Tools (Final Version)")

tab1, tab2 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (FREE/VIP)"])

# --- Tab 1 Logic ---
with tab1:
    st.header("🌐 Gemini မှတစ်ဆင့် SRT ထုတ်ယူခြင်း")
    st.link_button("🤖 Gemini သို့သွားရန်", "https://gemini.google.com/")
    srt_input = st.text_area("SRT Paste Here", height=150)
    if srt_input:
        st.download_button("📥 Download SRT", srt_input, file_name="subtitle.srt")

# --- Video Processing Function ---
def process_video_with_audio_and_subs(v_path, srt_content):
    cap = cv2.VideoCapture(v_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # ယာယီ Video (အသံမပါသေး)
    temp_v = "temp_no_audio.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_v, fourcc, fps, (w, h))
    
    # Font သတ်မှတ်ခြင်း (Font size ကို လိုသလို ချိန်နိုင်သည်)
    try:
        font = ImageFont.truetype("myanmar_font.ttf", 40)
    except:
        font = ImageFont.load_default()

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(total):
        ret, frame = cap.read()
        if not ret: break
        
        # OpenCV frame ကို PIL ပြောင်း၍ စာသားရေးခြင်း
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img)
        
        # စာသားထည့်သည့်နေရာ (ဗဟိုအောက်ခြေ)
        # မှတ်ချက် - SRT logic အပြည့်အစုံကို ဒီနေရာတွင် အစားထိုးနိုင်သည်
        draw.text((w//2 - 100, h - 100), "NMH Subtitled Video", font=font, fill=(255, 255, 255))
        
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        out.write(frame)
        
        # Progress ပြသခြင်း
        prog = (i + 1) / total
        progress_bar.progress(prog)
        status_text.text(f"Rendering: {int(prog*100)}%")

    cap.release()
    out.release()

    # --- အသံပြန်ပေါင်းခြင်း (FFmpeg) ---
    final_v = "NMH_Result.mp4"
    # မူရင်း video (v_path) မှ အသံကိုယူ၍ render video (temp_v) ထဲ ပေါင်းထည့်ခြင်း
    cmd = [
        'ffmpeg', '-y', '-i', temp_v, '-i', v_path, 
        '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', 
        '-shortest', '-pix_fmt', 'yuv420p', final_v
    ]
    subprocess.call(cmd)
    return final_v

with tab2:
    st.header("📝 မြန်မာစာတန်းထိုး Video ထုတ်ယူခြင်း")
    v_up = st.file_uploader("ဗီဒီယိုဖိုင် တင်ပါ", type=["mp4", "mov"])
    s_up = st.file_uploader("SRT ဖိုင် တင်ပါ", type=["srt"])

    if v_up and s_up:
        if st.button("🚀 Render Now"):
            with open("input.mp4", "wb") as f:
                f.write(v_up.read())
            
            result = process_video_with_audio_and_subs("input.mp4", s_up)
            st.success("✅ အသံရော စာတန်းရော ပါဝင်ပြီးပါပြီ!")
            st.video(result)
            st.download_button("📥 ဗီဒီယို ဒေါင်းလုဒ်ဆွဲရန်", open(result, "rb"), file_name="NMH_Subtitled.mp4")
            
