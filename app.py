import streamlit as st
import cv2
import numpy as np
import os
import subprocess
import re
import textwrap
import time
from PIL import Image, ImageDraw, ImageFont
from datetime import timedelta

# UI Configuration
st.set_page_config(page_title="NMH မြန်မာစာတန်းထိုး Pro", layout="wide")

# --- LOGIN GATE ---
all_vip_keys = st.secrets.get("vip_keys", {}).values()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'last_render' not in st.session_state:
    st.session_state.last_render = 0

if not st.session_state.authenticated:
    st.title("🔐 NMH မြန်မာစာတန်းထိုး Pro - Login")
    user_key = st.text_input("ဝင်ရောက်ရန် VIP Key ရိုက်ထည့်ပါ", type="password")
    
    if st.button("Login"):
        if user_key in all_vip_keys:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Key မှားယွင်းနေပါသည်။")
    
    st.divider()
    st.subheader("📞 Creator သို့ ဆက်သွယ်ရန်")
    st.write("Facebook: [NMH Creator](https://www.facebook.com/share/1BUUZ4pQ3N/)")
    st.stop()

# --- HELPER FUNCTIONS ---
def get_video_duration(file_path):
    cap = cv2.VideoCapture(file_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0
    cap.release()
    return duration

def compress_video_pro(input_path, output_path):
    # CRF 22: Quality အကောင်းဆုံးထိန်းပြီး MB ကျုံ့သည့်စနစ်
    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-c:v', 'libx264', '-crf', '22',
        '-preset', 'slow', 
        '-c:a', 'aac', '-b:a', '128k',
        output_path
    ]
    subprocess.call(cmd)
    return output_path

def parse_time(time_str):
    time_str = time_str.replace(',', '.')
    parts = time_str.split(':')
    return timedelta(hours=int(parts[0]), minutes=int(parts[1]), seconds=float(parts[2]))

def parse_srt(srt_string):
    subs = []
    blocks = re.split(r'\n\s*\n', srt_string.strip())
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            try:
                times = lines[1].split(' --> ')
                subs.append({'start': parse_time(times[0].strip()), 'end': parse_time(times[1].strip()), 'text': " ".join(lines[2:])})
            except: continue
    return subs

def process_srt_video(v_path, srt_text, pos_pct):
    subtitles = parse_srt(srt_text)
    cap = cv2.VideoCapture(v_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    out = cv2.VideoWriter("temp_render.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
    font_size = int(h / 18 if w > h else h / 25)
    font = ImageFont.truetype("myanmar_font.ttf", font_size)
    total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    prog = st.progress(0)
    
    for i in range(total_f):
        ret, frame = cap.read()
        if not ret: break
        cur_sec = i / fps
        active_txt = next((s['text'] for s in subtitles if s['start'].total_seconds() <= cur_sec <= s['end'].total_seconds()), "")
        if active_txt:
            wrap_limit = 60 if w > h else 30
            wrapped = "\n".join(textwrap.wrap(active_txt, width=wrap_limit))
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img)
            bbox = draw.multiline_textbbox((0, 0), wrapped, font=font)
            tx, ty = (w-(bbox[2]-bbox[0]))//2, h-int(h*(pos_pct/100))-(bbox[3]-bbox[1])
            overlay = Image.new('RGBA', img.size, (0,0,0,0))
            ImageDraw.Draw(overlay).rectangle([tx-15, ty-15, tx+(bbox[2]-bbox[0])+15, ty+(bbox[3]-bbox[1])+15], fill=(0,0,0,160))
            img = Image.alpha_composite(img.convert('RGBA'), overlay)
            ImageDraw.Draw(img).multiline_text((tx, ty), wrapped, font=font, fill=(255,255,255), align="center")
            frame = cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2BGR)
        out.write(frame)
        if i % 25 == 0: prog.progress((i+1)/total_f)
    cap.release(); out.release()
    
    subprocess.call(['ffmpeg', '-y', '-i', 'temp_render.mp4', '-i', v_path, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '22', '-pix_fmt', 'yuv420p', '-shortest', 'NMH_Final.mp4'])
    return 'NMH_Final.mp4'

# --- MAIN UI ---
st.title("✨ NMH မြန်မာစာတန်းထိုး Pro")

tab1, tab2, tab3 = st.tabs(["📉 Step 1: Video Compress", "🌐 Step 2: SRT Helper", "📝 Step 3: Subtitle Render"])

# --- Step 1: Video Compressor ---
with tab1:
    st.header("📉 Video File Size လျှော့ချခြင်း")
    st.info("၂ မိနစ်အောက် နှင့် 200MB အောက် ဗီဒီယိုများကိုသာ လက်ခံပါသည်")
    raw_v = st.file_uploader("ဗီဒီယိုတင်ပါ", type=["mp4", "mov"], key="comp")
    
    if raw_v:
        file_size_mb = raw_v.size / (1024 * 1024)
        if file_size_mb > 200:
            st.error(f"❌ ဖိုင်ဆိုဒ် {file_size_mb:.1f}MB ဖြစ်နေပါသည်။ 200MB ထက်မကျော်ရပါ။")
        else:
            if st.button("🚀 Start Smart Compress"):
                with st.spinner("အကြည်ဓာတ်ထိန်းသိမ်းပြီး ဆိုဒ်ကျုံ့နေပါသည်..."):
                    with open("temp_raw.mp4", "wb") as f: f.write(raw_v.read())
                    duration = get_video_duration("temp_raw.mp4")
                    
                    if duration > 120:
                        st.error(f"❌ ဗီဒီယိုက {int(duration)} စက္ကန့် ဖြစ်နေပါသည်။ ၂ မိနစ်ထက် မကျော်ရပါ။")
                    else:
                        res_v = compress_video_pro("temp_raw.mp4", "compressed.mp4")
                        st.success(f"✅ ကျုံ့ပြီးပါပြီ! ({os.path.getsize(res_v)//1024//1024} MB)")
                        st.video(res_v)
                        st.download_button("📥 Download Compressed Video", open(res_v, "rb"), file_name="NMH_Compressed.mp4")

# --- Step 2: SRT Helper ---
with tab2:
    st.header("🌐 Gemini SRT Helper")
    st.code("ဒီဗီဒီယိုအတွက် မြန်မာ SRT ထုတ်ပေးပါ", language=None)
    st.link_button("🤖 Gemini သို့သွားရန်", "https://gemini.google.com/")
    srt_in = st.text_area("SRT Paste လုပ်ပါ")
    if srt_in: st.download_button("📥 Save SRT", srt_in, file_name="sub.srt")

# --- Step 3: Render Subtitle ---
with tab3:
    st.header("📝 မြန်မာစာတန်းထိုးခြင်း")
    elapsed = time.time() - st.session_state.last_render
    if elapsed < 900 and st.session_state.last_render != 0:
        st.warning(f"⏳ ဗီဒီယိုတစ်ခုထုတ်ပြီးတိုင်း ၁၅ မိနစ် စောင့်ရပါမည်။ ကျန်ချိန်: {int((900-elapsed)//60)} မိနစ်")
    else:
        v_in = st.file_uploader("ဗီဒီယိုတင်ပါ (Compressed ဖိုင်ကိုသုံးပါ)", type=["mp4"], key="render_v")
        s_in = st.file_uploader("SRT ဖိုင်တင်ပါ", type=["srt"], key="render_s")
        pos = st.selectbox("စာတန်းနေရာ (%)", [10, 20, 30], index=1)
        if v_in and s_in and st.button("🚀 Start Rendering"):
            with st.spinner("စာတန်းမြှုပ်နေပါသည်..."):
                with open("render_in.mp4", "wb") as f: f.write(v_in.read())
                final = process_srt_video("render_in.mp4", s_in.read().decode('utf-8', errors='ignore'), pos)
                st.session_state.last_render = time.time()
                st.video(final)
                st.download_button("📥 Download Final Video", open(final, "rb"), file_name="NMH_Final.mp4")
                
