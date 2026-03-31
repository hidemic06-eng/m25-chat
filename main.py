import streamlit as st
from supabase import create_client

# --- 1. 設定と接続 (set_page_configは最初に行う必要があります) ---
st.set_page_config(page_title="M25", page_icon="💬", layout="wide")

# --- 2. パスワード認証 ---
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

# --- 3. Supabase接続 & ユーザー設定 ---
query_params = st.query_params
user_param = query_params.get("user", "HIDE")

SUPABASE_URL = "https://kvqbwknrsdasoipttkpr.supabase.co"
SUPABASE_KEY = "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 4. Discord風デザイン (CSS) ---
st.markdown("""
    <style>
    /* 全体をDiscord風のダークカラーに */
    .stApp { background-color: #313338; color: #dbdee1; }
    
    /* ヘッダー周りをスッキリ */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    
    /* 履歴エリアの余白調整 */
    .block-container { padding-top: 2rem; padding-bottom: 6rem; }
    
    /* メッセージの枠線を取り、背景色で区切る */
    .message-container {
        padding: 8px 16px;
        margin-bottom: 2px;
        border-radius: 4px;
    }
    .message-container:hover { background-color: #2e3035; }
    
    .sender-name { font-weight: bold; color: #ffffff; margin-right: 8px; font-size: 0.95rem; }
    .timestamp { color: #949ba4; font-size: 0.75rem; }
    .message-body { color: #dbdee1; margin-top: 2px; white-space: pre-wrap; font-size: 1rem; }

    /* 入力欄（st.chat_input）のカスタマイズは標準機能に任せるのが一番安定します */
    </style>
""", unsafe_allow_html=True)

st.title("💬 M25-Chat")

# --- 5. 履歴の表示機能（上に配置） ---
try:
    res = supabase.table("messages").select("*").order("created_at", desc=False).execute()
    
    for m in res.data:
        # 時刻の整形 (2026-03-31T12:34:56 -> 12:34)
        time_str = m['created_at'][11:16]
        
        # Discord風のフラットな表示
        st.markdown(f"""
            <div class="message-container">
                <span class="sender-name">{m['sender_name']}</span>
                <span class="timestamp">{time_str}</span>
                <div class="message-body">{m['message_body']}</div>
            </div>
        """, unsafe_allow_html=True)
except Exception as e:
    st.write("履歴を読み込み中...")

# --- 6. 入力欄の固定（最下部に表示） ---
# st.chat_input を使うと、自動的に画面下部に固定されます
prompt = st.chat_input("メッセージを入力...")

if prompt:
    # 送信処理
    data = {"sender_name": user_param, "message_body": prompt}
    try:
        supabase.table("messages").insert(data).execute()
        st.rerun()
    except Exception as e:
        st.error(f"エラー: {e}")