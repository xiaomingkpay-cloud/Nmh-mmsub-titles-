import streamlit as st

# Page configuration
st.set_page_config(page_title="NMH Pro Creator Tools", layout="wide")

# Header Section
st.title("✨ NMH Pro Creator Tools")
st.markdown("### 👨‍💻 Developed by Naing Min Htet")

# Tab ၄ ခု သတ်မှတ်ခြင်း
tab1, tab2, tab3, tab4 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (FREE/VIP)", "🗣️ အသံထုတ်ရန် (VIP)", "🎬 Video ပေါင်းရန် (VIP)"])

# --- Tab 1: SRT Helper ---
with tab1:
    st.header("🌐 Gemini မှတစ်ဆင့် SRT ထုတ်ယူခြင်း")
    
    # ခလုတ်များ
    col1, col2 = st.columns(2)
    with col1:
        # Gemini သို့ တိုက်ရိုက်သွားရန် link
        st.link_button("🤖 Gemini သို့သွားရန်", "https://gemini.google.com/")
    with col2:
        # Prompt ကို copy ကူးရလွယ်အောင် ပြပေးထားခြင်း
        st.code("ဒီဗီဒီယိုအတွက် မြန်မာ SRT ထုတ်ပေးပါ", language=None)
        st.caption("အပေါ်ကစာသားကို Copy ကူးပြီး Gemini မှာ ခိုင်းပေးပါ။")

    st.divider()

    # လမ်းညွှန်ချက်
    with st.expander("📖 လုပ်နည်းအဆင့်ဆင့်ကို ကြည့်ရန်"):
        st.write("""
        1. **Gemini သို့သွားရန်** ခလုတ်ကို နှိပ်ပါ။
        2. Gemini ရောက်လျှင် သင့်ဗီဒီယိုထဲက ပြောစကားများကို ပေးပြီး **'မြန်မာ SRT ထုတ်ပေးပါ'** ဟု ခိုင်းပါ။
        3. Gemini က SRT code များ ထုတ်ပေးလျှင် ထိုစာသားများကို အကုန် **Copy** ကူးခဲ့ပါ။
        4. အောက်ကအကွက်ထဲတွင် **Paste** လုပ်ပြီး ဖိုင်အဖြစ် ပြောင်းလဲပါ။
        """)

    st.divider()

    # SRT Text to File Converter
    st.subheader("📝 SRT စာသားကို ဖိုင်အဖြစ် ပြောင်းလဲရန်")
    srt_content = st.text_area("Gemini မှရလာသော SRT စာသားများကို ဒီမှာ Paste လုပ်ပါ", height=250, placeholder="1\n00:00:01,000 --> 00:00:04,000\nမင်္ဂလာပါခင်ဗျာ...")

    if srt_content:
        # ဖိုင်အမည် သတ်မှတ်ခြင်း
        file_name = st.text_input("ဖိုင်အမည် သတ်မှတ်ပါ (ဥပမာ- subtitle)", "mysubtitle")
        full_file_name = f"{file_name}.srt"
        
        # Download ခလုတ်
        st.download_button(
            label="📥 SRT ဖိုင်အဖြစ် ဒေါင်းလုဒ်ဆွဲရန်",
            data=srt_content,
            file_name=full_file_name,
            mime="text/plain"
        )
        st.success(f"စာသားများကို {full_file_name} အဖြစ် ပြောင်းလဲပေးထားပါသည်။")

# အခြား Tab များ (နမူနာ)
with tab2: st.info("Tab 2: စာတန်းမြှုပ်ခြင်း လုပ်ဆောင်ချက်ကို နောက်တစ်ဆင့်တွင် ရေးပါမည်။")
with tab3: st.info("Tab 3: အသံထုတ်ခြင်း (Coming Soon)")
with tab4: st.info("Tab 4: Video ပေါင်းခြင်း (Coming Soon)")
    
