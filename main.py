import streamlit as st
from supabase import create_client

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

# --- 2. 設定と接続 ---
query_params = st.query_params
current_user = query_params.get("user", "Hide") 

SUPABASE_URL = "https://kvqbwknrsdasoipttkpr.supabase.co"
SUPABASE_KEY = "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ページ全体の余白を最小化
st.set_page_config(page_title="M25", page_icon="💬", layout="centered")

# --- 3. スマホ特化・超省スペースデザイン (CSS) ---
st.markdown("""
    <style>
    /* 画面全体の余白を削る */
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    .stApp { background-color: #1a1c23 !important; color: #e0e6ed !important; }
    
    /* 入力欄のコンパクト化 */
    .stTextInput>div>div>input { padding: 5px !important; }
    .stTextArea>div>div>textarea { height: 70px !important; }
    
    /* 吹き出しの設定 */
    .chat-row { display: flex; margin-bottom: 8px; width: 100%; align-items: flex-end; }
    .chat-bubble { 
        padding: 8px 12px; border-radius: 15px; max-width: 80%; 
        width: auto; display: inline-block; font-size: 15px; line-height: 1.4; 
        color: #ffffff !important; box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        word-wrap: break-word;
    }
    
    .bubble-hide { background-color: #4682b4 !important; border-bottom-right-radius: 2px; }
    .bubble-maki { background-color: #d2691e !important; border-bottom-left-radius: 2px; }
    
    .chat-info { font-size: 9px; color: #888888; margin: 0 4px; min-width: fit-content; line-height: 1; }
    .sender-name { font-size: 11px; font-weight: bold; margin-bottom: 2px; color: #d2691e; }
    
    /* フォームの枠線を消してスッキリさせる */
    [data-testid="stForm"] { border: none !important; padding: 0 !important; }
    </style>
""", unsafe_allow_html=True)

# タイトルも小さく
st.markdown("### 💬 M25-Chat")

# --- 4. 送信フォーム（省スペース版） ---
with st.form("send_message", clear_on_submit=True):
    # 名前とボタンを横に並べるためのカラム
    col1, col2 = st.columns([2, 1])
    with col1:
        name = st.text_input("Name", value=current_user, label_visibility="collapsed")
    with col2:
        submit = st.form_submit_button("送信", use_container_width=True)
    
    msg = st.text_area("Message", placeholder="メッセージを入力...", label_visibility="collapsed")
    
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
                    <div class="chat-info" style="text-align: right;">{time}<br>✅</div>
                    <div class="chat-bubble bubble-hide">{text}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="chat-row" style="justify-content: flex-start;">
                    <div style="display: flex; flex-direction: column; align-items: flex-start; max-width: 100%;">
                        <div class="sender-name" style="margin-left: 8px;">{sender}</div>
                        <div style="display: flex; align-items: flex-end;">
                            <div class="chat-bubble bubble-maki" style="margin-left: 8px;">{text}</div>
                            <div class="chat-info">{time}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
except Exception as e:
    st.empty()