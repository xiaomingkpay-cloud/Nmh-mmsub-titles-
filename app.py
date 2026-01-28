import streamlit as st
import ffmpeg
import os
import shutil
from pathlib import Path

st.set_page_config(page_title="NMH Hardsubber", layout="wide")
st.title("🎬 NMH Video Hardsub Tool (System Font Fix)")
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
    if st.button("Start Burning (စာတန်းမြှုပ်မည်)"):
        with st.spinner("Font များကို System ထဲသို့ ထည့်သွင်းနေပါသည်..."):
            
            # --- Step 1: Font Installation (အဓိက ပြင်ဆင်ချက်) ---
            # GitHub ပေါ်က myanmar_font.ttf ကို ယူပါမယ်
            font_source = "myanmar_font.ttf"
            
            # Linux System ရဲ့ Font သိမ်းတဲ့ နေရာကို ရှာပြီး ဖိုင်ကူးထည့်ပါမယ်
            # ဒီလိုလုပ်လိုက်ရင် FFmpeg က "Padauk" လို့ ခေါ်လိုက်တာနဲ့ တန်းသိသွားပါလိမ့်မယ်
            user_font_dir = Path.home() / ".fonts"
            user_font_dir.mkdir(exist_ok=True)
            
            if os.path.exists(font_source):
                # System ထဲရောက်ရင် နာမည်ရင်းအတိုင်း ပြန်ထားလိုက်ပါမယ်
                destination = user_font_dir / "Padauk.ttf"
                shutil.copy(font_source, destination)
                
                # Font Cache ကို Update လုပ်ခြင်း (ကွန်ပျူတာကို Font အသစ်ရောက်ကြောင်း ပြောခြင်း)
                os.system("fc-cache -fv")
            else:
                st.error("⚠️ 'myanmar_font.ttf' ကို GitHub မှာ မတွေ့ပါ။")
                st.stop()

            # --- Step 2: File Processing ---
            input_video = "input_video.mp4"
            input_srt = "input_subs.srt"
            output_video = "output_hardsub.mp4"
            
            with open(input_video, "wb") as f:
                f.write(video_file.getbuffer())
            with open(input_srt, "wb") as f:
                f.write(srt_file.getbuffer())
                
            try:
                with st.spinner("Video ထုတ်လုပ်နေပါသည် (ခဏစောင့်ပါ)..."):
                    # --- Step 3: FFmpeg Burning ---
                    stream = ffmpeg.input(input_video)
                    
                    video = ffmpeg.output(
                        stream, 
                        output_video, 
                        # FontName=Padauk လို့ ခေါ်လိုက်တာနဲ့ ခုနက ထည့်ထားတဲ့ Font ကို ယူသုံးပါလိမ့်မယ်
                        vf=f"subtitles={input_srt}:force_style='FontName=Padauk,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1,Shadow=0'"
                    )
                    
                    ffmpeg.run(video, overwrite_output=True)
                    
                    st.success("အောင်မြင်ပါသည်! မြန်မာစာ အမှန်အတိုင်း ပေါ်ပါပြီ။")
                    
                    with open(output_video, "rb") as f:
                        st.download_button(
                            label="Download Final Video",
                            data=f.read(),
                            file_name="myanmar_hardsub_video.mp4",
                            mime="video/mp4"
                        )
                        
                    st.video(output_video)
                
            except ffmpeg.Error as e:
                st.error("Video ပြုလုပ်ရာတွင် Error ဖြစ်သွားပါသည်။")
                try:
                    st.error(e.stderr.decode('utf8'))
                except:
                    pass
            
            # Cleanup
            if os.path.exists(input_video): os.remove(input_video)
            if os.path.exists(input_srt): os.remove(input_srt)
            if os.path.exists(output_video): os.remove(output_video)
                
