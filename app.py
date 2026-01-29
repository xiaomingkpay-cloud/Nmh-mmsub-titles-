import streamlit as st

# Page configuration
st.set_page_config(page_title="NMH Pro Creator Tools", layout="wide")

# Header Section
st.title("✨ NMH Pro Creator Tools")
st.markdown("### 👨‍💻 Developed by Naing Min Htet")

# Tab ၄ ခု
tab1, tab2, tab3, tab4 = st.tabs(["🌐 SRT ထုတ်ရန်", "📝 စာတန်းမြှုပ် (FREE/VIP)", "🗣️ အသံထုတ်ရန် (VIP)", "🎬 Video ပေါင်းရန် (VIP)"])

# --- Tab 1: SRT Helper ---
with tab1:
    st.header("🌐 Gemini မှတစ်ဆင့် SRT ထုတ်ယူခြင်း")
    
    # Prompt Section
    st.info("ဒီဗီဒီယိုအတွက် မြန်မာ SRT ထုတ်ပေးပါ")
    st.caption("အပေါ်ကစာသားကို Copy ကူးပြီး Gemini မှာ ခိုင်းပေးပါ။")
    
    # Gemini Button (စာသားအောက်သို့ ရွှေ့ထားသည်)
    st.link_button("🤖 Gemini သို့သွားရန်", "https://gemini.google.com/")

    st.divider()

    # လမ်းညွှန်ချက် (အမြဲပွင့်နေစေရန် expander မသုံးတော့ပါ)
    st.subheader("📖 လုပ်နည်းအဆင့်ဆင့်")
    st.write("၁။ Gemini ရောက်လျှင် သင့်ဗီဒီယိုထဲက ပြောစကားများကို ပေးပြီး 'မြန်မာ SRT ထုတ်ပေးပါ' ဟု ခိုင်းပါ။")
    st.write("၂။ Gemini က SRT code များ ထုတ်ပေးလျှင် ထိုစာသားများကို အကုန် Copy ကူးခဲ့ပါ။")
    st.write("၃။ အောက်ကအကွက်ထဲတွင် Paste လုပ်ပြီး ဖိုင်အဖြစ် ဒေါင်းလုဒ်ဆွဲပါ။")

    st.divider()

    # SRT Text Area
    st.subheader("📝 SRT စာသားကို ဖိုင်အဖြစ် ပြောင်းလဲရန်")
    srt_content = st.text_area("Gemini မှရလာသော SRT စာသားများကို ဒီမှာ Paste လုပ်ပါ", height=300)

    if srt_content:
        # File Name ကို အသေထားပြီး Download ခလုတ်ပြခြင်း
        st.download_button(
            label="📥 SRT ဖိုင်အဖြစ် ဒေါင်းလုဒ်ဆွဲရန်",
            data=srt_content,
            file_name="subtitle.srt",
            mime="text/plain"
        )
        st.success("စာသားများကို subtitle.srt အဖြစ် ပြောင်းလဲရန် အဆင်သင့်ဖြစ်ပါပြီ။")

# အခြား Tab များ
with tab2: st.info("Tab 2: စာတန်းမြှုပ်ခြင်း လုပ်ဆောင်ချက်ကို နောက်တစ်ဆင့်တွင် ရေးပါမည်။")
with tab3: st.info("Tab 3: အသံထုတ်ခြင်း (Coming Soon)")
with tab4: st.info("Tab 4: Video ပေါင်းခြင်း (Coming Soon)")
    
