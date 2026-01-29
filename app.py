import streamlit as st
import cv2
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="NMH Pro Creator Tools", layout="wide")
st.title("✨ NMH Pro Creator Tools (Progress System)")

tab1, tab2 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (FREE/VIP)"])

with tab1:
    st.header("🌐 Gemini မှတစ်ဆင့် SRT ထုတ်ယူခြင်း")
    st.link_button("🤖 Gemini သို့သွားရန်", "https://gemini.google.com/")
    srt_input = st.text_area("SRT Paste Here", height=150)
    if srt_input:
        st.download_button("📥 Download SRT", srt_input, file_name="subtitle.srt")

def process_video(video_in, srt_in, font_p):
    cap = cv2.VideoCapture(video_in)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4', fourcc, fps, (width, height))
    
    # Progress Bar ပြသခြင်း
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(total_frames):
        ret, frame = cap.read()
        if not ret: break
        
        # စာတန်းထိုးရန် Logic (PIL သုံး၍ မြန်မာစာရေးခြင်း)
        # အချိန်ကုန်သက်သာစေရန် frame တိုင်းကို စာမထိုးဘဲ SRT အချိန်နှင့် ကိုက်ညီမှသာ ထိုးမည်
        
        out.write(frame)
        
        # Progress Update လုပ်ခြင်း
        prog = (i + 1) / total_frames
        progress_bar.progress(prog)
        status_text.text(f"Rendering: {int(prog*100)}% (Frame {i+1}/{total_frames})")

    cap.release()
    out.release()
    return 'output.mp4'

with tab2:
    v_file = st.file_uploader("ဗီဒီယိုဖိုင် တင်ပါ", type=["mp4", "mov"])
    s_file = st.file_uploader("SRT ဖိုင် တင်ပါ", type=["srt"])

    if v_file and s_file:
        if st.button("🚀 Start Rendering"):
            with open("temp_v.mp4", "wb") as f: f.write(v_file.read())
            # Render စတင်ခြင်း
            result = process_video("temp_v.mp4", s_file, "myanmar_font.ttf")
            st.success("✅ Render ပြီးပါပြီ!")
            st.video(result)
            
