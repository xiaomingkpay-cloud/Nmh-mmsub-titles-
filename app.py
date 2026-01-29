import streamlit as st
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import os

# --- ImageMagick Configuration ---
# Linux (Streamlit Cloud) အတွက်ဆိုရင် path ပေးစရာမလိုပါဘူး။ 
# Windows မှာ စမ်းမယ်ဆိုရင်တော့ သင့်စက်ထဲက path ကို အောက်မှာ ထည့်ပေးပါ။
if os.name == 'nt': 
    # Windows User ဖြစ်ခဲ့ရင် (Local မှာ စမ်းဖို့အတွက်)
    # ဥပမာ - r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
    os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
else:
    # Linux (Streamlit Cloud) အတွက် environment variable သတ်မှတ်စရာမလိုပါ
    pass

st.title("Myanmar Subtitle Generator")

uploaded_file = st.file_uploader("ဗီဒီယိုဖိုင် တင်ပေးပါ", type=["mp4", "mov", "avi"])

if uploaded_file:
    # ယာယီဖိုင်အဖြစ် သိမ်းဆည်းခြင်း
    with open("temp_video.mp4", "wb") as f:
        f.write(uploaded_file.read())
    
    video = VideoFileClip("temp_video.mp4")
    
    st.video("temp_video.mp4")
    
    text_input = st.text_input("ထည့်ချင်တဲ့ စာသားရေးပါ")
    
    if st.button("ဗီဒီယို ထုတ်မယ် (Render)"):
        with st.spinner("Processing... ခဏစောင့်ပေးပါ..."):
            try:
                # စာတန်းထိုး ဖန်တီးခြင်း
                txt_clip = TextClip(text_input, fontsize=50, color='white', font='Arial')
                txt_clip = txt_clip.set_pos('bottom').set_duration(video.duration)
                
                # ဗီဒီယိုနှင့် စာတန်းကို ပေါင်းခြင်း
                result = CompositeVideoClip([video, txt_clip])
                
                # ဗီဒီယိုဖိုင် ထုတ်ခြင်း (Memory သက်သာစေရန် threads လျှော့သုံးပါ)
                output_filename = "output_video.mp4"
                result.write_videofile(output_filename, codec="libx264", audio_codec="aac", fps=video.fps, threads=1)
                
                st.success("Render လုပ်ပြီးပါပြီ!")
                
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="ဗီဒီယိုကို ဒေါင်းလုဒ်လုပ်ရန်",
                        data=file,
                        file_name="mmsyub_video.mp4",
                        mime="video/mp4"
                    )
            except Exception as e:
                st.error(f"Error ဖြစ်သွားပါသည်: {e}")

