import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# --- 1. 設定 ---
st.set_page_config(page_title="M25", page_icon="💬", layout="wide")

# --- 2. デザイン (CSS) ---
st.markdown("""
    <style>
    /* 全体の背景と文字色 */
    .stApp { background-color: #313338; color: #dbdee1; }
    
    /* 1. 標準メニュー系を非表示 */
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}

    /* 2. 【最重要】右下の「Manage app」アイコンを消すための強力なセレクタ群 */
    /* これら複数の指定で、現行のStreamlit Cloudのメニューを封じ込めます */
    [data-testid="bundle-viewer-container"],
    [data-testid="stStatusWidget"],
    .st-emotion-cache-1wbqy5l, 
    .st-emotion-cache-k7vsyb,
    iframe[title="managed-browser"] {
        display: none !important;
    }

    /* 3. 余白調整（スマホのスクロール遊び用） */
    .block-container { 
        padding-top: 1rem; 
        padding-bottom: 3.5rem !important; 
        max-width: 100% !important; 
    }

    /* チャットのデザイン（維持） */
    .chat-row { display: flex; flex-direction: column; margin-bottom: 16px; width: 100%; }
    .chat-header { display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; font-size: 0.85rem; }
    .message-text { font-size: 1.05rem; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; max-width: 85%; }
    .align-right { align-items: flex-end; text-align: right; }
    .align-left { align-items: flex-start; text-align: left; }
    .name-maki { color: #ffa657 !important; font-weight: bold; }
    .name-hide { color: #58a6ff !important; font-weight: bold; }
    .timestamp { color: #949ba4; font-size: 0.75rem; }
    .text-content { color: #e6edf3; }
    div[data-testid="stChatInput"] { padding-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. パスワード認証 (スマホの安定性重視版) ---
if "password_correct" not in st.session_state:
    st.title("🔒 Authentication")
    pw = st.text_input("Password", type="password")
    if pw == "05250206":
        st.session_state["password_correct"] = True
        st.rerun()
    elif pw:
        st.error("❌")
    st.stop()

# --- 4. 接続 & ユーザー判定 ---
query_params = st.query_params
current_user = query_params.get("user", "HIDE").upper()

SUPABASE_URL = "https://kvqbwknrsdasoipttkpr.supabase.co"
SUPABASE_KEY = "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 5. 操作パネル ---
st.title("💬 M25-Chat")
col1, col2 = st.columns([2, 1])
with col1:
    auto_update = st.toggle("自動更新(5s)", value=True)
with col2:
    if st.button("🔄更新", use_container_width=True):
        st.rerun()

if auto_update:
    st_autorefresh(interval=5000, key="chat_update_timer")

st.divider()

# --- 6. 履歴の表示 (最新20件) ---
try:
    res = supabase.table("messages").select("*").order("created_at", desc=True).limit(20).execute()
    messages = res.data[::-1]
    for m in messages:
        sender = m['sender_name']
        sender_upper = sender.upper()
        text = m['message_body']
        time = m['created_at'][11:16]
        align_class = "align-right" if sender_upper == current_user else "align-left"
        header_style = "flex-direction: row-reverse;" if sender_upper == current_user else ""
        name_class = "name-maki" if "MAKI" in sender_upper else "name-hide" if "HIDE" in sender_upper else "name-default"
        st.markdown(f"""
            <div class="chat-row {align_class}">
                <div class="chat-header" style="{header_style}">
                    <span class="{name_class}">{sender}</span>
                    <span class="timestamp">{time}</span>
                </div>
                <div class="message-text text-content">{text}</div>
            </div>
        """, unsafe_allow_html=True)
except Exception:
    st.empty()

# --- 7. 入力欄 ---
prompt = st.chat_input("メッセージを入力...")
if prompt:
    try:
        supabase.table("messages").insert({"sender_name": current_user, "message_body": prompt}).execute()
        st.rerun()
    except Exception:
        pass

# --- 8. スクロールJavaScript ---
components.html(
    """
    <script>
    const scrollToEnd = () => {
        const win = window.parent.document;
        const main = win.querySelector(".main");
        if (main) {
            main.scrollTo({ top: main.scrollHeight + 5000, behavior: 'auto' });
        }
    };
    setTimeout(scrollToEnd, 500);
    setTimeout(scrollToEnd, 1500);
    </script>
    """,
    height=0,
)