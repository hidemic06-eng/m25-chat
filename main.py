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

# --- 2. 設定 ---
query_params = st.query_params
user_param = query_params.get("user", "HIDE") 

SUPABASE_URL = "https://kvqbwknrsdasoipttkpr.supabase.co"
SUPABASE_KEY = "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 3. デザイン調整 (CSS) ---
st.markdown("""
    <style>
    /* 画面端の余白を削り、ダークモード背景に */
    .block-container { padding: 1rem 0.5rem !important; max-width: 100% !important; }
    .stApp { background-color: #1a1c23 !important; color: #e0e6ed !important; }
    
    /* 入力エリアの調整 */
    [data-testid="stForm"] { border: none !important; padding: 0 !important; }
    .stTextArea>div>div>textarea { height: 80px !important; background-color: #2d333b !important; color: #fff !important; }
    .stTextInput>div>div>input { background-color: #2d333b !important; color: #fff !important; }

    /* 吹き出しの設定：最大幅8割、内容に合わせて縮む */
    .chat-row { display: flex; margin-bottom: 15px; width: 100%; align-items: flex-end; }
    .chat-bubble { 
        padding: 10px 14px; border-radius: 18px; 
        max-width: 80%; width: auto; 
        font-size: 16px; line-height: 1.4; 
        color: #ffffff !important; box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    
    /* HIDE（右・落ち着いた青） */
    .bubble-hide { background-color: #4682b4 !important; border-bottom-right-radius: 2px; }
    /* MAKI（左・落ち着いたオレンジ） */
    .bubble-maki { background-color: #d2691e !important; border-bottom-left-radius: 2px; }
    
    .chat-info { font-size: 10px; color: #888888; margin: 0 5px; min-width: fit-content; }
    .sender-name { font-size: 11px; font-weight: bold; margin-bottom: 2px; color: #d2691e; margin-left: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("💬 M25-Chat")

# --- 4. 送信フォーム ---
with st.form("send_message", clear_on_submit=True):
    # ラベルを消して省スペース化
    name = st.text_input("名前", value=user_param, label_visibility="collapsed")
    msg = st.text_area("内容を入力...", placeholder="メッセージを入力してください...", label_visibility="collapsed")
    submit = st.form_submit_button("送信する", use_container_width=True)
    
    if submit and msg:
        try:
            supabase.table("messages").insert({"sender_name": name, "message_body": msg}).execute()
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

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
                            <div class="chat-info" style="padding-bottom: 2px;">{time}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
except Exception as e:
    st.empty()