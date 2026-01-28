import streamlit as st
import whisper
import os
from datetime import timedelta

def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int(td.microseconds / 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def write_srt(segments):
    srt_content = ""
    for i, segment in enumerate(segments, start=1):
        start = format_timestamp(segment['start'])
        end = format_timestamp(segment['end'])
        text = segment['text'].strip()
        srt_content += f"{i}\n{start} --> {end}\n{text}\n\n"
    return srt_content

st.title("🎬 Myanmar Subtitle Tool")

uploaded_file = st.file_uploader("Video ရွေးပါ", type=["mp4", "mkv", "avi"])

if uploaded_file is not None:
    st.video(uploaded_file)
    if st.button("Generate Subtitle"):
        with st.spinner("AI အလုပ်လုပ်နေသည်... ခဏစောင့်ပါ..."):
            with open("temp.mp4", "wb") as f:
                f.write(uploaded_file.getbuffer())
            try:
                # Free Server မို့ model ကို 'base' သို့မဟုတ် 'small' သုံးမှ အဆင်ပြေပါမယ်
                model = whisper.load_model("base") 
                result = model.transcribe("temp.mp4") # language auto detect လုပ်ခိုင်းလိုက်ပါမယ်
                srt_output = write_srt(result['segments'])
                st.success("ပြီးပါပြီ!")
                st.download_button("Download SRT", srt_output, "sub.srt")
            except Exception as e:
                st.error(f"Error: {e}")

