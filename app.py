import streamlit as st
import google.generativeai as genai
import time
import os

# --- Gemini API Config ---
# ညီကိုပေးထားတဲ့ API Key ကို အသုံးပြုထားပါတယ်
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
st.set_page_config(page_title="NMH Visual Subtitle Expert", layout="wide")
st.title("🎬 NMH Visual Subtitle Expert (Gemini 1.5)")

tab1, tab2 = st.tabs(["Step 1: Video Text to English SRT", "Step 2: English SRT to Myanmar"])

# --- Part 1: Video Visual to English SRT ---
with tab1:
    st.header("Step 1: ဗီဒီယိုထဲက စာသားကိုကြည့်ပြီး အင်္ဂလိပ်စာတန်းထုတ်ယူခြင်း")
    video_file = st.file_uploader("ဗီဒီယို တင်ပါ (တရုတ်စာတန်းပါသော ဗီဒီယိုပိုကောင်းပါသည်)", type=["mp4", "mov", "avi"], key="vid_up")
    
    if video_file and st.button("Generate English SRT (Visual Based)"):
        with st.spinner("Gemini က ဗီဒီယိုထဲက တရုတ်စာတန်းတွေကို ဖတ်ပြီး ဘာသာပြန်နေပါသည်..."):
            temp_path = "temp_video.mp4"
            with open(temp_path, "wb") as f:
                f.write(video_file.getbuffer())
            
            try:
                gemini_file = upload_to_gemini(temp_path, mime_type="video/mp4")
                wait_for_files_active([gemini_file])
                
                # Model ကို models/gemini-1.5-flash လို့ အတိအကျ သတ်မှတ်ပါတယ်
                model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
                
                # ဗီဒီယိုထဲက စာသားကိုပါ ကြည့်ခိုင်းသည့် Prompt
                prompt = """
                Watch this video carefully. Read the Chinese subtitles (hardsubs) displayed in the video and listen to the audio. 
                Translate the Chinese text accurately into English and generate a precise SRT file with timestamps.
                Output ONLY the raw SRT content.
                """
                
                response = model.generate_content([gemini_file, prompt])
                srt_eng = response.text.strip()
                
                # Markdown ဖယ်ရှားခြင်း
                if "```" in srt_eng:
                    srt_eng = srt_eng.split("```")[1].replace("srt", "").strip()
                
                st.success("ဗီဒီယိုကို ကြည့်ပြီး အင်္ဂလိပ် SRT ထုတ်ယူပြီးပါပြီ!")
                st.download_button("Download English SRT", srt_eng, "english_visual.srt")
                st.text_area("Preview (English)", srt_eng, height=200)
                
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

# --- Part 2: English SRT to Myanmar ---
with tab2:
    st.header("Step 2: အင်္ဂလိပ် SRT မှ မြန်မာဘာသာပြန်ခြင်း")
    srt_input = st.file_uploader("English SRT ဖိုင်ကို တင်ပါ", type=["srt"], key="srt_up")
    
    if srt_input and st.button("Translate to Myanmar"):
        with st.spinner("Gemini AI က မြန်မာလို အလှပဆုံး ဘာသာပြန်ပေးနေပါသည်..."):
            eng_content = srt_input.read().decode("utf-8")
            
            model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
            prompt = f"Translate the following English SRT content into natural, conversational Myanmar language. Keep the timestamps exactly the same. Output ONLY the translated SRT content: \n\n{eng_content}"
            
            response = model.generate_content(prompt)
            srt_mm = response.text.strip()
            
            if "```" in srt_mm:
                srt_mm = srt_mm.split("```")[1].replace("srt", "").strip()
            
            st.success("မြန်မာ SRT ရပါပြီ!")
            st.download_button("Download Myanmar SRT", srt_mm, "myanmar_final.srt")
            st.text_area("Preview (Myanmar)", srt_mm, height=200)
            
