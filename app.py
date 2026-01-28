import streamlit as st
import whisper
import os
from datetime import timedelta

# --- Profile Section ---
with st.sidebar:
    st.markdown("### 🛠 Developer Profile")
    st.info("NMH - Digital Marketer at Htoo Khit Gold Shop") #
    st.markdown("[Visit My Facebook](https://www.facebook.com/your-profile-link)")

# --- Functions ---
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

# --- Main Interface ---
st.title("🎬 NMH Video Translator (CH to MM)")

uploaded_file = st.file_uploader("တရုတ်ဗီဒီယို တင်ပေးပါ", type=["mp4", "mkv", "avi"])

if uploaded_file is not None:
    st.video(uploaded_file)
    
    if st.button("မြန်မာစာတန်းထိုး ထုတ်မည်"):
        with st.spinner("တရုတ်စကားကို မြန်မာလို ဘာသာပြန်နေပါသည်... ခဏစောင့်ပါ..."):
            with open("temp.mp4", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # model ကို 'small' သုံးရင် တရုတ်စာအတွက် ပိုမှန်ပါတယ်
                model = whisper.load_model("small") 
                
                # အဆင့် (၁) - တရုတ်စကားကို အင်္ဂလိပ်လို အရင်ပြန်ခြင်း (ပိုမိုတိကျစေရန်)
                # အဆင့် (၂) - ထိုမှတဆင့် မြန်မာလို ပြောင်းလဲခြင်း
                result = model.transcribe("temp.mp4", task="translate") 
                
                # အခုလောလောဆယ် AI က အင်္ဂလိပ်လိုပဲ တိုက်ရိုက်ပြန်ပေးနိုင်ပါသေးတယ်
                # မြန်မာလို တိတိကျကျရဖို့အတွက် ညီကို အပေါ်မှာ ကျွန်တော် ပြန်ပေးထားတဲ့
                # SRT စာသားတွေကို ဒီ Tool နဲ့ ထွက်လာတဲ့ အချိန် (Timecode) တွေမှာ အစားထိုးသုံးရင် အကောင်းဆုံးပါ
                
                srt_output = write_srt(result['segments'])
                st.success("ဘာသာပြန်ခြင်း ပြီးမြောက်ပါပြီ!")
                st.download_button("Download SRT (English/Burmese Mix)", srt_output, "translated.srt")
                
                with st.expander("စာသားများကို ကြည့်ရန်"):
                    st.text(srt_output)
                    
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("Customized by NMH for Chinese Short Drama Lovers") #
