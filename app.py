import streamlit as st
import whisper
import os
from datetime import timedelta
from googletrans import Translator

# AI Translator ကို စတင်ခြင်း
translator = Translator()

# SRT အချိန် Format ပြောင်းပေးသည့် Function
def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int(td.microseconds / 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

# မြန်မာ SRT ရေးသားသည့် Function
def write_srt(segments):
    srt_content = ""
    for i, segment in enumerate(segments, start=1):
        start = format_timestamp(segment['start'])
        end = format_timestamp(segment['end'])
        
        # မူရင်းစာသား (English/Chinese) ကို မြန်မာသို့ ပြန်ခြင်း
        original_text = segment['text'].strip()
        try:
            # တရုတ် သို့မဟုတ် အင်္ဂလိပ်မှ မြန်မာသို့ ပြန်ရန်
            translated = translator.translate(original_text, dest='my')
            mm_text = translated.text
        except:
            mm_text = original_text # Error ရှိပါက မူရင်းစာသားပြရန်
            
        srt_content += f"{i}\n{start} --> {end}\n{text}\n\n"
    return srt_content

# --- Website UI ---
st.set_page_config(page_title="NMH Subtitle Tool", page_icon="🎬")

st.title("🇲🇲 Myanmar Auto Subtitle Generator")
st.write("NMH (Digital Marketer at Htoo Khit Gold Shop) မှ ဖန်တီးထားပါသည်") #

# Sidebar Profile
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/000000/user-male-circle.png")
    st.markdown("### NMH Developer")
    st.write("Digital Marketing specialist interested in AI and Tech.") #
    st.markdown("[Visit My Facebook](https://www.facebook.com/your-profile-link)")

uploaded_file = st.file_uploader("ဗီဒီယို တင်ပေးပါ (Video File Only)", type=["mp4", "mkv", "avi", "mov"])

if uploaded_file is not None:
    st.video(uploaded_file)
    if st.button("မြန်မာစာတန်းထိုး (SRT) စတင်ထုတ်မည်"):
        with st.spinner("AI က မြန်မာစာတန်းထိုးများကို အချိန်ကိုက် ဖန်တီးနေပါသည်..."):
            with open("temp_video.mp4", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # 'base' model ကို အသုံးပြုထားပါသည်
                model = whisper.load_model("base")
                # task="translate" က တရုတ်ကို အင်္ဂလိပ်အရင်ပြန်ပေးမှာပါ
                result = model.transcribe("temp_video.mp4", task="translate")
                
                # အင်္ဂလိပ်မှ မြန်မာသို့ ထပ်ဆင့် ဘာသာပြန်ခြင်း
                srt_output = write_srt(result['segments'])
                
                st.success("မြန်မာ SRT ထုတ်ယူမှု အောင်မြင်ပါသည်!")
                st.download_button("Download Myanmar SRT File", srt_output, "myanmar_sub.srt")
                
                with st.expander("စာသားများကို ကြည့်ရှုရန်"):
                    st.text(srt_output)
            except Exception as e:
                st.error(f"Error ဖြစ်ပွားပါသည်: {e}")
                
