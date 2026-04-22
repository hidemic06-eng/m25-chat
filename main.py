import streamlit as st
from streamlit_javascript import st_javascript

# 1. ページ設定
st.set_page_config(page_title="M25-Login", page_icon="🔒")

# --- CSS（文字色・背景・入力欄のスタイルを強制固定） ---
st.markdown("""
    <style>
    .stApp { background-color: #313338; color: #dbdee1; }
    label { color: #ffffff !important; }
    input { background-color: #40444b !important; color: white !important; }
    div[data-testid="stText"] { color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# 2. ユーザー自動判定ロジック
if "username" not in st.session_state:
    # URL引数を確認 (?user=Maki 等)
    url_user = st.query_params.get("user", "")
    
    if url_user.capitalize() in ["Hide", "Maki"]:
        st.session_state["username"] = url_user.capitalize()
    else:
        # User-Agentを取得してOS判定（JavaScript実行）
        ua = st_javascript("window.navigator.userAgent")
        if ua:
            if "Android" in ua:
                st.session_state["username"] = "Maki"
            elif "iPhone" in ua or "iPad" in ua or "Macintosh" in ua:
                st.session_state["username"] = "Hide"
            else:
                st.session_state["username"] = "Hide"

# 3. ログイン済みなら即遷移して終了
if st.session_state.get("password_correct", False):
    st.switch_page("pages/chat.py")
    st.stop()

# 4. ログイン画面（入力エリアはパスワードの1つだけ）
st.title("🔐 M25-Chat Login")
display_name = st.session_state.get('username', 'Hide')
st.write(f"User: **{display_name}**")

# パスワード入力欄（Enterキーで確定）
p_input = st.text_input("パスワードを入力してEnter", type="password", key="p_input")

if p_input:
    # 指定のパスワードで判定
    if p_input == "05250206":
        st.session_state["password_correct"] = True
        st.session_state["username"] = display_name # 判定された名前を確定
        st.rerun()
    else:
        st.error("😕 パスワードが違います")

st.stop()
