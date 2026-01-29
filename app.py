import streamlit as st
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import os

st.title("Video Subtitle Generator")

# Cloud ပေါ်မှာ ImageMagick Path သတ်မှတ်စရာမလိုပါ (packages.txt က လုပ်ပေးပါလိမ့်မယ်)
# Windows မှာလိုမျိုး IMAGEMAGICK_BINARY path တွေ ဒီမှာ လုံးဝ မထည့်ပါနဲ့။

uploaded_file = st.file_uploader("Video ဖိုင်တင်ပါ", type=["mp4", "mov"])

if uploaded_file:
    # ဗီဒီယိုဖိုင်ကို ခေတ္တသိမ်းဆည်းခြင်း
    with open("input_video.mp4", "wb") as f:
        f.write(uploaded_file.read())
    
    st.video("input_video.mp4")

    if st.button("Render Video"):
        try:
            with st.spinner('ဗီဒီယို ဖန်တီးနေသည်... ခေတ္တစောင့်ပါ'):
                video = VideoFileClip("input_video.mp4")
                
                # စာတန်းထိုးထည့်ခြင်း (နမူနာ)
                txt_clip = TextClip("Hello World", fontsize=70, color='white')
                txt_clip = txt_clip.set_pos('center').set_duration(video.duration)
                
                final_video = CompositeVideoClip([video, txt_clip])
                
                # Cloud အတွက် အကောင်းဆုံး Rendering settings
                output_path = "output_result.mp4"
                final_video.write_videofile(
                    output_path, 
                    fps=24, 
                    codec="libx264", 
                    audio_codec="aac",
                    temp_audiofile="temp-audio.m4a", 
                    remove_temp=True
                )
                
                st.success("Rendering ပြီးပါပြီ!")
                st.video(output_path)
                
        except Exception as e:
            st.error(f"Error တက်သွားပါတယ်: {e}")
            
