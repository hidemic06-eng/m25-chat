import streamlit as st
from supabase import create_client

# --- 1. 設定 (必ず最初に実行) ---
st.set_page_config(page_title="M25", page_icon="💬", layout="wide")

# --- 2. メニュー非表示 & デザイン (CSS) ---
st.markdown("""
    <style>
    /* 全体背景：Discord風ダーク */
    .stApp { background-color: #313338; color: #dbdee1; }
    
    /* 余計な要素を隠す */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    
    /* 履歴エリア：入力欄が下にあるので下に余白を作る */
    .block-container { padding-top: 1rem; padding-bottom: 5rem; max-width: 100% !important; }

    /* 吹き出しの基本構造 */
    .chat-row { display: flex; margin-bottom: 12px; width: 100%; align-items: flex-end; }
    
    .chat-bubble { 
        padding: 10px 14px; border-radius: 18px; 
        max-width: 75%; width: auto; 
        font-size: 16px; line-height: 1.4; 
        color: #ffffff !important; box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        word-wrap: break-word;
        white-space: pre-wrap;
    }

    /* 右側 (HIDE)：青系 */
    .bubble-right { background-color: #4682b4 !important; border-bottom-right-radius: 2px; }
    /* 左側 (MAKI)：オレンジ系 */
    .bubble-left { background-color: #d2691e !important; border-bottom-left-radius: 2px; }

    .chat-info { font-size: 10px; color: #949ba4; margin: 0 6px; min-width: fit-content; }
    .sender-name { font-size: 11px; font-weight: bold; margin-bottom: 2px; color: #d2691e; margin-left: 8px; }
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

# --- 5. 履歴の表示 (古いものから順に下へ) ---
try:
    # Discord/LINEと同じく、新しいのが下に来るように asc=True
    res = supabase.table("messages").select("*").order("created_at", desc=False).execute()
    
    for m in res.data:
        sender = m['sender_name']
        text = m['message_body']
        time = m['created_at'][11:16]

        if sender.upper() == "HIDE":
            # 自分 (右寄せ)
            st.markdown(f"""
                <div class="chat-row" style="justify-content: flex-end;">
                    <div class="chat-info" style="text-align: right; padding-bottom: 2px;">{time} ✅</div>
                    <div class="chat-bubble bubble-right">{text}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            # 相手 (左寄せ)
            st.markdown(f"""
                <div class="chat-row" style="justify-content: flex-start;">
                    <div style="display: flex; flex-direction: column; align-items: flex-start; max-width: 80%;">
                        <div class="sender-name">{sender}</div>
                        <div style="display: flex; align-items: flex-end;">
                            <div class="chat-bubble bubble-left">{text}</div>
                            <div class="chat-info" style="padding-bottom: 2px;">{time}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
except Exception as e:
    st.empty()

# --- 6. 入力欄の固定 (画面最下部) ---
prompt = st.chat_input("メッセージを入力...")

if prompt:
    try:
        supabase.table("messages").insert({"sender_name": user_param, "message_body": prompt}).execute()
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")