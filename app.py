import streamlit as st
import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip

# --- NMH DESIGN ---
st.set_page_config(page_title="NMH Pro Creator Tools", layout="wide")
st.title("✨ NMH Pro Creator Tools")
st.markdown("### 👨‍💻 Developed by Naing Min Htet")

tabs = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (FREE/VIP)", "🗣️ အသံထုတ်ရန် (VIP)", "🎬 Video ပေါင်းရန် (VIP)"])

# --- TAB 2: တကယ်အလုပ်လုပ်မည့် စာတန်းမြှုပ် Logic ---
with tabs[1]:
    st.header("Tab 2: စာတန်းမြှုပ်ခြင်း")
    video_in = st.file_uploader("Video တင်ပါ", type=["mp4", "mov"], key="v2")
    srt_in = st.file_uploader("SRT တင်ပါ", type=["srt"], key="s2")

    if video_in and srt_in:
        if st.button("Render Now"):
            try:
                with st.spinner('ဗီဒီယို ဖန်တီးနေသည်...'):
                    # ဖိုင်သိမ်းခြင်း
                    with open("temp_v.mp4", "wb") as f: f.write(video_in.read())
                    with open("temp_s.srt", "wb") as f: f.write(srt_in.read())
                    
                    video = VideoFileClip("temp_v.mp4")
                    
                    # Font ကို 'myanmar_font.ttf' လို့ နာမည်ပေးထားတာ သေချာပါစေ
                    generator = lambda txt: TextClip(txt, font='myanmar_font.ttf', fontsize=40, color='white', 
                                                   method='caption', size=(video.w*0.8, None))
                    
                    subtitles = SubtitlesClip("temp_s.srt", generator)
                    result = CompositeVideoClip([video, subtitles.set_pos(('center', 'bottom'))])
                    
                    output = "NMH_Subtitled.mp4"
                    result.write_videofile(output, fps=video.fps, codec="libx264", audio_codec="aac", 
                                         temp_audiofile='temp-audio.m4a', remove_temp=True)
                    
                    st.success("အောင်မြင်ပါသည်!")
                    st.video(output)
            except Exception as e:
                st.error(f"Error: {e}")

# အခြား Tab များကို Placeholder အနေနဲ့ ထားထားပါမည်
with tabs[0]: st.write("SRT Converter (Coming Soon)")
with tabs[2]: st.write("Text to Speech (Coming Soon)")
with tabs[3]: st.write("Video Merger (Coming Soon)")
    
