import streamlit as st
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
import os

# --- Page Layout & Styles ---
st.set_page_config(page_title="NMH Pro Creator Tools", layout="wide")

# NMH Design (Custom CSS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #1e2129;
        border-radius: 8px;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Header Section ---
st.title("✨ NMH Pro Creator Tools")
st.markdown("### 👨‍💻 Developed by Naing Min Htet")

col1, col2 = st.columns([3, 1])
with col2:
    st.link_button("🔵 Facebook Page", "https://www.facebook.com/share/1aavUJzZ9f/")
    st.link_button("✈️ Telegram Contact", "https://t.me/xiaoming2025nmx")

st.info("🚫Video Editing လုံးဝမလိုသော Professional Tools")
st.warning("🌟 VIP အကောင့်ဝယ်ယူလိုပါက အထက်ပါ Link များမှတစ်ဆင့် ဆက်သွယ်နိုင်ပါသည်။")

st.divider()

# --- Tabs Setup ---
tabs = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (FREE/VIP)", "🗣️ အသံထုတ်ရန် (VIP)", "🎬 Video ပေါင်းရန် (VIP)"])

# --- Tab 2: စာတန်းမြှုပ်ခြင်း (The Real Logic) ---
with tabs[1]:
    st.header("Tab 2: စာတန်းမြှုပ်ခြင်း")
    st.info("✅ Free လက်ကျန်: 3/3 ပုဒ်")
    
    video_input = st.file_uploader("Video တင်ပါ", type=["mp4", "mov"], key="v2")
    srt_input = st.file_uploader("SRT တင်ပါ", type=["srt"], key="s2")
    
    if video_input and srt_input:
        if st.button("Render Now (Start Subtitling)"):
            try:
                with st.spinner('ဗီဒီယို ဖန်တီးနေသည်... ခေတ္တစောင့်ပါ'):
                    # Save temporary files for MoviePy
                    with open("temp_video.mp4", "wb") as f: f.write(video_input.read())
                    with open("temp_sub.srt", "wb") as f: f.write(srt_input.read())
                    
                    video = VideoFileClip("temp_video.mp4")
                    
                    # Subtitle Generator Settings
                    # မြန်မာစာအတွက် font path ကို သေချာစစ်ဆေးပါ
                    def generator(txt):
                        return TextClip(txt, font='myanmar_font.ttf', fontsize=40, color='white', 
                                       method='caption', size=(video.w*0.8, None))
                    
                    subtitles = SubtitlesClip("temp_sub.srt", generator)
                    final_result = CompositeVideoClip([video, subtitles.set_pos(('center', 'bottom'))])
                    
                    output_file = "NMH_Output.mp4"
                    final_result.write_videofile(output_file, fps=video.fps, codec="libx264", 
                                               audio_codec="aac", temp_audiofile='temp-audio.m4a', 
                                               remove_temp=True)
                    
                    st.success("စာတန်းမြှုပ်ခြင်း အောင်မြင်ပါသည်။")
                    st.video(output_file)
                    
                    with open(output_file, "rb") as file:
                        st.download_button(label="Video ဒေါင်းလုဒ်လုပ်ရန်", data=file, file_name="NMH_Subbed_Video.mp4")
                        
            except Exception as e:
                st.error(f"Error တက်သွားပါသည်- {str(e)}")

# --- Other Tabs Content (Placeholders) ---
with tabs[0]:
    st.header("Tab 1: SRT ထုတ်ရန်")
    st.write("ယခု feature သည် VIP များအတွက်သာ ဖြစ်ပါသည်။")

with tabs[2]:
    st.header("Tab 3: အသံထုတ်ရန် (VIP)")
    st.write("မြန်မာစာကို အသံပြောင်းလဲပေးမည့် Tool ဖြစ်ပါသည်။")

with tabs[3]:
    st.header("Tab 4: Video နှင့် အသံဖိုင် ပေါင်းစပ်ခြင်း")
    st.success("✅ VIP အကောင့်: Maung Maung (VIP)")
    st.write("Video နှင့် Audio ပေါင်းစပ်ပေးသည့် Feature ဖြစ်ပါသည်။")
    
