import streamlit as st
import whisper
import os
from datetime import timedelta
from googletrans import Translator

# AI Translator စနစ်
translator = Translator()

def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int(td.microseconds / 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def translate_and_write_srt(segments):
    srt_content = ""
    for i, segment in enumerate(segments, start=1):
        start = format_timestamp(segment['start'])
        end = format_timestamp(segment['end'])
        
        # မူရင်းစကားသံကို မြန်မာသို့ ပြန်ခြင်း
        original_text = segment['text'].strip()
        try:
            translated = translator.translate(original_text, dest='my')
            mm_text = translated.text
        except:
            mm_text = original_text
            
        srt_content += f"{i}\n{start} --> {end}\n{mm_text}\n\n"
    return srt_content

# --- Website Design ---
st.set_page_config(page_title="NMH Myanmar Sub Tool", page_icon="🎬")

st.title("🇲🇲 Myanmar Auto Subtitle Generator")
st.write("NMH (Digital Marketer at Htoo Khit Gold Shop) မှ စီစဉ်တင်ဆက်သည်")

with st.sidebar:
    st.markdown("### 🛠 Developer Profile")
    st.info("NMH - AI & Digital Marketing Enthusiast")
    st.markdown("[Visit Facebook Page](https://www.facebook.com/your-profile-link)")

uploaded_file = st.file_uploader("ဗီဒီယို ဖိုင်တင်ပေးပါ", type=["mp4", "mkv", "avi", "mov"])

if uploaded_file is not None:
    st.video(uploaded_file)
    if st.button("မြန်မာ SRT စတင်ထုတ်မည်"):
        with st.spinner("AI က မြန်မာစာတန်းထိုးများကို အချိန်ကိုက် ဖန်တီးနေပါသည်... ခဏစောင့်ပါ..."):
            with open("temp_v.mp4", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # Whisper model 'base' သုံးခြင်းဖြင့် ပိုမြန်စေပါသည်
                model = whisper.load_model("base")
                # task="translate" ကို သုံးပြီး အင်္ဂလိပ်မှတစ်ဆင့် မြန်မာသို့ ပြန်ပါမည်
                result = model.transcribe("temp_v.mp4", task="translate")
                
                # မြန်မာ SRT ထုတ်ယူခြင်း
                srt_output = translate_and_write_srt(result['segments'])
                
                st.success("မြန်မာစာတန်းထိုး ထုတ်ယူမှု အောင်မြင်ပါသည်!")
                st.download_button("Download Myanmar SRT", srt_output, "myanmar_subtitle.srt")
                
                with st.expander("စာသားများကို ကြည့်ရှုရန်"):
                    st.text(srt_output)
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                if os.path.exists("temp_v.mp4"):
                    os.remove("temp_v.mp4")
                    
