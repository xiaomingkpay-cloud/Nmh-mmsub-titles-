import streamlit as st
import google.generativeai as genai
import time
import os
from deep_translator import GoogleTranslator

# --- Gemini API Config ---
GEMINI_API_KEY = "AIzaSyAqugREh5sZDVJQBuuy-fXBgN2V9o8pAfQ"
genai.configure(api_key=GEMINI_API_KEY)

# --- Smart Model Selector (အလိုအလျောက် Model ရှာဖွေခြင်း) ---
def get_best_model():
    try:
        # ရှိသမျှ Model တွေကို လှမ်းမေးပါတယ်
        models = [m.name for m in genai.list_models()]
        
        # Flash 1.5 ကို ဦးစားပေးရှာမယ်
        for m in models:
            if "gemini-1.5-flash" in m:
                return m
        
        # မရှိရင် Pro 1.5 ကို ရှာမယ်
        for m in models:
            if "gemini-1.5-pro" in m:
                return m
                
        # ဘာမှမတွေ့ရင် Default ကို ပြန်ပေးမယ် (Error မတက်အောင်)
        return "models/gemini-1.5-flash"
    except:
        return "models/gemini-1.5-flash"

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

# --- UI Setup ---
st.set_page_config(page_title="NMH Auto-Fix Tool", layout="wide")
st.title("🎬 NMH Intelligent Subtitle Expert")

tab1, tab2 = st.tabs(["Step 1: Visual Video to English SRT", "Step 2: English to Myanmar"])

# --- Step 1: Visual Extraction ---
with tab1:
    st.header("Step 1: Video to English (Auto-Model)")
    video_file = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"], key="v1")
    
    if video_file and st.button("Generate English SRT"):
        # အကောင်းဆုံး Model ကို အရင်ရှာပါမယ်
        active_model_name = get_best_model()
        st.info(f"Using AI Model: {active_model_name}")
        
        with st.spinner("Gemini is reading hard-subs from video..."):
            temp_path = "temp_v.mp4"
            with open(temp_path, "wb") as f:
                f.write(video_file.getbuffer())
            
            try:
                g_file = upload_to_gemini(temp_path, mime_type="video/mp4")
                wait_for_files_active([g_file])
                
                # ရှာတွေ့ထားတဲ့ Model နာမည်ကို သုံးပါမယ်
                model = genai.GenerativeModel(model_name=active_model_name)
                
                prompt = """
                Task: Read the hard-coded Chinese subtitles on the screen.
                Action: Translate the visual text into English.
                Output: Return ONLY the raw SRT format with timestamps.
                """
                
                response = model.generate_content([g_file, prompt])
                srt_out = response.text.strip()
                
                if "```" in srt_out:
                    srt_out = srt_out.split("```")[1].replace("srt", "").strip()
                
                st.success("Success! English SRT Generated.")
                st.download_button("Download English SRT", srt_out, "english.srt")
                st.text_area("Preview", srt_out, height=200)
                
            except Exception as e:
                st.error(f"Failed. Error Details: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

# --- Step 2: Translation ---
with tab2:
    st.header("Step 2: English to Myanmar")
    srt_file = st.file_uploader("Upload English SRT", type=["srt"], key="s2")
    
    if srt_file and st.button("Translate Now"):
        with st.spinner("Translating..."):
            eng_txt = srt_file.read().decode("utf-8")
            lines = eng_txt.split('\n')
            translated_srt = ""
            
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
            
            st.success("Translation Complete!")
            st.download_button("Download Myanmar SRT", translated_srt, "myanmar_final.srt")
            st.text_area("Preview", translated_srt, height=200)
            
