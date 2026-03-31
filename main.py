import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# --- 1. 設定 ---
st.set_page_config(page_title="M25", page_icon="💬", layout="wide")

# --- 2. デザイン (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #313338; color: #dbdee1; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="bundle-viewer-container"] {display: none !important;}

    /* 余白を 150px → 80px へ。これで「広すぎず、隠れず」のラインを狙います */
    .block-container { 
        padding-top: 1rem; 
        padding-bottom: 80px !important; 
        max-width: 100% !important; 
    }

    .chat-row { display: flex; flex-direction: column; margin-bottom: 16px; width: 100%; }
    .chat-header { display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; font-size: 0.85rem; }
    .message-text { font-size: 1.05rem; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; max-width: 85%; }
    .align-right { align-items: flex-end; text-align: right; }
    .align-left { align-items: flex-start; text-align: left; }
    .name-maki { color: #ffa657 !important; font-weight: bold; }
    .name-hide { color: #58a6ff !important; font-weight: bold; }
    .timestamp { color: #949ba4; font-size: 0.75rem; }
    .text-content { color: #e6edf3; }
    
    /* 入力欄の下の隙間を最小限に */
    div[data-testid="stChatInput"] { padding-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 認証 ---
if "password_correct" not in st.session_state:
    pw = st.text_input("PW", type="password")
    if pw == "05250206":
        st.session_state["password_correct"] = True
        st.rerun()
    st.stop()

# --- 4. 接続 ---
query_params = st.query_params
current_user = query_params.get("user", "HIDE").upper()
supabase = create_client("https://kvqbwknrsdasoipttkpr.supabase.co", "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT")

# --- 5. 操作 ---
st.title("💬 M25-Chat")
auto_update = st.toggle("自動更新(5s)", value=True)
if auto_update:
    st_autorefresh(interval=5000, key="chat_ref")

st.divider()

# --- 6. 表示 (20件) ---
try:
    res = supabase.table("messages").select("*").order("created_at", desc=True).limit(20).execute()
    for m in res.data[::-1]:
        sender = m['sender_name']
        s_up = sender.upper()
        align = "align-right" if s_up == current_user else "align-left"
        h_style = "flex-direction: row-reverse;" if s_up == current_user else ""
        n_class = "name-maki" if "MAKI" in s_up else "name-hide" if "HIDE" in s_up else ""
        
        st.markdown(f"""
            <div class="chat-row {align}">
                <div class="chat-header" style="{h_style}">
                    <span class="{n_class}">{sender}</span>
                    <span class="timestamp">{m['created_at'][11:16]}</span>
                </div>
                <div class="message-text text-content">{m['message_body']}</div>
            </div>
        """, unsafe_allow_html=True)
except:
    st.empty()

# --- 7. 入力 ---
prompt = st.chat_input("メッセージを入力...")
if prompt:
    supabase.table("messages").insert({"sender_name": current_user, "message_body": prompt}).execute()
    st.rerun()

# --- 8. スクロール ---
components.html(
    """<script>
    const f = () => { window.parent.document.querySelector(".main").scrollTo(0, 99999); };
    setTimeout(f, 500); setTimeout(f, 1500);
    </script>""", height=0
)