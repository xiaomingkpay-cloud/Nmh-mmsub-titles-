import streamlit as st
import ffmpeg
import os

st.set_page_config(page_title="NMH Video Hardsubber", layout="wide")
st.title("🎬 NMH Video Hardsub Tool (Subtitle Burner)")
st.write("Video နှင့် မြန်မာ SRT ဖိုင်ကို တင်ပြီး စာတန်းမြှုပ် Video ထုတ်ယူပါ။")

# --- UI Uploads ---
col1, col2 = st.columns(2)
with col1:
    video_file = st.file_uploader("၁။ Video ဖိုင် တင်ပါ", type=["mp4", "mov", "avi"])
with col2:
    srt_file = st.file_uploader("၂။ Myanmar SRT ဖိုင် တင်ပါ", type=["srt"])

# --- Processing ---
if video_file and srt_file:
    st.write("---")
    if st.button("Start Burning Subtitles (စာတန်းမြှုပ်မည်)"):
        with st.spinner("Video ထဲသို့ စာတန်းများ ထည့်သွင်းနေပါသည် (ခဏစောင့်ပါ)..."):
            
            # 1. ဖိုင်များကို ယာယီသိမ်းဆည်းခြင်း
            input_video = "input_video.mp4"
            input_srt = "input_subs.srt"
            output_video = "output_hardsub.mp4"
            
            with open(input_video, "wb") as f:
                f.write(video_file.getbuffer())
            with open(input_srt, "wb") as f:
                f.write(srt_file.getbuffer())
                
            try:
                # 2. FFmpeg ဖြင့် စာတန်းမြှုပ်ခြင်း
                # Note: force_style is used to ensure font size is visible
                stream = ffmpeg.input(input_video)
                stream = ffmpeg.output(stream, output_video, vf=f"subtitles={input_srt}:force_style='FontSize=24'")
                ffmpeg.run(stream, overwrite_output=True)
                
                # 3. ရလာတဲ့ Video ကို Download ပေးခြင်း
                st.success("အောင်မြင်ပါသည်! အောက်တွင် Download ရယူပါ။")
                
                with open(output_video, "rb") as f:
                    video_bytes = f.read()
                    st.download_button(
                        label="Download Video with Subtitles",
                        data=video_bytes,
                        file_name="myanmar_subtitled_video.mp4",
                        mime="video/mp4"
                    )
                    
                # Preview (Optional)
                st.video(output_video)
                
            except ffmpeg.Error as e:
                st.error("Video ပြုလုပ်ရာတွင် Error ဖြစ်သွားပါသည်။")
                st.error(e.stderr.decode('utf8'))
            except Exception as e:
                st.error(f"Error: {e}")
                
            # Cleanup
            if os.path.exists(input_video): os.remove(input_video)
            if os.path.exists(input_srt): os.remove(input_srt)
            if os.path.exists(output_video): os.remove(output_video)
                
