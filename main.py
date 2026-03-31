import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# --- 1. 設定 ---
st.set_page_config(page_title="M25", page_icon="💬", layout="wide")

# --- 2. デザイン (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #313338; color: #dbdee1; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display:none;}

    .block-container { 
        padding-top: 1rem; 
        padding-bottom: 50px !important; 
        max-width: 100% !important; 
    }

    .chat-row { display: flex; flex-direction: column; margin-bottom: 16px; width: 100%; }
    .chat-header { display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; font-size: 0.85rem; }
    .message-text { font-size: 1.05rem; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; max-width: 85%; }
    .align-right { align-items: flex-end; text-align: right; }
    .align-left { align-items: flex-start; text-align: left; }
    
    /* 名前の色設定（判定は大文字で行いますが、表示は元の文字を維持します） */
    .name-maki { color: #ffa657 !important; font-weight: bold; }
    .name-hide { color: #58a6ff !important; font-weight: bold; }
    
    .timestamp { color: #949ba4; font-size: 0.75rem; }
    .text-content { color: #e6edf3; }
    div[data-testid="stChatInput"] { padding-bottom: 0px !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 認証 ---
if "password_correct" not in st.session_state:
    pw = st.text_input("PW", type="password")
    if pw == "05250206":
        st.session_state["password_correct"] = True
        st.rerun()
    st.stop()

# --- 4. 接続 ---
query_params = st.query_params
# 判定用には大文字を使いますが、変数としては元の値を保持
current_user_raw = query_params.get("user", "Hide")
current_user_upper = current_user_raw.upper()

SUPABASE_URL = "https://kvqbwknrsdasoipttkpr.supabase.co"
SUPABASE_KEY = "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 5. 操作 ---
st.title("💬 M25-Chat")
auto_update = st.toggle("自動更新(5s)", value=True)
if auto_update:
    st_autorefresh(interval=5000, key="chat_ref")

st.divider()

# --- 6. 表示 (20件) ---
try:
    res = supabase.table("messages").select("*").order("created_at", desc=True).limit(20).execute()
    messages = res.data[::-1]
    
    for m in messages:
        sender_name = m['sender_name'] # DBから取得した名前（Hide や Maki）
        s_up = sender_name.upper()     # 判定用
        
        # 右寄せ・左寄せの判定
        align = "align-right" if s_up == current_user_upper else "align-left"
        h_style = "flex-direction: row-reverse;" if s_up == current_user_upper else ""
        
        # 色分けのクラス判定
        n_class = ""
        if "MAKI" in s_up:
            n_class = "name-maki"
        elif "HIDE" in s_up:
            n_class = "name-hide"
            
        t_str = m['created_at'][11:16]
        
        st.markdown(f"""
            <div class="chat-row {align}">
                <div class="chat-header" style="{header_style if 'header_style' in locals() else h_style}">
                    <span class="{n_class}">{sender_name}</span>
                    <span class="timestamp">{t_str}</span>
                </div>
                <div class="message-text text-content">{m['message_body']}</div>
            </div>
        """, unsafe_allow_html=True)
except Exception as e:
    st.empty()

# --- 7. 入力 ---
prompt = st.chat_input("メッセージを入力...")
if prompt:
    try:
        # 送信時は元の表記(Hide/Maki)で送るように設定
        supabase.table("messages").insert({"sender_name": current_user_raw, "message_body": prompt}).execute()
        st.rerun()
    except:
        pass

# --- 8. スクロール ---
components.html(
    """<script>
    const f = () => { 
        const main = window.parent.document.querySelector(".main");
        if (main) main.scrollTo(0, 99999); 
    };
    setTimeout(f, 500); 
    </script>""", height=0
)