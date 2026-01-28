import streamlit as st
import google.generativeai as genai
import time
import os

# --- Gemini API Config ---
# ညီကိုပေးထားတဲ့ Key ကို အသုံးပြုထားပါတယ်
GEMINI_API_KEY = "AIzaSyCsB5NMrCY0OPsXx53u5W7onVAEsG0qjjE"
genai.configure(api_key=GEMINI_API_KEY)

def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    return file

def wait_for_files_active(files):
    for name in (f.name for f in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            time.sleep(2)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")

# --- UI Interface ---
st.set_page_config(page_title="NMH Gemini Subtitle Expert", layout="wide")
st.title("🎬 NMH Gemini AI Subtitle Expert")

tab1, tab2 = st.tabs(["Step 1: Video to English SRT", "Step 2: English SRT to Myanmar"])

# --- Part 1: Video to English SRT ---
with tab1:
    st.header("ဗီဒီယိုမှ အင်္ဂလိပ်စာတန်းထုတ်ယူခြင်း")
    video_file = st.file_uploader("Video တင်ပါ", type=["mp4", "mov", "avi"], key="vid_up")
    
    if video_file and st.button("Generate English SRT"):
        with st.spinner("Gemini က ဗီဒီယိုကို စတင်ကြည့်ရှုနေပါသည်... (ခဏစောင့်ပါ)"):
            temp_path = "temp_video.mp4"
            with open(temp_path, "wb") as f:
                f.write(video_file.getbuffer())
            
            # Gemini ဆီ ဗီဒီယိုပို့ခြင်း
            gemini_file = upload_to_gemini(temp_path, mime_type="video/mp4")
            wait_for_files_active([gemini_file])
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            # ဗီဒီယိုကို ကြည့်ပြီး အင်္ဂလိပ် SRT ထုတ်ခိုင်းခြင်း
            prompt = "Watch this video and generate a precise English SRT subtitle file with timestamps. Output ONLY the SRT content."
            
            response = model.generate_content([gemini_file, prompt])
            srt_eng = response.text.strip()
            
            st.success("English SRT ထွက်လာပါပြီ!")
            st.download_button("Download English SRT", srt_eng, "english_sub.srt")
            st.text_area("Preview", srt_eng, height=200)
            
            os.remove(temp_path)

# --- Part 2: English SRT to Myanmar ---
with tab2:
    st.header("အင်္ဂလိပ် SRT မှ မြန်မာဘာသာပြန်ခြင်း")
    st.write("Step 1 မှ ရလာသော english_sub.srt ဖိုင်ကို ဤနေရာတွင် ပြန်တင်ပေးပါ")
    srt_input = st.file_uploader("English SRT ဖိုင်ကို တင်ပါ", type=["srt"], key="srt_up")
    
    if srt_input and st.button("Translate to Myanmar"):
        with st.spinner("Gemini က မြန်မာလို သဘာဝကျကျ ဘာသာပြန်ပေးနေပါသည်..."):
            eng_content = srt_input.read().decode("utf-8")
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            # Gemini ကို မြန်မာလိုပဲ သီးသန့်ဘာသာပြန်ခိုင်းခြင်း
            prompt = f"Translate the following English SRT content into natural, conversational Myanmar (Burmese) language. Keep the timestamps exactly the same. Output ONLY the translated SRT content: \n\n{eng_content}"
            
            response = model.generate_content(prompt)
            srt_mm = response.text.strip()
            
            st.success("မြန်မာ SRT ရပါပြီ!")
            st.download_button("Download Myanmar SRT", srt_mm, "myanmar_final.srt")
            st.text_area("Preview", srt_mm, height=200)

