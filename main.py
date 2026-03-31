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
    [data-testid="bundle-viewer-container"] {display: none !important;}

    .block-container { 
        padding-top: 1rem; 
        padding-bottom: 80px !important; 
        max-width: 100% !important; 
    }

    .chat-row { display: flex; flex-direction: column; margin-bottom: 16px; width: 100%; }
    .chat-header { display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; font-size: 0.85rem; }
    .message-text { font-size: 1.05rem; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; max-width: 85%; }
    .align-right { align-items: flex-end; text-align: right; }
    .align-left { align-items: flex-start; text-align: left; }
    .name-maki { color: #ffa657 !important; font-weight: bold; }
    .name-hide { color: #58a6ff !important; font-weight: bold; }
    .timestamp { color: #949ba4; font-size: 0.75rem; }
    .text-content { color: #e6edf3; }
    
    div[data-testid="stChatInput"] { padding-bottom: 0px !important; }

    .stButton > button {
        height: 30px !important;
        padding: 0 10px !important;
        font-size: 0.8rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 認証 (最も確実な標準方式) ---
if "password_correct" not in st.session_state:
    st.write("🔒 Enter Password")
    
    # 履歴を出さない、伏せ字にする、を標準機能だけで実行
    # type="password" にすれば、スマホでも「数字のみ」の設定にしていればテンキーが出やすくなります
    pw = st.text_input("Password", type="password", key="standard_pw")

    # Enterキーまたは入力後の確定で判定
    if pw == "05250206":
        st.session_state["password_correct"] = True
        st.rerun()
    elif len(pw) >= 8:
        st.error("❌")
    
    st.stop()

# --- 4. ページ管理 ---
if "page_offset" not in st.session_state:
    st.session_state["page_offset"] = 0

# --- 5. 接続 ---
query_params = st.query_params
current_user_raw = query_params.get("user", "Hide")
current_user_upper = current_user_raw.upper()
supabase = create_client("https://kvqbwknrsdasoipttkpr.supabase.co", "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT")

# --- 6. 操作パネル ---
st.title("💬 M25-Chat")
auto_update = st.toggle("自動更新(5s)", value=True)

if auto_update and st.session_state["page_offset"] == 0:
    st_autorefresh(interval=5000, key="chat_ref")

st.divider()

# --- 7. ページ切り替え ---
col_prev, col_page, col_next = st.columns([1, 2, 1])
with col_prev:
    if st.button("⬅️ 前の20件"):
        st.session_state["page_offset"] += 20
        st.rerun()
with col_page:
    current_range = f"{st.session_state['page_offset'] + 1}〜{st.session_state['page_offset'] + 20}件目"
    st.write(f"<div style='text-align:center; font-size:0.8rem; color:#949ba4;'>{current_range}</div>", unsafe_allow_html=True)
with col_next:
    if st.session_state["page_offset"] >= 20:
        if st.button("次の20件 ➡️"):
            st.session_state["page_offset"] -= 20
            st.rerun()
    else:
        st.button("最新です", disabled=True)

# --- 8. 表示 ---
try:
    res = supabase.table("messages") \
        .select("*") \
        .order("created_at", desc=True) \
        .range(st.session_state["page_offset"], st.session_state["page_offset"] + 19) \
        .execute()
    
    messages = res.data[::-1]

    for m in messages:
        sender_name = m['sender_name']
        s_up = sender_name.upper()
        align = "align-right" if s_up == current_user_upper else "align-left"
        h_style = "flex-direction: row-reverse;" if s_up == current_user_upper else ""
        n_class = "name-maki" if "MAKI" in s_up else "name-hide" if "HIDE" in s_up else ""
        
        st.markdown(f"""
            <div class="chat-row {align}">
                <div class="chat-header" style="{h_style}">
                    <span class="{n_class}">{sender_name}</span>
                    <span class="timestamp">{m['created_at'][11:16]}</span>
                </div>
                <div class="message-text text-content">{m['message_body']}</div>
            </div>
        """, unsafe_allow_html=True)
except:
    st.empty()

# --- 9. 入力 ---
prompt = st.chat_input("メッセージを入力...")
if prompt:
    supabase.table("messages").insert({"sender_name": current_user_raw, "message_body": prompt}).execute()
    st.session_state["page_offset"] = 0
    st.rerun()

# --- 10. スクロール ---
if st.session_state["page_offset"] == 0:
    components.html(
        """<script>
        window.parent.document.querySelector(".main").scrollTo(0, 99999);
        </script>""", height=0
    )