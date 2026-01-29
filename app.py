import streamlit as st
import cv2
import numpy as np
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="NMH Pro Creator Tools", layout="wide")
st.title("✨ NMH Pro Creator Tools (Final Fix)")

tab1, tab2 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (FREE/VIP)"])

# --- Tab 2 logic (ဗီဒီယိုကြည့်ရအောင် ပြင်ဆင်ထားသည်) ---
def process_video_final(video_in, srt_in):
    cap = cv2.VideoCapture(video_in)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # ယာယီဖိုင်အဖြစ် အရင်သိမ်းဆည်းမည်
    temp_output = 'temp_output.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_output, fourcc, fps, (width, height))
    
    progress_bar = st.progress(0)
    for i in range(total_frames):
        ret, frame = cap.read()
        if not ret: break
        # စာတန်းထိုးရန် logic များ ဤနေရာတွင် ရှိမည်
        out.write(frame)
        progress_bar.progress((i + 1) / total_frames)

    cap.release()
    out.release()

    # Browser မှာ ကြည့်လို့ရအောင် H.264 သို့ ပြောင်းလဲခြင်း (အရေးကြီးဆုံးအဆင့်)
    final_output = 'NMH_Final_Video.mp4'
    subprocess.call(['ffmpeg', '-y', '-i', temp_output, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', final_output])
    return final_output

with tab2:
    v_file = st.file_uploader("ဗီဒီယိုဖိုင် တင်ပါ", type=["mp4", "mov"])
    if v_file:
        with open("input_v.mp4", "wb") as f: f.write(v_file.read())
        if st.button("🚀 Render & Download Video"):
            result_file = process_video_final("input_v.mp4", None)
            st.success("✅ Render ပြီးပါပြီ!")
            
            # ဗီဒီယို ပြသခြင်း
            st.video(result_file)
            
            # ဒေါင်းလုဒ် ခလုတ်
            with open(result_file, "rb") as file:
                st.download_button(
                    label="📥 ဗီဒီယိုကို ဒေါင်းလုဒ်ဆွဲရန်",
                    data=file,
                    file_name="NMH_Subtitled.mp4",
                    mime="video/mp4"
                )
                
