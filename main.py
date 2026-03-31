import streamlit as st
from supabase import create_client

# --- 1. 設定 (必ず最初に実行) ---
st.set_page_config(page_title="M25", page_icon="💬", layout="wide")

# --- 2. デザイン (CSS) ---
st.markdown("""
    <style>
    /* 全体背景：Discord風ダークグレー */
    .stApp { background-color: #313338; color: #dbdee1; }
    
    /* 不要な要素を非表示 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    
    /* 履歴エリアの余白調整 */
    .block-container { padding-top: 1rem; padding-bottom: 6rem; max-width: 100% !important; }

    /* メッセージ一行の枠（背景なし・枠なし） */
    .chat-row { 
        display: flex; 
        flex-direction: column;
        margin-bottom: 16px; 
        width: 100%; 
    }
    
    /* 名前と時間のヘッダー */
    .chat-header { 
        display: flex; 
        align-items: baseline; 
        gap: 8px; 
        margin-bottom: 4px;
        font-size: 0.85rem;
    }

    /* 本文：枠をなくしてシンプルに */
    .message-text { 
        font-size: 1rem; 
        line-height: 1.5; 
        white-space: pre-wrap;
        word-wrap: break-word;
        max-width: 85%;
    }

    /* 右側 (HIDE) の配色と配置 */
    .align-right { align-items: flex-end; text-align: right; }
    .name-hide { color: #58a6ff; font-weight: bold; }
    .text-hide { color: #e6edf3; }

    /* 左側 (MAKI) の配色と配置 */
    .align-left { align-items: flex-start; text-align: left; }
    .name-maki { color: #ffa657; font-weight: bold; }
    .text-maki { color: #dbdee1; }

    .timestamp { color: #949ba4; font-size: 0.75rem; }
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

# --- 4. 接続 & 設定 ---
query_params = st.query_params
user_param = query_params.get("user", "HIDE")

SUPABASE_URL = "https://kvqbwknrsdasoipttkpr.supabase.co"
SUPABASE_KEY = "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("💬 M25-Chat")

# --- 5. 履歴の表示 (新しいのが下) ---
try:
    res = supabase.table("messages").select("*").order("created_at", desc=False).execute()
    
    for m in res.data:
        sender = m['sender_name']
        text = m['message_body']
        time = m['created_at'][11:16]

        if sender.upper() == "HIDE":
            # 自分 (右寄せ・青文字)
            st.markdown(f"""
                <div class="chat-row align-right">
                    <div class="chat-header" style="flex-direction: row-reverse;">
                        <span class="name-hide">{sender}</span>
                        <span class="timestamp">{time}</span>
                    </div>
                    <div class="message-text text-hide">{text}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            # 相手 (左寄せ・オレンジ文字)
            st.markdown(f"""
                <div class="chat-row align-left">
                    <div class="chat-header">
                        <span class="name-maki">{sender}</span>
                        <span class="timestamp">{time}</span>
                    </div>
                    <div class="message-text text-maki">{text}</div>
                </div>
            """, unsafe_allow_html=True)
except Exception as e:
    st.empty()

# --- 6. 入力欄の固定 ---
prompt = st.chat_input("メッセージを入力...")

if prompt:
    try:
        supabase.table("messages").insert({"sender_name": user_param, "message_body": prompt}).execute()
        st.rerun()
    except Exception as e:
        st.error(f"Error")