import streamlit as st
from streamlit_javascript import st_javascript

# 1. ページ設定
st.set_page_config(page_title="M25-Login", page_icon="🔒")

# --- CSS（背景色と文字色の調整） ---
st.markdown("""
    <style>
    .stApp { background-color: #313338; color: #dbdee1; }
    label { color: #ffffff !important; }
    input { background-color: #40444b !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# 2. ユーザー自動判定ロジック
if "username" not in st.session_state:
    # URL引数を確認 (?user=Maki など)
    url_user = st.query_params.get("user", "")
    
    if url_user.capitalize() in ["Hide", "Maki"]:
        st.session_state["username"] = url_user.capitalize()
    else:
        # User-Agentを取得してOS判定
        ua = st_javascript("window.navigator.userAgent")
        if ua:
            if "Android" in ua:
                st.session_state["username"] = "Maki"
            elif "iPhone" in ua or "iPad" in ua or "Macintosh" in ua:
                st.session_state["username"] = "Hide"
            else:
                st.session_state["username"] = "Hide" # デフォルト

# 3. ログイン済みなら即遷移
if st.session_state.get("password_correct", False):
    st.switch_page("pages/chat.py")
    st.stop()

# 4. ログイン画面（入力エリアはパスワードの「1つ」だけになります）
st.title(f"🔐 M25-Chat Login")
st.write(f"User: **{st.session_state.get('username', 'Detecting...')}**")

# パスワード入力欄（ここだけが表示されます）
p_input = st.text_input("パスワードを入力してEnter", type="password", key="p_input")

if p_input:
    if p_input == st.secrets["PASSWORD"]:
        st.session_state["password_correct"] = True
        st.rerun()
    else:
        st.error("😕 パスワードが違います")

# ログインしていない時はここで止める
st.stop()
