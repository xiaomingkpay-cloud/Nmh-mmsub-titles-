import streamlit as st
import cv2
import numpy as np
import os
import subprocess
import re
import textwrap
import time
from PIL import Image, ImageDraw, ImageFont
from datetime import timedelta, datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# UI Configuration
st.set_page_config(page_title="NMH Pro Creator Tools", layout="wide")
st.title("✨ NMH Pro Creator Tools (Database Edition)")

# --- DATABASE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db_data():
    try:
        # Google Sheet ထဲက data အားလုံးကို ဖတ်ယူခြင်း
        return conn.read(ttl="0s")
    except:
        # Error တက်ခဲ့လျှင် column ခေါင်းစဉ်များဖြင့် အလွတ်တစ်ခု တည်ဆောက်ခြင်း
        return pd.DataFrame(columns=['Key', 'Daily_Count', 'Last_Time', 'Date'])

def update_db_data(user_key, new_count, new_time):
    df = get_db_data()
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    if user_key in df['Key'].values:
        # ရှိပြီးသား User ဆိုလျှင် update လုပ်ခြင်း
        df.loc[df['Key'] == user_key, ['Daily_Count', 'Last_Time', 'Date']] = [new_count, new_time, today_date]
    else:
        # User အသစ်ဆိုလျှင် row အသစ်ထည့်ခြင်း
        new_row = pd.DataFrame([{'Key': user_key, 'Daily_Count': new_count, 'Last_Time': new_time, 'Date': today_date}])
        df = pd.concat([df, new_row], ignore_index=True)
    
    # Google Sheet ထဲသို့ ပြန်လည်သိမ်းဆည်းခြင်း
    conn.update(data=df)

# --- VIP & LIMIT SYSTEM ---
all_vip_keys = st.secrets.get("vip_keys", {}).values()

with st.sidebar:
    st.header("🔑 Member Login")
    user_key_input = st.text_input("သီးသန့် VIP Key ကို ရိုက်ထည့်ပါ", type="password")
    
    # Database မှ အချက်အလက်ရယူခြင်း
    db_df = get_db_data()
    user_data = db_df[db_df['Key'] == user_key_input].iloc[0] if user_key_input in db_df['Key'].values else None
    
    # နေ့စွဲအလိုက် အကြိမ်ရေ Reset လုပ်ခြင်း (Date မတူလျှင် 0 မှ ပြန်စမည်)
    today_date = datetime.now().strftime("%Y-%m-%d")
    if user_data is not None and user_data['Date'] != today_date:
        user_daily_count = 0
    else:
        user_daily_count = int(user_data['Daily_Count']) if user_data is not None else 0
    
    user_last_time = float(user_data['Last_Time']) if user_data is not None else 0.0

    if user_key_input in all_vip_keys:
        st.session_state.user_type = "VIP"
        max_daily = 10
        st.success("🌟 VIP Member အဖြစ် ဝင်ရောက်ထားသည်။")
    else:
        st.session_state.user_type = "Free"
        max_daily = 2
        if user_key_input != "":
            st.error("❌ Key မှားယွင်းနေပါသည်။")
        else:
            st.info("🆓 Free User အဖြစ် အသုံးပြုနေသည်။")

    st.divider()
    st.subheader("📊 အသုံးပြုမှု အခြေအနေ (DB)")
    st.write(f"✅ ထုတ်ပြီးသောအရေအတွက်: **{user_daily_count} / {max_daily}**")
    
    # စောင့်ဆိုင်းချိန် တွက်ချက်ခြင်း
    wait_time = 1800 # 30 mins
    elapsed = time.time() - user_last_time
    if elapsed < wait_time and user_last_time != 0:
        rem_min = int((wait_time - elapsed) // 60)
        st.warning(f"🕒 နောက်ထပ်ထုတ်ရန်: **{rem_min} မိနစ်** စောင့်ပါ")

# --- PROCESSING LOGIC (SRT & Rendering) ---
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
    fps, w, h = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter("temp_render.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
    font = ImageFont.truetype("myanmar_font.ttf", int(h/18 if w > h else h/25))
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
    subprocess.call(['ffmpeg', '-y', '-i', 'temp_render.mp4', '-i', v_path, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-shortest', 'NMH_Final.mp4'])
    return 'NMH_Final.mp4'

# --- TABS UI ---
tab1, tab2 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (FREE/VIP)"])

# --- Tab 1: SRT Helper (အညွှန်းစုံလင်စွာဖြင့်) ---
with tab1:
    st.header("🌐 Gemini မှတစ်ဆင့် SRT ထုတ်ယူခြင်း")
    st.subheader("အဆင့် (၁) - စာသားကို Copy ယူပါ")
    prompt_text = "ဒီဗီဒီယိုအတွက် မြန်မာ SRT ထုတ်ပေးပါ"
    col1, col2 = st.columns([3, 1])
    with col1: st.code(prompt_text, language=None)
    with col2: st.write("နှိပ်ပြီး Copy ယူပါ ☝️")

    st.divider()
    st.subheader("အဆင့် (၂) - Gemini သို့သွား၍ SRT ထုတ်ယူပါ")
    st.write("အောက်ကခလုတ်ကိုနှိပ်ပြီး Gemini မှာ SRT Copy သွားယူပါ 👇")
    st.link_button("🤖 Gemini သို့သွားရန်", "https://gemini.google.com/")

    st.divider()
    st.subheader("အဆင့် (၃) - ရလာသော SRT ကို သိမ်းဆည်းပါ")
    srt_input = st.text_area("Gemini မှရလာသော SRT စာသားများကို ဒီမှာ Paste လုပ်ပါ", height=150)
    if srt_input:
        st.download_button("📥 SRT ဖိုင်အဖြစ် သိမ်းဆည်းရန်", srt_input, file_name="subtitle.srt")

# --- Tab 2: စာတန်းမြှုပ်ခြင်း (Database Limit စနစ်ဖြင့်) ---
with tab2:
    st.header("📝 မြန်မာစာတန်းထိုး Video ထုတ်ယူခြင်း")
    v_up, s_up = st.file_uploader("Video တင်ပါ", type=["mp4"]), st.file_uploader("SRT တင်ပါ", type=["srt"])
    pos = st.selectbox("စာတန်းနေရာ (%)", [10, 20, 30], index=1)
    
    if v_up and s_up and user_key_input != "":
        if user_daily_count >= max_daily:
            st.error(f"❌ သင်၏ တစ်နေ့တာ ဗီဒီယိုထုတ်ယူခွင့် ({max_daily} ကြိမ်) ပြည့်သွားပါပြီ။")
        elif elapsed < 1800 and user_last_time != 0:
            st.error(f"⏳ နာရီဝက်ခြားမှ တစ်ကြိမ် ထုတ်နိုင်ပါသည်။ နောက်ထပ် {int((1800-elapsed)//60)} မိနစ် စောင့်ပါ။")
        else:
            if st.button("🚀 Render Final Video"):
                with open("in.mp4", "wb") as f: f.write(v_up.read())
                res = process_srt_video("in.mp4", s_up.read().decode('utf-8', errors='ignore'), pos)
                
                # Database (Google Sheet) တွင် အချက်အလက်သွားသိမ်းခြင်း
                update_db_data(user_key_input, user_daily_count + 1, time.time())
                
                st.success("✅ အောင်မြင်စွာ ထုတ်ယူပြီးပါပြီ!")
                st.video(res)
                st.download_button("📥 Video ဒေါင်းရန်", open(res, "rb"), file_name="NMH_Subtitled.mp4")
                
