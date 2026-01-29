import streamlit as st
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import os

# Page Setting
st.set_page_config(page_title="Myanmar Subtitle App", layout="wide")

# Sidebar သို့မဟုတ် Tabs များပြုလုပ်ခြင်း
tab1, tab2, tab3, tab4 = st.tabs(["🎥 Video Upload", "✍️ Subtitles", "⚙️ Settings", "👤 Creator Info"])

with tab1:
    st.header("ဗီဒီယိုတင်ရန်")
    uploaded_file = st.file_uploader("ဗီဒီယိုဖိုင်ကို ဒီမှာတင်ပါ", type=["mp4", "mov", "mpeg4"])
    if uploaded_file:
        with open("input_video.mp4", "wb") as f:
            f.write(uploaded_file.read())
        st.video("input_video.mp4")
        st.success("ဗီဒီယို တင်ပြီးပါပြီ။ Tab 2 မှာ စာသားသွားထည့်ပါ။")

with tab2:
    st.header("စာတန်းထိုးထည့်ရန်")
    sub_text = st.text_input("ထည့်ချင်သည့် စာသားကို ရေးပါ", "မြန်မာစာတန်းထိုး")
    font_size = st.slider("စာလုံးအရွယ်အစား", 20, 100, 50)
    color = st.color_picker("စာလုံးအရောင်", "#FFFFFF")
    
    if st.button("Render Video"):
        if os.path.exists("input_video.mp4"):
            try:
                with st.spinner('ဗီဒီယို ဖန်တီးနေသည်...'):
                    video = VideoFileClip("input_video.mp4")
                    txt_clip = TextClip(sub_text, fontsize=font_size, color=color, font="myanmar_font.ttf")
                    txt_clip = txt_clip.set_pos(('center', 'bottom')).set_duration(video.duration)
                    
                    final_video = CompositeVideoClip([video, txt_clip])
                    output_path = "output_result.mp4"
                    
                    final_video.write_videofile(
                        output_path, 
                        fps=24, 
                        codec="libx264", 
                        audio_codec="aac",
                        temp_audiofile="temp-audio.m4a", 
                        remove_temp=True
                    )
                    st.success("ပြီးပါပြီ!")
                    st.video(output_path)
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("အရင်ဦးဆုံး Tab 1 မှာ ဗီဒီယိုတင်ပေးပါ။")

with tab3:
    st.header("အထွေထွေ Setting")
    st.write("Video Resolution နှင့် အခြား Setting များကို ဤနေရာတွင် ပြင်နိုင်သည် (Coming Soon)")

with tab4:
    st.header("Creator Information")
    st.write("**Facebook:** [https://www.facebook.com/share/1aavUJzZ9f/](https://www.facebook.com/share/1aavUJzZ9f/)")
    st.write("**Telegram:** @xiaoming2025nmx")
    st.info("ဒီ App ကို Myanmar Subtitle အတွက် အထူးပြုလုပ်ထားပါသည်။")
    
