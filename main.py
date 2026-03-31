import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh # 追加

# --- 1. 設定 (必ず最初に実行) ---
st.set_page_config(page_title="M25", page_icon="💬", layout="wide")

# 5秒ごとに自動更新する設定を追加（これで新着メッセージに気づけます）
st_autorefresh(interval=5000, key="chat_update")

# --- 2. デザイン (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #313338; color: #dbdee1; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    .block-container { padding-top: 1rem; padding-bottom: 6rem; max-width: 100% !important; }

    .chat-row { display: flex; flex-direction: column; margin-bottom: 16px; width: 100%; }
    .chat-header { display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; font-size: 0.85rem; }
    
    /* 本文のサイズを少しだけ大きく(1.05rem)、行間をゆったり(1.6)に調整 */
    .message-text { 
        font-size: 1.05rem; 
        line-height: 1.6; 
        white-space: pre-wrap; 
        word-wrap: break-word; 
        max-width: 85%; 
    }

    /* 配置用のクラス */
    .align-right { align-items: flex-end; text-align: right; }
    .align-left { align-items: flex-start; text-align: left; }

    /* 名前ごとの固定色設定 */
    .name-maki { color: #ffa657 !important; font-weight: bold; } /* オレンジ */
    .name-hide { color: #58a6ff !important; font-weight: bold; } /* 青 */
    .name-default { color: #dbdee1; font-weight: bold; }

    .timestamp { color: #949ba4; font-size: 0.75rem; }
    .text-content { color: #e6edf3; }
    </style>
""", unsafe_allow_html=True)

# --- 3. パスワード認証 ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "05250206":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.text_input("PW", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.error("❌")
        return False
    return True

if not check_password():
    st.stop()

# --- 4. 接続 & URLからユーザー判定 ---
query_params = st.query_params
current_user = query_params.get("user", "HIDE").upper()

SUPABASE_URL = "https://kvqbwknrsdasoipttkpr.supabase.co"
SUPABASE_KEY = "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("💬 M25-Chat")

# --- 5. 履歴の表示 ---
try:
    res = supabase.table("messages").select("*").order("created_at", desc=False).execute()
    
    for m in res.data:
        sender = m['sender_name']
        sender_upper = sender.upper()
        text = m['message_body']
        time = m['created_at'][11:16]

        align_class = "align-right" if sender_upper == current_user else "align-left"
        header_style = "flex-direction: row-reverse;" if sender_upper == current_user else ""

        if "MAKI" in sender_upper:
            name_class = "name-maki"
        elif "HIDE" in sender_upper:
            name_class = "name-hide"
        else:
            name_class = "name-default"

        st.markdown(f"""
            <div class="chat-row {align_class}">
                <div class="chat-header" style="{header_style}">
                    <span class="{name_class}">{sender}</span>
                    <span class="timestamp">{time}</span>
                </div>
                <div class="message-text text-content">{text}</div>
            </div>
        """, unsafe_allow_html=True)
except Exception as e:
    st.empty()

# --- 6. 入力欄の固定 ---
prompt = st.chat_input("メッセージを入力...")

if prompt:
    try:
        supabase.table("messages").insert({"sender_name": current_user, "message_body": prompt}).execute()
        st.rerun()
    except Exception as e:
        st.error(f"Error")