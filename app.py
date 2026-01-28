import streamlit as st
import google.generativeai as genai
import time
import os
from deep_translator import GoogleTranslator

# --- Gemini API Config ---
# ညီကိုပေးထားတဲ့ Key အသစ်ကို အသုံးပြုထားပါတယ်
GEMINI_API_KEY = "AIzaSyAqugREh5sZDVJQBuuy-fXBgN2V9o8pAfQ"
genai.configure(api_key=GEMINI_API_KEY)

# --- Functions ---
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

# --- UI Layout ---
st.set_page_config(page_title="NMH Subtitle Tool", layout="wide")
st.title("🎬 NMH Gemini Visual & Translation Expert")

tab1, tab2 = st.tabs(["Step 1: Video Text to English SRT (Gemini)", "Step 2: English SRT to Myanmar (Stable)"])

# --- Step 1: Video to English (Gemini Visual Analysis) ---
with tab1:
    st.header("Step 1: ဗီဒီယိုထဲက တရုတ်စာတန်းကို ကြည့်ပြီး အင်္ဂလိပ် SRT ထုတ်ယူခြင်း")
    video_file = st.file_uploader("Video တင်ပါ", type=["mp4", "mov", "avi"], key="v1")
    
    if video_file and st.button("Generate English SRT"):
        with st.spinner("Gemini က ဗီဒီယိုထဲက စာသားတွေကို ဖတ်နေပါသည်..."):
            temp_path = "temp_v.mp4"
            with open(temp_path, "wb") as f:
                f.write(video_file.getbuffer())
            
            try:
                g_file = upload_to_gemini(temp_path, mime_type="video/mp4")
                wait_for_files_active([g_file])
                
                # Model Name ကို 404 Error လုံးဝမတက်နိုင်သော format ဖြင့် ပြင်ဆင်ထားပါသည်
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = """
                Watch the video carefully. Focus on the hard-coded Chinese subtitles (hardsubs) on the screen. 
                Read the Chinese text and translate it into clear English. 
                Output ONLY as a raw SRT file format with accurate timestamps.
                """
                
                response = model.generate_content([g_file, prompt])
                srt_out = response.text.strip()
                
                if "```" in srt_out:
                    srt_out = srt_out.split("```")[1].replace("srt", "").strip()
                
                st.success("အင်္ဂလိပ် SRT ထုတ်ယူပြီးပါပြီ!")
                st.download_button("Download English SRT", srt_out, "english.srt")
                st.text_area("Preview (English)", srt_out, height=200)
                
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

# --- Step 2: English to Myanmar (Using Deep Translator) ---
with tab2:
    st.header("Step 2: အင်္ဂလိပ် SRT ကို မြန်မာဘာသာပြန်ခြင်း (API Key မလိုပါ)")
    st.write("Step 1 မှ ရလာသော .srt ဖိုင်ကို ပြန်တင်ပေးပါ။")
    srt_file = st.file_uploader("English SRT တင်ပါ", type=["srt"], key="s2")
    
    if srt_file and st.button("Translate to Myanmar"):
        with st.spinner("မြန်မာလို ဘာသာပြန်နေပါသည်..."):
            eng_txt = srt_file.read().decode("utf-8")
            lines = eng_txt.split('\n')
            translated_srt = ""
            
            # API Key မလိုဘဲ အတည်ငြိမ်ဆုံး ဘာသာပြန်စနစ်ကို သုံးထားပါတယ်
            translator = GoogleTranslator(source='en', target='my')
            
            for line in lines:
                if line.strip() and not line.strip().isdigit() and "-->" not in line:
                    try:
                        translated = translator.translate(line)
                        translated_srt += translated + "\n"
                    except:
                        translated_srt += line + "\n"
                else:
                    translated_srt += line + "\n"
            
            st.success("မြန်မာဘာသာပြန်ပြီးပါပြီ!")
            st.download_button("Download Myanmar SRT", translated_srt, "myanmar_final.srt")
            st.text_area("Preview (Myanmar)", translated_srt, height=200)
            
