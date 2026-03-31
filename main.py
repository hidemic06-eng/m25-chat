import streamlit as st
from supabase import create_client

# --- 2. 設定と接続 (set_page_configは最初に行う必要があります) ---
st.set_page_config(page_title="M25", page_icon="💬", layout="wide")

# --- メニューと猫アイコンを非表示にする設定 ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

# --- 1. パスワード認証機能 ---
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

# --- 2. 継続設定 ---
query_params = st.query_params
current_user = query_params.get("user", "Hide") 

SUPABASE_URL = "https://kvqbwknrsdasoipttkpr.supabase.co"
SUPABASE_KEY = "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 3. デザイン：初期の明るいLINE風スタイル (CSS) ---
st.markdown("""
    <style>
    /* 全体を標準の明るいテーマに */
    .stApp { background-color: #f0f2f6; color: #31333F; }
    
    /* 吹き出しのレイアウト */
    .chat-row { display: flex; margin-bottom: 12px; width: 100%; align-items: flex-end; }
    
    .chat-bubble { 
        padding: 10px 14px; border-radius: 18px; 
        max-width: 80%; width: auto; 
        font-size: 16px; line-height: 1.4; 
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    
    /* Hide用（右・明るい緑） */
    .bubble-hide { background-color: #95ec7a !important; color: #000000 !important; border-bottom-right-radius: 2px; }
    
    /* Maki用（左・白） */
    .bubble-maki { background-color: #ffffff !important; color: #000000 !important; border: 1px solid #ddd; border-bottom-left-radius: 2px; }
    
    .chat-info { font-size: 10px; color: #888888; margin: 0 5px; min-width: fit-content; }
    .sender-name { font-size: 12px; font-weight: bold; margin-bottom: 2px; color: #555555; margin-left: 10px; }

    /* メニュー類は隠したままにします */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    </style>
""", unsafe_allow_html=True)

st.title("💬 M25-Chat")

# --- 4. 送信フォーム ---
with st.form("send_message", clear_on_submit=True):
    name = st.text_input("Name", value=current_user)
    msg = st.text_area("Message", placeholder="メッセージを入力...")
    submit = st.form_submit_button("送信", use_container_width=True)
    
    if submit and msg:
        try:
            supabase.table("messages").insert({"sender_name": name, "message_body": msg}).execute()
            st.rerun()
        except Exception as e:
            st.error(f"Error")

# --- 5. 履歴表示 ---
st.write("---")
try:
    res = supabase.table("messages").select("*").order("created_at", desc=True).execute()
    for m in res.data:
        sender = m['sender_name']
        text = m['message_body']
        time = m['created_at'][11:16]

        if sender.upper() == "HIDE":
            st.markdown(f"""
                <div class="chat-row" style="justify-content: flex-end;">
                    <div class="chat-info" style="text-align: right;">{time} ✅</div>
                    <div class="chat-bubble bubble-hide">{text}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="chat-row" style="justify-content: flex-start;">
                    <div style="display: flex; flex-direction: column; align-items: flex-start; max-width: 85%;">
                        <div class="sender-name">{sender}</div>
                        <div style="display: flex; align-items: flex-end;">
                            <div class="chat-bubble bubble-maki">{text}</div>
                            <div class="chat-info">{time}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
except Exception as e:
    st.empty()

