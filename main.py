import streamlit as st

# 1. ページ設定
st.set_page_config(page_title="M25-Login", page_icon="🔒")

# --- CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #313338; color: #dbdee1; }
    div[data-testid="stText"] { color: #dbdee1; }
    </style>
""", unsafe_allow_html=True)

# 2. ログイン判定（セッションがTrueなら即座にチャットページへ飛ばす）
if st.session_state.get("password_correct", False):
    st.switch_page("pages/chat.py")

# 3. ログイン画面の表示（ここはログインしていない時だけ実行される）
st.title("🔐 M25-Chat Login")

# 入力欄はここに「1回だけ」書く
u_input = st.text_input("名前（Hide or Maki）", key="username_input")
p_input = st.text_input("パスワード", type="password", key="password_input")

if st.button("ログイン"):
    # 判定ロジック
    if u_input.strip().capitalize() in ["Hide", "Maki"] and p_input == st.secrets["PASSWORD"]:
        st.session_state["password_correct"] = True
        st.session_state["username"] = u_input.strip().capitalize()
        st.rerun() # 自分を再起動させて、上の st.switch_page を発動させる
    else:
        # エラーメッセージだけを出す
        st.error("😕 名前かパスワードが違います")
