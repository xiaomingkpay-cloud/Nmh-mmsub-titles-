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
st.set_page_config(page_title="NMH မြန်မာစာတန်းထိုး Pro", layout="wide")

# --- LOGIN GATE ---
all_vip_keys = st.secrets.get("vip_keys", {}).values()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'last_render' not in st.session_state:
    st.session_state.last_render = 0

if not st.session_state.authenticated:
    # ခေါင်းစဉ်ကို ပြောင်းလဲထားသည်
    st.title("🔐 NMH မြန်မာစာတန်းထိုး Pro")
    user_key = st.text_input("ဝင်ရောက်ရန် VIP Key ရိုက်ထည့်ပါ", type="password")
    
    if st.button("Login"):
        if user_key in all_vip_keys:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Key မှားယွင်းနေပါသည်။")
    
    # --- CREATOR CONTACT SECTION (Login အောက်တွင် ပြသရန်) ---
    st.divider()
    st.subheader("📞 Creator သို့ ဆက်သွယ်ရန်")
    
    col1, col2 = st.columns(2)
    with col1:
        # Facebook ခလုတ်နှင့် Link
        st.link_button("🔵 Facebook", "https://www.facebook.com/share/1BUUZ4pQ3N/")
    with col2:
        # Telegram ခလုတ်နှင့် ID
        st.link_button("✈️ Telegram", "https://t.me/xiaoming2025nmx")
    
    st.write("🆔 Telegram ID: `@xiaoming2025nmx`")
    
    # ဝန်ဆောင်မှုများ ဖော်ပြချက်
    st.info("""
    🌟 **Service များ:**
    VPN / Follower / Facebook / TikTok Service များလည်း ရရှိနိုင်ပါသည်။
    """)
    st.stop()

# --- FUNCTIONS ---
def get_video_duration(file_path):
    cap = cv2.VideoCapture(file_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0
    cap.release()
    return duration

def compress_video_pro(input_path, output_path):
    # CRF 22 ဖြင့် Resolution မကျဘဲ အကောင်းဆုံးချုံ့ခြင်း
    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-c:v', 'libx264', '-crf', '22',
        '-preset', 'slow',
        '-c:a', 'aac', '-b:a', '128k',
        output_path
    ]
    subprocess.call(cmd)
    return output_path

# ... (parse_time, parse_srt နှင့် process_srt_video logic များသည် ယခင်အတိုင်းဖြစ်သည်)

# --- MAIN UI (After Login) ---
st.title("✨ NMH မြန်မာစာတန်းထိုး Pro")

tab1, tab2, tab3 = st.tabs(["📉 Step 1: Video Compress", "🌐 Step 2: SRT Helper", "📝 Step 3: Subtitle Render"])

with tab1:
    st.header("📉 Video File Size လျှော့ချခြင်း")
    # ကန့်သတ်ချက် စာသားများ
    st.write("✅ **၂ မိနစ်** အထိသာ လက်ခံပါမည်။")
    st.write("✅ **200MB** အထိသာ အများဆုံး ထည့်သွင်းနိုင်ပါသည်။")
    
    raw_v = st.file_uploader("ဗီဒီယိုတင်ပါ", type=["mp4", "mov", "mpeg4"], key="comp")
    
    if raw_v:
        # 200MB စစ်ဆေးခြင်း
        file_size_mb = raw_v.size / (1024 * 1024)
        if file_size_mb > 200:
            st.error(f"❌ ဖိုင်ဆိုဒ် {file_size_mb:.1f}MB ဖြစ်နေပါသည်။ 200MB ထက်မကျော်ရပါ။")
        else:
            if st.button("🚀 Smart Compress"):
                with st.spinner("အကြည်ဓာတ်မပျက်စေဘဲ ဆိုဒ်ကျုံ့နေပါသည်..."):
                    with open("temp_raw.mp4", "wb") as f: f.write(raw_v.read())
                    
                    # ၂ မိနစ် စစ်ဆေးခြင်း
                    duration = get_video_duration("temp_raw.mp4")
                    if duration > 120:
                        st.error(f"❌ ဗီဒီယိုကြာချိန် ၂ မိနစ် ထက်ကျော်လွန်နေပါသည်။")
                    else:
                        res_v = compress_video_pro("temp_raw.mp4", "compressed.mp4")
                        st.success(f"✅ ကျုံ့ပြီးပါပြီ! ({os.path.getsize(res_v)//1024//1024} MB)")
                        st.video(res_v)
                        st.download_button("📥 Download Compressed Video", open(res_v, "rb"), file_name="NMH_Compressed.mp4")

# ... (Step 2 နှင့် Step 3 logic များသည် ယခင်အတိုင်းဖြစ်သည်)
