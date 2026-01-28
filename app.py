import streamlit as st
import ffmpeg
import os

st.set_page_config(page_title="NMH Hardsubber", layout="wide")
st.title("🎬 NMH Video Hardsub Tool (Fixed Font)")
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
        with st.spinner("Video ထဲသို့ မြန်မာစာတန်းများ ထည့်သွင်းနေပါသည်..."):
            
            input_video = "input_video.mp4"
            input_srt = "input_subs.srt"
            output_video = "output_hardsub.mp4"
            
            # Font ဖိုင်နာမည် (GitHub မှာ တင်ထားတဲ့ နာမည်အတိုင်း ဖြစ်ရပါမယ်)
            font_path = "myanmar_font.ttf" 
            
            # Font ဖိုင် တကယ်ရှိမရှိ စစ်ဆေးခြင်း
            if not os.path.exists(font_path):
                st.error(f"⚠️ '{font_path}' ဖိုင်ကို GitHub မှာ မတွေ့ပါ။ Font ဖိုင်တင်ပြီး နာမည်တူအောင် ပေးပါ။")
                st.stop()

            # ဖိုင်များ သိမ်းဆည်းခြင်း
            with open(input_video, "wb") as f:
                f.write(video_file.getbuffer())
            with open(input_srt, "wb") as f:
                f.write(srt_file.getbuffer())
                
            try:
                # FFmpeg ဖြင့် Font ဖိုင်ကို အသုံးပြုပြီး စာတန်းမြှုပ်ခြင်း
                # fontsdir=. ဆိုတာ လက်ရှိ Folder ထဲက Font ကို ရှာခိုင်းတာပါ
                # FontName=MyanmarFont ဆိုတာ လှမ်းခေါ်မည့် နာမည်ပါ (စိတ်ကြိုက်ပေးလို့ရသည်)
                
                stream = ffmpeg.input(input_video)
                
                # အရေးကြီးသော အပိုင်း - fontsdir နှင့် fontfile ကို ထည့်သွင်းခြင်း
                video = ffmpeg.output(
                    stream, 
                    output_video, 
                    # ဒီနေရာမှာ အပြောင်းအလဲ လုပ်ထားပါတယ်
                    vf=f"subtitles={input_srt}:fontsdir=.:force_style='FontName=myanmar_font,FontSize=24'"
                )
                
                ffmpeg.run(video, overwrite_output=True)
                
                st.success("အောင်မြင်ပါသည်! မြန်မာစာ မှန်ကန်စွာ ပေါ်ပါလိမ့်မည်။")
                
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
                    st.error("Unknown FFmpeg error")
            
            # Cleanup
            if os.path.exists(input_video): os.remove(input_video)
            if os.path.exists(input_srt): os.remove(input_srt)
            if os.path.exists(output_video): os.remove(output_video)
                
