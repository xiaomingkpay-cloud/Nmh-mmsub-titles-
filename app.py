import streamlit as st
import google.generativeai as genai
import time
import os
from deep_translator import GoogleTranslator

# --- Gemini API Config ---
# Using the new key you provided
GEMINI_API_KEY = "AIzaSyAqugREh5sZDVJQBuuy-fXBgN2V9o8pAfQ"
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

# --- UI Layout ---
st.set_page_config(page_title="NMH Subtitle Expert", layout="wide")
st.title("🎬 NMH Gemini Visual Subtitle Tool")

tab1, tab2 = st.tabs(["Step 1: Video Text to English SRT", "Step 2: English SRT to Myanmar"])

# --- Step 1: Visual Extraction ---
with tab1:
    st.header("Step 1: Generate English SRT from Video Screen")
    video_file = st.file_uploader("Upload Video File", type=["mp4", "mov", "avi"], key="v1")
    
    if video_file and st.button("Start Extraction"):
        with st.spinner("Gemini is reading the screen subtitles..."):
            temp_path = "temp_v.mp4"
            with open(temp_path, "wb") as f:
                f.write(video_file.getbuffer())
            
            try:
                g_file = upload_to_gemini(temp_path, mime_type="video/mp4")
                wait_for_files_active([g_file])
                
                # Using exact model path to resolve 404 error
                model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
                
                prompt = """
                Task: Read the Chinese hard-coded subtitles displayed on the screen. 
                Instruction: Translate those Chinese visual texts into natural English. 
                Output: Provide ONLY the raw SRT file content with accurate timestamps.
                """
                
                response = model.generate_content([g_file, prompt])
                srt_out = response.text.strip()
                
                if "```" in srt_out:
                    srt_out = srt_out.split("```")[1].replace("srt", "").strip()
                
                st.success("Step 1 Complete!")
                st.download_button("Download English SRT", srt_out, "english.srt")
                st.text_area("Preview", srt_out, height=200)
                
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

# --- Step 2: Myanmar Translation ---
with tab2:
    st.header("Step 2: English SRT to Myanmar Translation")
    srt_file = st.file_uploader("Upload English SRT File", type=["srt"], key="s2")
    
    if srt_file and st.button("Translate Now"):
        with st.spinner("Translating to Myanmar..."):
            eng_txt = srt_file.read().decode("utf-8")
            lines = eng_txt.split('\n')
            translated_srt = ""
            
            # Using stable Deep Translator
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
            
            st.success("Step 2 Complete!")
            st.download_button("Download Myanmar SRT", translated_srt, "myanmar_final.srt")
            st.text_area("Preview", translated_srt, height=200)
            
