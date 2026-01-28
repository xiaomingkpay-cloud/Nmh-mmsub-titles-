import streamlit as st
import google.generativeai as genai
import time
import os
from deep_translator import GoogleTranslator

# --- Config ---
GEMINI_API_KEY = "AIzaSyAqugREh5sZDVJQBuuy-fXBgN2V9o8pAfQ"
genai.configure(api_key=GEMINI_API_KEY)

# --- Brute Force Model Selector ---
def generate_with_fallback(file_obj, prompt_text):
    # စမ်းသပ်မည့် Model နာမည်များ (တစ်ခုမရရင် တစ်ခု ပြောင်းသုံးမည်)
    model_list = [
        "gemini-1.5-flash",
        "models/gemini-1.5-flash",
        "gemini-1.5-flash-001",
        "models/gemini-1.5-flash-001",
        "gemini-1.5-flash-002",
        "models/gemini-1.5-flash-002",
        "gemini-1.5-pro",
        "models/gemini-1.5-pro"
    ]
    
    last_error = None
    
    for model_name in model_list:
        try:
            print(f"Trying model: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([file_obj, prompt_text])
            
            # Error မတက်ရင် ဒီ Model နာမည်ကို မှတ်သားပြီး အဖြေထုတ်ပေးမယ်
            return response.text.strip(), model_name
            
        except Exception as e:
            # Error တက်ရင် နောက် Model တစ်ခုကို ဆက်စမ်းမယ်
            print(f"Failed {model_name}: {e}")
            last_error = e
            continue
            
    # ဘယ်ကောင်မှ မရတော့မှ Error ထုတ်မယ်
    raise last_error

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

# --- UI ---
st.set_page_config(page_title="NMH Ultimate Fix", layout="wide")
st.title("🎬 NMH Ultimate Subtitle Tool (Brute Force Mode)")

tab1, tab2 = st.tabs(["Step 1: Visual Extraction", "Step 2: Translation"])

# --- Step 1 ---
with tab1:
    st.header("Step 1: Video -> English SRT")
    st.write("System will try ALL available models until one works.")
    
    video_file = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"], key="v1")
    
    if video_file and st.button("Generate English SRT"):
        with st.spinner("AI is finding a working model & reading subtitles..."):
            temp_path = "temp_v.mp4"
            with open(temp_path, "wb") as f:
                f.write(video_file.getbuffer())
            
            try:
                g_file = upload_to_gemini(temp_path, mime_type="video/mp4")
                wait_for_files_active([g_file])
                
                prompt = """
                Read the hard-coded Chinese subtitles on the screen.
                Translate them into English.
                Output ONLY raw SRT format with timestamps.
                """
                
                # Brute Force Function ကို ခေါ်မယ်
                srt_out, worked_model = generate_with_fallback(g_file, prompt)
                
                # Clean up format
                if "```" in srt_out:
                    srt_out = srt_out.split("```")[1].replace("srt", "").strip()
                
                st.success(f"Success! Used Model: {worked_model}")
                st.download_button("Download English SRT", srt_out, "english.srt")
                st.text_area("Preview", srt_out, height=200)
                
            except Exception as e:
                st.error(f"All models failed. Final Error: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

# --- Step 2 ---
with tab2:
    st.header("Step 2: English -> Myanmar")
    srt_file = st.file_uploader("Upload English SRT", type=["srt"], key="s2")
    
    if srt_file and st.button("Translate"):
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
            
            st.success("Done!")
            st.download_button("Download Myanmar SRT", translated_srt, "myanmar_final.srt")
            st.text_area("Preview", translated_srt, height=200)
            
