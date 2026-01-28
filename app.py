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

# --- UI Interface ---
st.set_page_config(page_title="NMH 2-Step Subtitle Tool", layout="wide")
st.title("🎬 NMH 2-Step AI Subtitle Tool")

tab1, tab2 = st.tabs(["Step 1: Video to English SRT (Whisper)", "Step 2: English to Myanmar Translation"])

# --- Part 1: Video to English SRT ---
with tab1:
    st.header("Step 1: တရုတ်/အင်္ဂလိပ် ဗီဒီယိုမှ အင်္ဂလိပ်စာတန်းထုတ်ယူခြင်း")
    video_file = st.file_uploader("Video တင်ပါ", type=["mp4", "mov", "avi"], key="vid_step1")
    
    if video_file and st.button("Generate English SRT"):
        with st.spinner("Whisper AI က ဗီဒီယိုကို နားထောင်ပြီး အင်္ဂလိပ်လို ပြန်ပေးနေပါသည်..."):
            with open("temp_v.mp4", "wb") as f:
                f.write(video_file.getbuffer())
            
            # Whisper Model Load (base သည် မြန်ဆန်ပြီး အင်္ဂလိပ်ပြန်ဆိုမှု ကောင်းမွန်ပါသည်)
            model = whisper.load_model("base")
            # task="translate" က တရုတ်ကို အင်္ဂလိပ်လို တိုက်ရိုက်ပြောင်းပေးပါသည်
            result = model.transcribe("temp_v.mp4", task="translate")
            
            srt_eng = ""
            for i, segment in enumerate(result['segments'], start=1):
                start = format_timestamp(segment['start'])
                end = format_timestamp(segment['end'])
                text = segment['text'].strip()
                srt_eng += f"{i}\n{start} --> {end}\n{text}\n\n"
            
            st.success("English SRT ထုတ်ယူမှု အောင်မြင်ပါသည်!")
            st.download_button("Download English SRT", srt_eng, "english_sub.srt")
            st.text_area("English Preview", srt_eng, height=200)
            os.remove("temp_v.mp4")

# --- Part 2: English to Myanmar Translation ---
with tab2:
    st.header("Step 2: အင်္ဂလိပ် SRT မှ မြန်မာဘာသာသို့ ပြောင်းလဲခြင်း")
    st.write("Step 1 မှ ရရှိလာသော အင်္ဂလိပ်စာတန်းဖိုင်ကို တင်ပေးပါ။")
    srt_input = st.file_uploader("English SRT ဖိုင်ကို တင်ပါ", type=["srt"], key="srt_step2")
    
    if srt_input and st.button("Start Myanmar Translation"):
        st.info("ဤအပိုင်းတွင် ပိုမိုတည်ငြိမ်သော ဘာသာပြန်စနစ်ကို အသုံးပြုရန် ပြင်ဆင်နေပါသည်...")
        # ဤနေရာတွင် ညီကိုအလိုရှိသော တခြား AI ဘာသာပြန်စနစ်တစ်ခုခုကို ထပ်မံထည့်သွင်းနိုင်ပါသည်
        eng_text = srt_input.read().decode("utf-8")
        st.text_area("Original English SRT", eng_text, height=200)
