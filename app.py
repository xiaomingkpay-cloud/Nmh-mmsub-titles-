import streamlit as st
import whisper
import os
from datetime import timedelta
from deep_translator import GoogleTranslator

# အချိန်မှတ်တမ်း Format ပြောင်းသည့် Function
def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int(td.microseconds / 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

# --- UI Interface ---
st.set_page_config(page_title="NMH Free Subtitle Tool", layout="wide")
st.title("🎬 NMH 100% Free AI Subtitle Maker")

tab1, tab2 = st.tabs(["Step 1: Video to English SRT", "Step 2: English SRT to Myanmar"])

# --- Part 1: Video to English SRT ---
with tab1:
    st.header("Step 1: ဗီဒီယိုမှ အင်္ဂလိပ်စာတန်းထုတ်ယူခြင်း (Whisper)")
    video_file = st.file_uploader("Video တင်ပါ", type=["mp4", "mov", "avi"], key="v1")
    
    if video_file and st.button("Generate English SRT"):
        with st.spinner("AI က အသံကို နားထောင်ပြီး အင်္ဂလိပ်လို ပြန်ပေးနေပါသည်..."):
            with open("temp_v.mp4", "wb") as f:
                f.write(video_file.getbuffer())
            
            # Whisper က အခမဲ့ သုံးလို့ရတဲ့ model ဖြစ်ပါတယ်
            model = whisper.load_model("base")
            result = model.transcribe("temp_v.mp4", task="translate")
            
            srt_eng = ""
            for i, segment in enumerate(result['segments'], start=1):
                start = format_timestamp(segment['start'])
                end = format_timestamp(segment['end'])
                text = segment['text'].strip()
                srt_eng += f"{i}\n{start} --> {end}\n{text}\n\n"
            
            st.success("English SRT ရပါပြီ!")
            st.download_button("Download English SRT", srt_eng, "english.srt")
            st.text_area("English Preview", srt_eng, height=200)
            os.remove("temp_v.mp4")

# --- Part 2: English SRT to Myanmar ---
with tab2:
    st.header("Step 2: အင်္ဂလိပ် SRT မှ မြန်မာဘာသာသို့ ပြောင်းလဲခြင်း (Free)")
    srt_input = st.file_uploader("English SRT ဖိုင်ကို တင်ပါ", type=["srt"], key="s2")
    
    if srt_input and st.button("Translate to Myanmar"):
        with st.spinner("မြန်မာလို အခမဲ့ ဘာသာပြန်ပေးနေပါသည်..."):
            eng_content = srt_input.read().decode("utf-8")
            lines = eng_content.split('\n')
            translated_srt = ""
            
            # API Key လုံးဝ မလိုသော Translator ဖြစ်ပါတယ်
            translator = GoogleTranslator(source='en', target='my')
            
            for line in lines:
                # အချိန် သို့မဟုတ် ဂဏန်းမဟုတ်လျှင် ဘာသာပြန်မည်
                if line.strip() and not line.strip().isdigit() and "-->" not in line:
                    try:
                        translated = translator.translate(line)
                        translated_srt += translated + "\n"
                    except:
                        translated_srt += line + "\n"
                else:
                    translated_srt += line + "\n"
            
            st.success("မြန်မာ SRT ဘာသာပြန်ခြင်း အောင်မြင်ပါသည်!")
            st.download_button("Download Myanmar SRT", translated_srt, "myanmar_final.srt")
            st.text_area("Myanmar Preview", translated_srt, height=200)

