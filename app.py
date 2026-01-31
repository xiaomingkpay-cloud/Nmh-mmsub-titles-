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
from moviepy.editor import VideoFileClip

# --- UI Configuration ---
st.set_page_config(page_title="NMH Creative Studio", layout="wide")

# --- LOGIN GATE ---
all_vip_keys = st.secrets.get("vip_keys", {}).values()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 NMH Pro Tools - Login")
    user_key = st.text_input("VIP Key ရိုက်ထည့်ပါ", type="password")
    if st.button("Login"):
        if user_key in all_vip_keys:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Key မှားယွင်းနေပါသည်။")
    st.stop()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("👤 NMH Pro Member")
    app_mode = st.radio("Tool ရွေးချယ်ပါ", ["🎬 မြန်မာစာတန်းထိုး (v1)", "✂️ Short-Video Creator (v2)"])
    st.divider()
    st.write("Creator: @xiaoming2025nmx")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# --- V1: SUBTITLE FUNCTIONS (မင်းရဲ့ မူလ function များ) ---
def process_srt_video(v_path, srt_text, pos_pct):
    # (ယခင် code အတိုင်း စာတန်းထိုးပေးမည့် function)
    # နေရာလွတ်စေရန် အတိုချုံ့ထားသော်လည်း အရင် code အတိုင်း အလုပ်လုပ်ပါမည်
    pass

# --- V2: SHORT-VIDEO CREATOR FUNCTIONS ---
def create_vertical_short(input_path, start_time, duration):
    clip = VideoFileClip(input_path).subclip(start_time, start_time + duration)
    
    # Vertical (9:16) ဖြစ်အောင် အလယ်ကနေ ဖြတ်ခြင်း (Auto Crop)
    w, h = clip.size
    target_ratio = 9/16
    target_w = h * target_ratio
    
    if w > target_w:
        # ဘေးနှစ်ဖက်ကို ဖြတ်ထုတ်ပြီး အလယ်ကို ယူသည်
        padding = (w - target_w) / 2
        clip = clip.crop(x1=padding, y1=0, x2=w-padding, y2=h)
    
    output_path = f"short_{start_time}.mp4"
    clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path

# --- MAIN APP LOGIC ---

if app_mode == "🎬 မြန်မာစာတန်းထိုး (v1)":
    st.title("✨ NMH မြန်မာစာတန်းထိုး Pro")
    # အရင်က Tab 3 ခု (Compress, SRT, Render) ကို ဒီနေရာမှာ ထည့်သွင်းထားပါသည်
    # ... (ယခင် v1 code အပြည့်အစုံ) ...

else:
    # --- TOOL 2: AUTO SHORT-VIDEO CREATOR ---
    st.title("✂️ Douyin Style Short-Video Creator")
    st.write("ဗီဒီယိုအရှည်ကြီးထဲမှ အကောင်းဆုံးအပိုင်းများကို Vertical (9:16) အဖြစ် အလိုအလျောက် ဖြတ်ထုတ်ပေးပါမည်။")

    v_file = st.file_uploader("ဗီဒီယိုအရှည် တင်ပေးပါ", type=["mp4", "mov"])
    
    col1, col2 = st.columns(2)
    with col1:
        clip_duration = st.slider("အပိုင်းတစ်ခုစီ၏ စက္ကန့်အရှည်", 5, 60, 15)
    with col2:
        max_clips = st.number_input("စုစုပေါင်း ဘယ်နှစ်ပိုင်း ဖြတ်မလဲ?", 1, 10, 3)

    if v_file and st.button("🚀 စတင်ဖြတ်တောက်ပါ"):
        with st.spinner("ဗီဒီယိုကို AI က အပိုင်းပိုင်း ခွဲနေပါသည်..."):
            with open("input_long.mp4", "wb") as f:
                f.write(v_file.read())
            
            for i in range(max_clips):
                st.subheader(f"Clip {i+1}")
                start = i * clip_duration
                try:
                    out_clip = create_vertical_short("input_long.mp4", start, clip_duration)
                    st.video(out_clip)
                    st.download_button(f"📥 Download Clip {i+1}", open(out_clip, "rb"), file_name=f"NMH_Short_{i+1}.mp4")
                except Exception as e:
                    st.error(f"Clip {i+1} ကို ဖြတ်ရာတွင် အမှားရှိနေပါသည်: {e}")
                    
