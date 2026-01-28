import streamlit as st
import whisper
import os
from datetime import timedelta
from googletrans import Translator

# AI ဘာသာပြန်ပေးမည့် စက်
translator = Translator()

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
        
        # အင်္ဂလိပ်စာကို မြန်မာစာသို့ ပြောင်းခြင်း
        eng_text = segment['text'].strip()
        try:
            mm_text = translator.translate(eng_text, src='en', dest='my').text
        except:
            mm_text = eng_text # Error တက်ရင် မူရင်းစာပဲပြမယ်
            
        srt_content += f"{i}\n{start} --> {end}\n{mm_text}\n\n"
    return srt_content

st.title("🇲🇲 Myanmar Auto SRT Generator")

uploaded_file = st.file_uploader("Video တင်ပေးပါ", type=["mp4", "mkv", "avi"])

if uploaded_file is not None:
    st.video(uploaded_file)
    if st.button("မြန်မာစာတန်းထိုး စတင်ထုတ်မည်"):
        with st.spinner("မြန်မာလို ဘာသာပြန်နေပါပြီ... ခဏစောင့်ပါ..."):
            with open("temp.mp4", "wb") as f:
                f.write(uploaded_file.getbuffer())
            try:
                # 'base' model က မြန်မာစာအတွက် ပိုမြန်ပါတယ်
                model = whisper.load_model("base") 
                # တရုတ်မှ အင်္ဂလိပ်သို့ အရင်ပြန်ခိုင်းပါသည်
                result = model.transcribe("temp.mp4", task="translate") 
                
                # အင်္ဂလိပ်မှ မြန်မာသို့ ထပ်ဆင့်ပြန်ပြီး SRT ထုတ်ပါသည်
                srt_output = write_srt(result['segments'])
                
                st.success("မြန်မာ SRT ထုတ်ယူမှု အောင်မြင်ပါသည်!")
                st.download_button("Download Myanmar SRT", srt_output, "myanmar.srt")
                
                with st.expander("စာသားများ ကြည့်ရန်"):
                    st.text(srt_output)
            except Exception as e:
                st.error(f"Error: {e}")
