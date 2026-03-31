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
current_user = query_params.get("user", "HIDE") # 今ログインしている人

SUPABASE_URL = "https://kvqbwknrsdasoipttkpr.supabase.co"
SUPABASE_KEY = "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="M25-Chat", page_icon="💬")

# --- 3. アップロード画像風・ダークモードデザイン (CSS) ---
st.markdown("""
    <style>
    /* 全体の背景色を少し明るいダークグレーに（画像風） */
    .stApp {
        background-color: #1a1c23 !important;
        color: #e0e6ed !important;
    }

    /* 入力欄（テキスト入力、テキストエリア）のスタイル */
    /* 背景を濃いグレー (#2d333b)、文字を白 (#ffffff) に */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #2d333b !important;
        color: #ffffff !important;
        border: 1px solid #444c56 !important; /* 枠線を少し明るく */
        border-radius: 8px !important;
        font-size: 16px !important;
    }

    /* 入力欄にフォーカスが当たった時の枠線の色（少し青っぽく） */
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #539bf5 !important;
        box-shadow: 0 0 0 1px #539bf5 !important;
    }

    /* 入力欄のラベル（"名前"、"メッセージ入力"など）の文字色 */
    .stTextInput>label, .stTextArea>label {
        color: #e0e6ed !important;
        font-weight: 600 !important;
    }

    /* 送信ボタンのスタイル（画像のような濃いグレー） */
    .stButton>button {
        background-color: #3e4451 !important;
        color: #ffffff !important;
        border: 1px solid #444c56 !important;
        border-radius: 8px !important;
        padding: 8px 20px !important;
    }
    /* ボタンホバー時 */
    .stButton>button:hover {
        background-color: #4c5361 !important;
        border-color: #539bf5 !important;
    }

    /* 履歴表示の吹き出し（LINE風を維持しつつ、ダークモードに対応） */
    .chat-row { display: flex; margin-bottom: 15px; width: 100%; }
    .chat-bubble { 
        padding: 12px 18px; 
        border-radius: 18px; 
        max-width: 80%; 
        font-size: 16px; 
        line-height: 1.5; 
        box-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    /* 自分の吹き出し（ダークグリーン） */
    .bubble-hide { background-color: #2e6b3b !important; color: #ffffff !important; border-top-right-radius: 2px; }
    /* 相手の吹き出し（濃いグレー） */
    .bubble-maki { background-color: #3e4451 !important; color: #ffffff !important; border: 1px solid #444c56; border-top-left-radius: 2px; }
    
    .chat-info { font-size: 11px; color: #888888; margin-top: 5px; }
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

# --- 5. 履歴表示 (吹き出しスタイル) ---
st.write("---")
try:
    res = supabase.table("messages").select("*").order("created_at", desc=True).execute()
    for m in res.data:
        sender = m['sender_name']
        text = m['message_body']
        time = m['created_at'][11:16] # 時刻だけ抽出

        # 自分のメッセージか相手のかでクラスを切り替え
        if sender == current_user:
            # 自分（右側）
            st.markdown(f"""
                <div class="chat-row" style="justify-content: flex-end;">
                    <div style="text-align: right; margin-right: 10px;">
                        <div class="chat-bubble" style="background-color: #DCF8C6; border-radius: 15px 15px 2px 15px;">{text}</div>
                        <div class="chat-info">{time} ✅</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            # 相手（左側）
            st.markdown(f"""
                <div class="chat-row" style="justify-content: flex-start;">
                    <div style="text-align: left; margin-left: 10px;">
                        <div style="font-size: 12px; font-weight: bold; margin-bottom: 2px;">{sender}</div>
                        <div class="chat-bubble" style="background-color: #FFFFFF; border: 1px solid #ddd; border-radius: 15px 15px 15px 2px;">{text}</div>
                        <div class="chat-info">{time}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
except Exception as e:
    st.write("履歴を読み込み中...")