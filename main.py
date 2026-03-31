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
        st.text_input("パスワード", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.error("😕 パスワードが正しくありません")
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

st.set_page_config(page_title="M25-Chat", page_icon="💬")

# --- 3. ダークモード & カスタムデザイン (CSS) ---
st.markdown("""
    <style>
    /* 背景と入力欄のデザイン */
    .stApp { background-color: #1a1c23 !important; color: #e0e6ed !important; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #2d333b !important; color: #ffffff !important;
        border: 1px solid #444c56 !important; border-radius: 8px !important;
    }
    
    /* 吹き出しの共通設定 */
    .chat-row { display: flex; margin-bottom: 20px; width: 100%; align-items: flex-end; }
    
    /* 横幅を80%に設定 */
    .chat-bubble { 
        padding: 14px 20px; border-radius: 18px; width: 80%; 
        font-size: 16px; line-height: 1.5; color: #ffffff !important; 
        font-weight: 500; box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        word-wrap: break-word;
    }
    
    /* Hide用（右・落ち着いた深みのある青：スレートブルー系） */
    .bubble-hide { background-color: #4682b4 !important; border-bottom-right-radius: 2px; }
    
    /* Maki用（左・落ち着いた深みのあるオレンジ：テラコッタ系） */
    .bubble-maki { background-color: #d2691e !important; border-bottom-left-radius: 2px; }
    
    .chat-info { font-size: 10px; color: #888888; margin: 0 8px; min-width: fit-content; }
    .sender-name { font-size: 12px; font-weight: bold; margin-bottom: 6px; color: #d2691e; }
    </style>
""", unsafe_allow_html=True)

st.title("💬 M25-Chat")

# --- 4. 送信フォーム ---
with st.form("send_message", clear_on_submit=True):
    name = st.text_input("名前", value=current_user)
    msg = st.text_area("メッセージを入力...")
    submit = st.form_submit_button("送信")
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
            # Hideさんは右側（青・幅8割）
            st.markdown(f"""
                <div class="chat-row" style="justify-content: flex-end;">
                    <div class="chat-info" style="text-align: right;">{time}<br>✅</div>
                    <div class="chat-bubble bubble-hide">{text}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Makiさんは左側（オレンジ・幅8割）
            st.markdown(f"""
                <div class="chat-row" style="justify-content: flex-start;">
                    <div style="width: 100%;">
                        <div class="sender-name" style="margin-left: 10px;">{sender}</div>
                        <div style="display: flex; align-items: flex-end;">
                            <div class="chat-bubble bubble-maki" style="margin-left: 10px;">{text}</div>
                            <div class="chat-info">{time}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
except Exception as e:
    st.write("履歴を読み込み中...")