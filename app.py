import streamlit as st
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import os

# အရေးကြီးသည်- Windows path သတ်မှတ်ချက်များကို လုံးဝမသုံးပါနှင့်

st.title("Myanmar Subtitle Generator")

uploaded_file = st.file_uploader("ဗီဒီယိုတင်ပါ", type=["mp4", "mov"])

if uploaded_file:
    # ဗီဒီယိုဖိုင်ကို သိမ်းဆည်းခြင်း
    with open("input_video.mp4", "wb") as f:
        f.write(uploaded_file.read())
    
    st.video("input_video.mp4")

    if st.button("Render Video"):
        try:
            with st.spinner('ဗီဒီယို ဖန်တီးနေသည်... ခေတ္တစောင့်ပါ'):
                video = VideoFileClip("input_video.mp4")
                
                # မြန်မာစာ စာတန်းထိုးထည့်ခြင်း
                # font file နာမည်ကို သင့် GitHub ထဲက 'myanmar_font.ttf' နဲ့ အညီထားပါ
                txt_clip = TextClip(
                    "မြန်မာစာတန်းထိုး စမ်းသပ်ခြင်း", 
                    fontsize=50, 
                    color='white', 
                    font="myanmar_font.ttf"
                )
                
                txt_clip = txt_clip.set_pos(('center', 'bottom')).set_duration(video.duration)
                
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
            st.error(f"Error ဖြစ်သွားပါသည်: {e}")
            
