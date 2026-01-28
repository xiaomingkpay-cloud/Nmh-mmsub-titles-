import streamlit as st
import google.generativeai as genai
import time
import os

# --- Gemini API Config ---
# ညီကိုပေးထားတဲ့ Key အသစ်ကို ဒီမှာ ထည့်သွင်းထားပါတယ်
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
st.set_page_config(page_title="NMH Gemini Visual Expert", layout="wide")
st.title("🎬 NMH Gemini Visual Subtitle Maker")

tab1, tab2 = st.tabs(["Step 1: Video to English SRT", "Step 2: English SRT to Myanmar"])

# --- Step 1: Video to English (Visual Analysis) ---
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
                Translate the Chinese text into natural English. 
                Output ONLY as a raw SRT file with precise timestamps. Do not add conversational text.
                """
                
                # API ခေါ်ယူခြင်း
                response = model.generate_content([g_file, prompt])
                srt_out = response.text.strip()
                
                # Markdown block များ သန့်စင်ခြင်း
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

# --- Step 2: English to Myanmar ---
with tab2:
    st.header("Step 2: အင်္ဂလိပ် SRT ကို မြန်မာဘာသာပြန်ခြင်း")
    st.write("Step 1 မှ ရလာသော .srt ဖိုင်ကို ပြန်တင်ပေးပါ။")
    srt_file = st.file_uploader("English SRT တင်ပါ", type=["srt"], key="s2")
    
    if srt_file and st.button("Translate to Myanmar"):
        with st.spinner("မြန်မာလို ဘာသာပြန်နေပါသည်..."):
            eng_txt = srt_file.read().decode("utf-8")
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Translate this English SRT to natural, high-quality Myanmar language. Keep timestamps exactly the same. Output ONLY SRT content: \n\n{eng_txt}"
            
            response = model.generate_content(prompt)
            mm_srt = response.text.strip()
            
            if "```" in mm_srt:
                mm_srt = mm_srt.split("```")[1].replace("srt", "").strip()
            
            st.success("မြန်မာဘာသာပြန်ပြီးပါပြီ!")
            st.download_button("Download Myanmar SRT", mm_srt, "myanmar_sub.srt")
            st.text_area("Preview (Myanmar)", mm_srt, height=200)
            
