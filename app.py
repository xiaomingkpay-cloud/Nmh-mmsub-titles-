import streamlit as st
import os
import pysubs2
import numpy as np
import asyncio
import edge_tts
from datetime import datetime
from streamlit.web.server.websocket_headers import _get_websocket_headers
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip
from PIL import Image, ImageDraw, ImageFont

# Website ခေါင်းစဉ်
st.set_page_config(page_title="NMH Pro Creator Mood", layout="wide")

# ==========================================
# 🛡️ SECURITY & TRACKER
# ==========================================
@st.cache_resource
def get_usage_data():
    return {"date": datetime.now().strftime("%Y-%m-%d"), "users": {}, "bindings": {}}

usage_data = get_usage_data()
current_date = datetime.now().strftime("%Y-%m-%d")
if usage_data["date"] != current_date:
    usage_data["date"] = current_date
    usage_data["users"] = {} 

def get_remote_ip():
    try:
        headers = _get_websocket_headers()
        ip = headers.get("X-Forwarded-For")
        if ip: return ip.split(",")[0]
    except: pass
    return "unknown_user"

# ==========================================
# 🏠 HEADER
# ==========================================
st.title("✨ NMH Pro Creator Mood")
st.markdown("""
**📞 Contact Creator:** Facebook: [NMH Facebook](https://www.facebook.com/share/16pXwBsqte) | Telegram: [@xiaoming2025nmx](https://t.me/xiaoming2025nmx)
""")
st.success("📢 Facebook / TikTok / VPN / Follower နှင့် တခြား Premium Service များလဲ ရသည်!")

# TAB 3 ခု
tab1, tab2, tab3 = st.tabs(["Tab 1: 🌐 Get SRT (Gemini)", "Tab 2: 📝 စာတန်းမြှုပ် (Free)", "Tab 3: 🗣️ အသံထည့် (Pro - Fixed)"])

# ==========================================
# TAB 1: GEMINI LINK & TEXT TO SRT CONVERTER
# ==========================================
with tab1:
    st.header("အဆင့် ၁ - Gemini မှ SRT စာသားတောင်းယူပါ")
    st.info("အောက်ပါခလုတ်ကို နှိပ်ပြီး Gemini တွင် Video တင်ပါ။ 'Generate Myanmar SRT file' ဟု ရေးပြီး တောင်းပါ။")
    
    st.link_button("🚀 Go to Google Gemini App/Web", "https://gemini.google.com/")
    
    st.write

