import streamlit as st
import os
import pysubs2
from datetime import datetime
from streamlit.web.server.websocket_headers import _get_websocket_headers
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import nest_asyncio
import subprocess

nest_asyncio.apply()

# Website ခေါင်းစဉ်
st.set_page_config(page_title="NMH Pro Creator Tools", layout="wide")

# ==========================================
# 🛡️ SECURITY & TRACKER
# ==========================================
@st.cache_resource
def get_usage_data():
    return {"date": datetime.now().strftime("%Y-%m-%d"), "users": {}, "bindings": {}}

usage_data = get_usage_data()
current_date = datetime.now().strftime("%Y-%m-%d")
if usage_data["date"] != current_date:
    usage_data["date"] = current_date
    usage_data["users"] = {} 

def get_remote_ip():
    try:
        headers = _get_websocket_headers()
        ip = headers.get("X-Forwarded-For")
        if ip: return ip.split(",")[0]
    except: pass
    return "unknown_user"

# ==========================================
# 📅 EXPIRY CHECK
# ==========================================
def check_code_validity(user_value):
    if "|" in user_value:
        try:
            name_part, date_part = user_value.split("|")
            name = name_part.strip()
            expiry_str = date_part.strip()
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            today = datetime.now().date()
            if today > expiry_date:
                return False, name, f"⛔ ကုဒ်သက်တမ်းကုန်ဆုံးသွားပါပြီ။ (Expired on: {expiry_str})"
            else:
                return True, name, None
        except:
            return True, user_value, None
    else:
        return True, user_value, None

# ==========================================
# 🔄 AUTO LOGIN
# ==========================================
def check_auto_login():
    if "user_info" in st.session_state and st.session_state.user_info is not None:
        return
    current_ip = get_remote_ip()
    for code, bound_ip in usage_data["bindings"].items():
        if bound_ip == current_ip:
            if "users" in st.secrets and code in st.secrets["users"]:
                raw_value = st.secrets["users"][code]
                is_valid, user_name, error_msg = check_code_validity(raw_value)
                if is_valid:
                    st.session_state.user_info = user_name
                    st.toast(f"ကြိုဆိုပါတယ် {user_name}! (Auto Login)", icon="✅")
                    return
                else:
                    del usage_data["bindings"][code]
                    return
check_auto_login()

if "user_info" not in st.session_state:
    st.session_state.user_info = None

# ==========================================
# 🏠 HEADER
# ==========================================
st.title("✨ NMH Pro Creator Tools")
st.success("📢 Professional Video Tools: အသံဖိုင်ပေါင်းခြင်း၊ စာတန်းထိုးခြင်းများကို Error ကင်းစွာ လုပ်ဆောင်နိုင်ပါသည်။")

tab1, tab2, tab3, tab4 = st.tabs([
    "Tab 1: 🌐 SRT စာသားထုတ်ရန်", 
    "Tab 2: 📝 စာတန်းမြှုပ် (Free)", 
    "Tab 3: 🗣️ အသံဖိုင်ထုတ်ရန် (VIP)", 
    "Tab 4: 🎬 Video ပေါင်းရန် (VIP)"
])

# ==========================================
# TAB 1: GEMINI SRT
# ==========================================
with tab1:
    st.header("အဆင့် ၁ - Gemini မှ SRT စာသားတောင်းယူပါ")
    st.link_button("🚀 Google Gemini သို့သွားရန် နှိပ်ပါ", "https://gemini.google.com/")
    st.info("Gemini တွင် 'Generate Myanmar SRT file for this video' ဟု ရေးပြီး တောင်းပါ။")
    srt_text_input = st.text_area("Gemini မှပေးလိုက်သော SRT စာသားများကို ဒီအကွက်ထဲ Paste ချပါ:", height=300)
    if srt_text_input and st.button("SRT ဖိုင်အဖြစ် ပြောင်းမည်"):
        clean_text = srt_text_input.replace("```srt", "").replace("```", "").strip()
        output_srt = "manual_converted.srt"
        with open(output_srt, "w", encoding="utf-8") as f: f.write(clean_text)
        st.success("✅ SRT ဖိုင် ရရှိပါပြီ! ဒေါင်းယူနိုင်ပါပြီ။")
        with open(output_srt, "rb") as f: st.download_button("SRT ဖိုင် ဒေါင်းရန် (Download)", f.read(), "myanmar.srt", "text/plain")

# ==========================================
# TAB 2: BURN SUBTITLE
# ==========================================
with tab2:
    st.header("Tab 2: စာတန်းမြှုပ်ခြင်း (Free)")
    user_ip = get_remote_ip()
    if user_ip not in usage_data["users"]: usage_data["users"][user_ip] = 0
    usage_left = 3 - usage_data["users"][user_ip]
    if usage_left > 0: st.info(f"✅ ယနေ့လက်ကျန် Free Limit: {usage_left}/3 ပုဒ်")
    else: st.error("⛔ Free Limit ကုန်သွားပါပြီ။ မနက်ဖြန်မှ ပြန်ရပါမည်။")

    col1, col2 = st.columns(2)
    with col1: v1_file = st.file_uploader("Video ဖိုင် ရွေးပါ", type=["mp4", "mov"], key="v1")
    with col2: s1_file = st.file_uploader("SRT ဖိုင် ရွေးပါ", type=["srt"], key="s1")

    def generate_subtitle_clips(subtitle_path, video_width, video_height, font_path):
        subs = pysubs2.load(subtitle_path, encoding="utf-8")
        subtitle_clips = []
        try: font = ImageFont.truetype(font_path, int(video_width/25))
        except: font = ImageFont.load_default()
        for line in subs:
            if not line.text.strip(): continue
            text_w, text_h = int(video_width * 0.9), int(video_height * 0.25)
            img = Image.new('RGBA', (text_w, text_h), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            text_content = line.text.replace("\\N", "\n")
            try: draw.text((text_w/2, text_h/2), text_content, font=font, fill="white", stroke_width=3, stroke_fill="black", anchor="mm", align="center")
            except: draw.text((10, 10), text_content, font=font, fill="white", stroke_width=2, stroke_fill="black")
            clip = ImageClip(np.array(img)).set_start(line.start / 1000).set_duration((line.end - line.start) / 1000)
            clip = clip.set_position(('center', 0.80), relative=True)
            subtitle_clips.append(clip)
        return subtitle_clips

    if usage_left > 0 and v1_file and s1_file and st.button("စာတန်းမြှုပ်မည် (Start)", key="btn_free"):
        with st.spinner("လုပ်ဆောင်နေပါသည်..."):
            vp, sp, fp, op = "temp_v1.mp4", "temp_s1.srt", "myanmar_font.ttf", "output_sub.mp4"
            with open(vp, "wb") as f: f.write(v1_file.getbuffer())
            with open(sp, "wb") as f: f.write(s1_file.getbuffer())
            if not os.path.exists(fp): st.error("Font ဖိုင် မရှိပါ! (myanmar_font.ttf)")
            else:
                try:
                    video = VideoFileClip(vp)
                    sub_clips = generate_subtitle_clips(sp, video.w, video.h, fp)
                    final_video = CompositeVideoClip([video] + sub_clips)
                    final_video.write_videofile(op, fps=24, codec='libx264', preset='fast', audio_codec='aac', threads=4, ffmpeg_params=["-crf", "23"])
                    usage_data["users"][user_ip] += 1
                    st.success("အောင်မြင်ပါသည်!")
                    with open(op, "rb") as f: st.download_button("Video ဒေါင်းရန် (Download Video)", f.read(), "subbed.mp4", "video/mp4")
                except Exception as e: st.error(f"Error: {e}")
            if os.path.exists(vp): os.remove(vp)
            if os.path.exists(sp): os.remove(sp)
            if os.path.exists(op): os.remove(op)

# ==========================================
# HELPER: LOGIN UI
# ==========================================
def show_login_ui(key_suffix):
    st.warning("🔒 ဤနေရာကို ဝင်ရောက်ရန် VIP ကုဒ် (Code) လိုအပ်ပါသည်။")
    col_pass1, _ = st.columns([3, 1])
    with col_pass1: 
        token_input = st.text_input("VIP ကုဒ် ရိုက်ထည့်ပါ:", type="password", key=f"pro_token_{key_suffix}")
    if st.button("VIP အကောင့်ဝင်မည်", key=f"btn_login_{key_suffix}"):
        if "users" in st.secrets and token_input in st.secrets["users"]:
            raw_value = st.secrets["users"][token_input]
            is_valid, user_name, error_msg = check_code_validity(raw_value)
            if not is_valid:
                st.error(error_msg)
                return
            current_ip = get_remote_ip()
            if token_input == "nmh-123":
                st.session_state.user_info = user_name
                st.rerun()
            else:
                if token_input not in usage_data["bindings"]:
                    usage_data["bindings"][token_input] = current_ip
                    st.session_state.user_info = user_name
                    st.rerun()
                elif usage_data["bindings"][token_input] == current_ip:
                    st.session_state.user_info = user_name
                    st.rerun()
                else: st.error("⛔ Device Locked: ဤကုဒ်ကို အခြားဖုန်းတစ်ခုတွင် သုံးနေပါသည်။")
        else: st.error("ကုဒ် မှားယွင်းနေပါသည်။")

# ==========================================
# TAB 3: GOOGLE AI STUDIO (FULL GUIDE)
# ==========================================
with tab3:
    st.header("Tab 3: အသံဖိုင်ထုတ်လုပ်နည်း (Audio Generation)")
    if st.session_state.user_info is None:
        show_login_ui("t3")
    else:
        st.success(f"✅ VIP အကောင့်ဖြင့် ဝင်ရောက်ထားပါသည်: {st.session_state.user_info}")
        
        # --- Voice Recommendations ---
        st.markdown("### 🔊 အသံရွေးချယ်ရန် လမ်းညွှန်")
        
        col_m, col_f = st.columns(2)
        with col_m:
            st.info("""
            **👨 ယောက်ျားအသံ (Male) လိုချင်ပါက:**
            * **Charon** (အသံနက်)
            * **Orion** (အသံသွက်)
            * **Puck** (လူငယ်အသံ)
            **👉 ဒီ (၃) ခုထဲက တစ်ခုခုကို ရွေးပေးပါ။**
            """)
        with col_f:
            st.warning("""
            **👩 မိန်းမအသံ (Female) လိုချင်ပါက:**
            * **Nova** (တက်ကြွသည်)
            * **Shimmer** (တည်ငြိမ်သည်)
            * **Aoede** (အသံပါး)
            **👉 ဒီ (၃) ခုထဲက တစ်ခုခုကို ရွေးပေးပါ။**
            """)
        
        st.write("---")
        
        # --- Step-by-Step Guide ---
        st.markdown("### 📝 လုပ်ဆောင်ရမည့် အဆင့်ဆင့်:")
        st.markdown("""
        1. အောက်ပါ **"Go to Google AI Studio"** ခလုတ်ကို နှိပ်ပါ။
        2. ဘယ်ဘက်ထောင့်ရှိ **Create New > Speech** ကို နှိပ်ပါ။
        3. ညာဘက်ရှိ **Voice** နေရာတွင် အပေါ်ကပြောထားသော အသံတစ်ခုခု (ဥပမာ - **Charon** သို့မဟုတ် **Nova**) ကို ရွေးပါ။
        4. စာသားများကို Copy ကူးထည့်ပြီး **Generate** လုပ်ပါ။
        5. ပြီးလျှင် **Download** လုပ်ပြီး Tab 4 တွင် ပြန်သုံးပါ။
        """)
        
        st.link_button("🚀 Google AI Studio သို့ သွားရန် နှိပ်ပါ", "https://aistudio.google.com/")

# ==========================================
# TAB 4: MANUAL MERGE (FFMPEG - NO ERROR)
# ==========================================
with tab4:
    st.header("Tab 4: Video နှင့် အသံဖိုင် ပေါင်းစပ်ခြင်း")
    if st.session_state.user_info is None:
        show_login_ui("t4")
    else:
        st.success(f"✅ VIP အကောင့်ဖြင့် ဝင်ရောက်ထားပါသည်: {st.session_state.user_info}")
        if st.button("အကောင့်ထွက်မည် (Logout)", key="out_t4"):
            st.session_state.user_info = None
            st.rerun()
        st.write("---")

        col_v, col_a = st.columns(2)
        with col_v: video_input = st.file_uploader("၁။ Video ဖိုင် ရွေးချယ်ပါ", type=["mp4", "mov", "avi"], key="vid_merge")
        with col_a: audio_input = st.file_uploader("၂။ အသံဖိုင် ရွေးချယ်ပါ (MP3/WAV)", type=["mp3", "wav", "m4a"], key="aud_merge")
        
        st.write("⏱️ **အသံ အနှေး/အမြန် ချိန်ညှိရန် (Audio Speed):**")
        speed_option = st.select_slider(
            "Slide to adjust speed", 
            options=["0.5x (Slow)", "0.75x", "1.0x (Normal)", "1.25x (Fast)", "1.5x (Faster)", "2.0x"], 
            value="1.0x (Normal)"
        )

        keep_bg = st.checkbox("မူရင်း Video နောက်ခံအသံကို မဖျက်ဘဲထားမည်", value=True, key="bg_t4")

        # --- FFmpeg Speed Change Function (Error Free) ---
        def change_audio_speed_ffmpeg(input_file, output_file, speed_str):
            if "0.5x" in speed_str: rate = "0.5"
            elif "0.75x" in speed_str: rate = "0.75"
            elif "1.25x" in speed_str: rate = "1.25"
            elif "1.5x" in speed_str: rate = "1.5"
            elif "2.0x" in speed_str: rate = "2.0"
            else: return input_file 

            # FFmpeg Command
            cmd = [
                "ffmpeg", "-y",
                "-i", input_file,
                "-filter:a", f"atempo={rate}",
                "-vn", 
                output_file
            ]
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return output_file
            except Exception as e:
                print(f"FFmpeg Error: {e}")
                return input_file

        if video_input and audio_input and st.button("စတင်ပေါင်းစပ်မည် (Merge Now)", key="btn_merge"):
            with st.spinner("အသံချိန်ညှိပြီး ပေါင်းစပ်နေပါသည်..."):
                ext = audio_input.name.split(".")[-1]
                t_vid, t_aud, t_out = "temp_v.mp4", f"temp_a.{ext}", "out.mp4"
                processed_aud = "temp_processed_audio.mp3"

                with open(t_vid, "wb") as f: f.write(video_input.getbuffer())
                with open(t_aud, "wb") as f: f.write(audio_input.getbuffer())
                
                try:
                    # 1. Audio Speed Change (FFmpeg)
                    final_audio_path = t_aud
                    if "Normal" not in speed_option:
                        final_audio_path = change_audio_speed_ffmpeg(t_aud, processed_aud, speed_option)

                    vc = VideoFileClip(t_vid)
                    ac = AudioFileClip(final_audio_path)
                    
                    if ac.duration > vc.duration: ac = ac.subclip(0, vc.duration)
                    
                    final_audio = None
                    if keep_bg and vc.audio is not None:
                        bg_audio = vc.audio.volumex(0.1)
                        final_audio = CompositeAudioClip([bg_audio, ac])
                    else:
                        final_audio = ac
                    
                    final_video = vc.set_audio(final_audio)
                    final_video.write_videofile(t_out, fps=24, codec='libx264', preset='fast', audio_codec='aac', threads=4, ffmpeg_params=["-crf", "23"])
                    st.success(f"အောင်မြင်ပါသည်! (Speed: {speed_option})")
                    with open(t_out, "rb") as f: st.download_button("Video ဒေါင်းရန် (Download Video)", f.read(), "merged.mp4", "video/mp4")
                except Exception as e: st.error(f"Error: {e}")
                
                if os.path.exists(t_vid): os.remove(t_vid)
                if os.path.exists(t_aud): os.remove(t_aud)
                if os.path.exists(processed_aud): os.remove(processed_aud)
                if os.path.exists(t_out): os.remove(t_out)
                    
