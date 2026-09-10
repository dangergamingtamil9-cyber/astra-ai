import io
import json
import requests
import streamlit as st

# Page Configuration
st.set_page_config(page_title="Astra AI", page_icon="⚡", layout="centered")

# 🔑 இங்க உங்களோட OpenRouter API Key-ஐ பேஸ்ட் பண்ணுங்க:
OPENROUTER_API_KEY = "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"

# -------------------- PREMIUM BLACK & WHITE CSS --------------------
st.markdown("""
    <style>
    .stApp { background-color: #0a0a0a; color: #ffffff; }
    .glass-card { background: rgba(20, 20, 20, 0.8); border: 1px solid #262626; border-radius: 12px; padding: 24px; margin-top: 10px; }
    .user-row { display: flex; justify-content: flex-end; margin-bottom: 10px; }
    .user-bubble { background-color: #ffffff; color: #000000; padding: 10px 16px; border-radius: 16px 16px 2px 16px; max-width: 80%; font-size: 14px; font-weight: 500; word-wrap: break-word; }
    .ai-row { display: flex; justify-content: flex-start; margin-bottom: 10px; }
    .ai-bubble { background-color: #161616; color: #ededed; padding: 10px 16px; border-radius: 16px 16px 16px 2px; max-width: 85%; border-left: 3px solid #ffffff; font-size: 14px; word-wrap: break-word; }
    section[data-testid="stSidebar"] { background-color: #111111 !important; border-right: 1px solid #222222; width: 250px !important; }
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stFileUploader"]) { background-color: #141414 !important; border: 1px solid #333333 !important; border-radius: 20px !important; padding: 2px 8px !important; align-items: center !important; }
    div[data-testid="stFileUploader"] section { padding: 0px !important; min-height: 0px !important; border: none !important; background: transparent !important; }
    div[data-testid="stFileUploader"] { margin: 0px !important; padding: 0px !important; }
    div[data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }
    div[data-testid="stChatInput"] { border: none !important; background: transparent !important; padding: 0px !important; }
    div[data-testid="stChatInput"] > div { background: transparent !important; border: none !important; box-shadow: none !important; }
    div[data-testid="stAudioInput"] { background: transparent !important; border: none !important; padding: 0px !important; }
    .stSpinner > div { border-top-color: #ffffff !important; }
    .stButton>button { border-radius: 8px; border: 1px solid #333; background-color: #141414; color: #fff; font-size: 13px; padding: 4px 10px; }
    .stButton>button:hover { background-color: #ffffff; color: #000000; border: 1px solid #ffffff; }
    </style>
""", unsafe_allow_html=True)

# -------------------- AUDIO TRANSCRIPTION FUNCTION --------------------
def convert_audio_to_text(audio_bytes):
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            r.adjust_for_ambient_noise(source, duration=0.3)
            audio_data = r.record(source)
            
        try:
            text = r.recognize_google(audio_data, language="ta-IN")
            if text: return text.strip()
        except Exception: pass
            
        try:
            text = r.recognize_google(audio_data, language="en-IN")
            if text: return text.strip()
        except Exception: pass
    except Exception: pass
    return None

# -------------------- SESSION STATE INIT --------------------
if "users" not in st.session_state: st.session_state.users = {}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "messages" not in st.session_state: st.session_state.messages = []

# -------------------- LOGIN PAGE --------------------
if not st.session_state.logged_in:
    st.markdown("<h2 style='color: #ffffff; text-align: center;'>⚡ Astra AI</h2>", unsafe_allow_html=True)
    st.caption("<center style='color: #777;'>Created & Owned by MGS TAMIZHAN</center>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email_in = st.text_input("Email", key="login_email", placeholder="Enter email")
        pass_in = st.text_input("Password", type="password", key="login_pass", placeholder="Enter password")
        st.write("")
        if st.button("Login", use_container_width=True):
            if email_in in st.session_state.users and st.session_state.users[email_in] == pass_in:
                st.session_state.logged_in = True
                st.session_state.user_email = email_in
                st.rerun()
            else:
                st.error("Invalid credentials.")

        st.markdown("<center style='margin: 6px 0; color:#555;'>or</center>", unsafe_allow_html=True)

        if st.button("🌐 Sign in with Google", use_container_width=True):
            if email_in.strip() != "" and "@" in email_in:
                st.session_state.logged_in = True
                st.session_state.user_email = email_in.strip()
                st.rerun()
            else:
                st.info("Enter email above first.")

        if st.button("👤 Continue as Guest", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_email = "Guest User"
            st.rerun()

    with tab2:
        new_email = st.text_input("Email", key="signup_email", placeholder="Enter email")
        new_pass = st.text_input("Password", type="password", key="signup_pass", placeholder="Create password")
        st.write("")
        if st.button("Sign Up", use_container_width=True):
            if new_email and new_pass:
                st.session_state.users[new_email] = new_pass
                st.success("Account created! Please login.")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -------------------- LEFT SIDEBAR (ACCOUNT & LOGOUT) --------------------
with st.sidebar:
    st.markdown("### 👤 Account Details")
    st.markdown("<p style='color: #aaa; font-size: 12px; margin-bottom: 2px;'>Logged in as:</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #fff; font-size: 13px; font-weight: bold; word-break: break-all;'>{st.session_state.user_email}</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: #555; font-size: 11px;'>Owned by MGS TAMIZHAN</p>", unsafe_allow_html=True)
    st.write("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.messages = []
        st.rerun()

# -------------------- SYSTEM PROMPT --------------------
system_prompt = (
    "You are Astra AI, an intelligent assistant created and solely owned by MGS TAMIZHAN.\n"
    "Rules:\n"
    "1. Understand the user's query carefully and give direct, helpful answers.\n"
    "2. If the user writes in Tanglish, reply in clean, natural Tanglish.\n"
    "3. Never output random gibberish, broken translations, or repetitive loops.\n"
    "4. If asked about your creator, state you were created by MGS TAMIZHAN."
)

# -------------------- MAIN CHAT DISPLAY --------------------
st.markdown("<h2 style='color: #ffffff; text-align: center; margin-top: -10px; margin-bottom: 15px;'>⚡ Astra AI</h2>", unsafe_allow_html=True)

chat_box = st.container()

with chat_box:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-row"><div class="user-bubble">{msg["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-row"><div class="ai-bubble">{msg["content"]}</div></div>', unsafe_allow_html=True)

st.write("")

# -------------------- INPUT BAR --------------------
col_left, col_mid, col_right = st.columns([1, 8, 1], vertical_alignment="center")

with col_left:
    uploaded_image = st.file_uploader("➕", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="img_up")

with col_mid:
    user_text = st.chat_input("Message Astra AI...")

with col_right:
    audio_record = st.audio_input("🎙️", label_visibility="collapsed", key="voice_up")

# -------------------- RESPONSE & LOADING LOGIC --------------------
if user_text or uploaded_image or audio_record:
    prompt = ""

    if user_text:
        prompt = user_text
    elif audio_record:
        transcribed = convert_audio_to_text(audio_record.read())
        if transcribed:
            prompt = transcribed
        else:
            st.warning("🎤 Voice புரியவில்லை, மீண்டும் பேசுங்கள்.")
            st.stop()
    elif uploaded_image:
        prompt = "📷 Image uploaded"

    st.session_state.messages.append({"role": "user", "content": prompt})

    with chat_box:
        st.markdown(f'<div class="user-row"><div class="user-bubble">{prompt}</div></div>', unsafe_allow_html=True)

        bot_reply = None
        last_error = ""

        with st.spinner("⚡ Astra AI is thinking..."):
            clean_key = OPENROUTER_API_KEY.strip()
            
            headers = {
                "Authorization": f"Bearer {clean_key}",
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "Astra AI",
                "Content-Type": "application/json"
            }

            fast_models = [
                "meta-llama/llama-3.1-8b-instruct",
                "google/gemma-2-9b-it",
                "mistralai/mistral-7b-instruct"
            ]

            for model in fast_models:
                try:
                    response = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        data=json.dumps({
                            "model": model,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.1,
                            "repetition_penalty": 1.2,
                            "max_tokens": 1000
                        }),
                        timeout=15
                    )
                    res_data = response.json()

                    if "choices" in res_data and len(res_data["choices"]) > 0:
                        bot_reply = res_data["choices"][0]["message"]["content"]
                        break
                    else:
                        if "error" in res_data:
                            last_error = res_data["error"].get("message", str(res_data["error"]))
                except Exception as e:
                    last_error = str(e)
                    continue

        if bot_reply:
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.markdown(f'<div class="ai-row"><div class="ai-bubble">{bot_reply}</div></div>', unsafe_allow_html=True)
            st.rerun()
        else:
            st.error(f"⚠️ Connection Error: {last_error if last_error else 'OpenRouter API Key செல்லாது.'}")
