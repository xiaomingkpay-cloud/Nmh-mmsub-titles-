import streamlit as st
import os
import pysubs2
import textwrap
import numpy as np
from datetime import datetime
from streamlit.web.server.websocket_headers import _get_websocket_headers
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
import nest_asyncio
import subprocess

nest_asyncio.apply()

# Website Config
st.set_page_config(page_title="NMH Pro Creator Tools", layout="wide")

# ==========================================
# 🛡️ SECURITY & TRACKER
# ==========================================
@st.cache_resource
def get_usage_data():
    return {"date": datetime.now().strftime("%Y-%m-%d"), "users": {}, "bindings": {}}

usage_data = get_usage_data()

def get_remote_ip():
    try:
        headers = _get_websocket_headers()
        ip = headers.get("X-Forwarded-For")
        if ip: return ip.split(",")[0]
    except: pass
    return "unknown_user"

def check_code_validity(user_value):
    if "|" in user_value:
        try:
            name_part, date_part = user_value.split("|")
            expiry_date = datetime.strptime(date_part.strip(), "%Y-%m-%d").date()
            if datetime.now().date() > expiry_date: 
                return False, name_part.strip(), f"⛔ သက်တမ်းကုန်သွားပါပြီ ({date_part.strip()})"
            return True, name_part.strip(), None
        except: return True, user_value, None
    return True, user_value, None

# Auto Login Check
if "user_info" not in st.session_state:
    st.session_state.user_info = None
    current_ip = get_remote_ip()
    for code, bound_ip in usage_data["bindings"].items():
        if bound_ip == current_ip and code in st.secrets.get("users", {}):
            ok, name, err = check_code_validity(st.secrets["users"][code])
            if ok: st.session_state.user_info = name

# ==========================================
# 🏠 MAIN TABS
# ==========================================
st.title("✨ NMH Pro Creator Tools")

tab1, tab2, tab3, tab4 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (Free)", "🗣️ အသံထုတ်ရန် (VIP)", "🎬 Video ပေါင်းရန် (VIP)"])

# --- TAB 1: SRT ---
with tab1:
    st.header("Gemini SRT Generator")
    st.link_button("🚀 Google Gemini သို့သွားရန်", "https://gemini.google.com/")
    srt_ta = st.text_area("Gemini မှ စာသားများကို ဒီမှာထည့်ပါ:", height=200, key="t1_ta")
    if srt_ta and st.button("SRT အဖြစ် ပြောင်းမည်", key="t1_btn"):
        clean = srt_ta.replace("```srt", "").replace("```", "").strip()
        st.success("အောင်မြင်ပါသည်!")
        st.download_button("Download SRT", clean, "myanmar.srt")

# --- TAB 2: SUBTITLE BURNER ---
with tab2:
    st.header("Tab 2: စာတန်းမြှုပ်ခြင်း (Free)")
    user_ip = get_remote_ip()
    if user_ip not in usage_data["users"]: usage_data["users"][user_ip] = 0
    left = 3 - usage_data["users"][user_ip]
    if left > 0: st.info(f"✅ လက်ကျန်: {left}/3 ပုဒ်")
    else: st.error("⛔ Limit Reached")

    v_file = st.file_uploader("Video တင်ပါ", type=["mp4", "mov"], key="t2_v")
    s_file = st.file_uploader("SRT တင်ပါ", type=["srt"], key="t2_s")

    def make_subs(s_path, v_w, v_h, f_path):
        subs = pysubs2.load(s_path, encoding="utf-8")
        clips = []
        is_vert = v_h > v_w
        wrap, pos, f_div = (35, 0.70, 18) if is_vert else (50, 0.75, 22)
        font = ImageFont.truetype(f_path, int(v_w / f_div))
        for line in subs:
            if not line.text.strip(): continue
            txt = textwrap.fill(line.text.replace("\\N", " "), width=wrap)
            img = Image.new('RGBA', (int(v_w*0.95), int(v_h*0.45)), (0,0,0,0))
            ImageDraw.Draw(img).text((img.width/2, img.height/2), txt, font=font, fill="white", stroke_width=3, stroke_fill="black", anchor="mm", align="center")
            c = ImageClip(np.array(img)).set_start(line.start/1000).set_duration((line.end-line.start)/1000).set_position(('center', pos), relative=True)
            clips.append(c)
        return clips

    if left > 0 and v_file and s_file and st.button("စာတန်းမြှုပ်မည်", key="t2_btn"):
        with st.spinner("Processing..."):
            with open("temp_v.mp4", "wb") as f: f.write(v_file.getbuffer())
            with open("temp_s.srt", "wb") as f: f.write(s_file.getbuffer())
            try:
                vid = VideoFileClip("temp_v.mp4")
                final = CompositeVideoClip([vid] + make_subs("temp_s.srt", vid.w, vid.h, "myanmar_font.ttf"))
                final.write_videofile("out.mp4", fps=24, codec='libx264', audio_codec='aac')
                usage_data["users"][user_ip] += 1
                st.success("အောင်မြင်ပါသည်!")
                with open("out.mp4", "rb") as f: st.download_button("Download Video", f.read(), "subbed.mp4")
            except Exception as e: st.error(str(e))
            for f in ["temp_v.mp4", "temp_s.srt", "out.mp4"]: 
                if os.path.exists(f): os.remove(f)

# --- VIP LOGIN HELPER ---
def login_ui(key):
    st.warning("🔒 VIP ကုဒ် လိုအပ်ပါသည်။")
    tk = st.text_input("Enter Token:", type="password", key=f"tk_{key}")
    if st.button("Login", key=f"ln_{key}"):
        if tk in st.secrets.get("users", {}):
            ok, name, err = check_code_validity(st.secrets["users"][tk])
            if ok:
                usage_data["bindings"][tk] = get_remote_ip()
                st.session_state.user_info = name
                st.rerun()
            else: st.error(err)
        else: st.error("Code မှားယွင်းနေပါသည်။")

# --- TAB 3: AUDIO GUIDE ---
with tab3:
    st.header("Tab 3: အသံထုတ်လုပ်နည်း")
    if not st.session_state.user_info: login_ui("t3")
    else:
        st.success(f"✅ VIP အကောင့်: {st.session_state.user_info}")
        col1, col2 = st.columns(2)
        with col1: st.info("**👨 ကျားအသံ (Male):**\n* Charon, Orion, Puck")
        with col2: st.warning("**👩 မအသံ (Female):**\n* Nova, Shimmer, Aoede")
        st.write("---")
        st.markdown("### 📝 အသံထုတ်ရန် လမ်းညွှန်:")
        st.markdown("1. Go to Google AI Studio.\n2. နှိပ်ပါ: 'Turn text into audio with Gemini'.\n3. ရွေးပါ: **'Single speaker'**.\n4. အသံရွေး၊ စာထည့်ပြီး Generate လုပ်ပါ။")
        st.link_button("🚀 Go to Google AI Studio", "https://aistudio.google.com/")

# --- TAB 4: VIDEO & AUDIO MERGE (AUDIO FIX) ---
with tab4:
    st.header("Tab 4: Video နှင့် အသံဖိုင် ပေါင်းစပ်ခြင်း")
    if not st.session_state.user_info: login_ui("t4")
    else:
        st.success(f"✅ VIP အကောင့်: {st.session_state.user_info}")
        if st.button("Logout"): st.session_state.user_info = None; st.rerun()
        
        # 🔥 FIX: အသံဖိုင်ရွေးတဲ့အခါ wav, m4a တွေကိုပါ လွတ်လွတ်လပ်လပ် ရွေးလို့ရအောင် type=None လုပ်ပေးထားပါတယ်
        v_in = st.file_uploader("Video ရွေးပါ", type=["mp4", "mov"], key="t4_v")
        a_in = st.file_uploader("Audio ရွေးပါ", type=None, key="t4_a", help="MP3, WAV, M4A ဖိုင်အားလုံးကို ရွေးနိုင်ပါသည်")
        
        spd = st.select_slider("အသံ အနှေး/အမြန်:", options=["0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"], value="1.0x")
        bg = st.checkbox("မူရင်း Background အသံထားမည်", value=True)
        
        if v_in and a_in and st.button("Merge Now"):
            with st.spinner("ပေါင်းစပ်နေပါသည်..."):
                a_ext = a_in.name.split(".")[-1]
                t_v, t_a, t_o = "t_v.mp4", f"t_a.{a_ext}", "fin.mp4"
                
                with open(t_v, "wb") as f: f.write(v_in.getbuffer())
                with open(t_a, "wb") as f: f.write(a_in.getbuffer())
                
                try:
                    final_a_path = t_a
                    if spd != "1.0x":
                        rate = spd.replace('x','')
                        subprocess.run(["ffmpeg", "-y", "-i", t_a, "-filter:a", f"atempo={rate}", "-vn", "t_ap.mp3"])
                        final_a_path = "t_ap.mp3"
                    
                    vc = VideoFileClip(t_v)
                    ac = AudioFileClip(final_a_path)
                    
                    if ac.duration > vc.duration: ac = ac.subclip(0, vc.duration)
                    af = CompositeAudioClip([vc.audio.volumex(0.1), ac]) if bg and vc.audio else ac
                    
                    vc.set_audio(af).write_videofile(t_o, fps=24, codec='libx264', audio_codec='aac')
                    st.success("Done!")
                    with open(t_o, "rb") as f: st.download_button("Download Video", f.read(), "merged.mp4")
                except Exception as e: st.error(str(e))
                for f in [t_v, t_a, t_o, "t_ap.mp3"]:
                    if os.path.exists(f): os.remove(f)
                        
