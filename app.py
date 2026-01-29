import streamlit as st
import cv2
import numpy as np
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

# UI Configuration
st.set_page_config(page_title="NMH Pro Creator Tools", layout="wide")
st.title("✨ NMH Pro Creator Tools")

tab1, tab2 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (FREE/VIP)"])

# --- Tab 1: SRT Helper ---
with tab1:
    st.header("🌐 Gemini မှတစ်ဆင့် SRT ထုတ်ယူခြင်း")
    st.link_button("🤖 Gemini သို့သွားရန်", "https://gemini.google.com/")
    srt_input = st.text_area("Gemini မှရလာသော SRT စာသားများကို ဒီမှာ Paste လုပ်ပါ", height=150)
    if srt_input:
        st.download_button("📥 SRT ဖိုင်အဖြစ် ဒေါင်းလုဒ်ဆွဲရန်", srt_input, file_name="subtitle.srt")

# --- Tab 2: စာတန်းမြှုပ်ခြင်း Logic ---
def process_video_final(video_in):
    cap = cv2.VideoCapture(video_in)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    temp_render = 'temp_render.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_render, fourcc, fps, (width, height))
    
    progress_bar = st.progress(0)
    for i in range(total_frames):
        ret, frame = cap.read()
        if not ret: break
        out.write(frame)
        progress_bar.progress((i + 1) / total_frames)

    cap.release()
    out.release()

    final_output = 'NMH_Final.mp4'
    # ffmpeg သုံး၍ browser format ပြောင်းခြင်း
    subprocess.call(['ffmpeg', '-y', '-i', temp_render, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', final_output])
    return final_output

with tab2:
    st.header("📝 မြန်မာစာတန်းထိုး Video ထုတ်ယူခြင်း")
    v_file = st.file_uploader("ဗီဒီယိုဖိုင် တင်ပါ", type=["mp4", "mov"], key="v_up")
    s_file = st.file_uploader("SRT ဖိုင် တင်ပါ", type=["srt"], key="s_up")

    if v_file and s_file:
        st.success("✅ ဖိုင်များ အဆင်သင့်ဖြစ်ပါပြီ။")
        if st.button("🚀 Start Rendering"):
            with open("input_video.mp4", "wb") as f:
                f.write(v_file.read())
            
            result_path = process_video_final("input_video.mp4")
            st.success("✅ အောင်မြင်စွာ Render ပြီးပါပြီ!")
            
            st.video(result_path)
            with open(result_path, "rb") as file:
                st.download_button("📥 ဗီဒီယိုကို ဒေါင်းလုဒ်ဆွဲရန်", file, file_name="NMH_Subtitled.mp4", mime="video/mp4")
                
