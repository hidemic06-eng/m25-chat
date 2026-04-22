import streamlit as st

# 1. ページ設定（一番最初に1回だけ）
st.set_page_config(page_title="M25-Login", page_icon="🔒")

# --- CSS（文字色と背景を強制固定） ---
st.markdown("""
    <style>
    .stApp { background-color: #313338; color: #dbdee1; }
    label { color: #ffffff !important; }
    input { background-color: #40444b !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# 2. 状態の初期化
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

# 3. ログイン済みなら即遷移して終了
if st.session_state["password_correct"]:
    st.switch_page("pages/chat.py")
    st.stop()

# 4. ログイン画面（ここが1回しか通らないようにします）
st.title("🔐 M25-Chat Login")

# 入力欄を配置（ボタンなし・Enterキーで確定）
u_input = st.text_input("名前（Hide or Maki）", key="user_field")
p_input = st.text_input("パスワード", type="password", key="pass_field")

# パスワードが入力された（Enterが押された）瞬間に判定
if p_input:
    u_val = u_input.strip().capitalize()
    if u_val in ["Hide", "Maki"] and p_input == st.secrets["PASSWORD"]:
        st.session_state["password_correct"] = True
        st.session_state["username"] = u_val
        st.rerun() # 成功したら即座に再起動して上の switch_page を発動
    else:
        st.error("😕 名前かパスワードが違います")
