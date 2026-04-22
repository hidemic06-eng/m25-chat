import streamlit as st

# ページ設定
st.set_page_config(page_title="M25-Login", page_icon="🔒")

# --- CSSで背景色をチャット側に合わせる ---
st.markdown("""
    <style>
    .stApp { background-color: #313338; color: #dbdee1; }
    div[data-testid="stText"] { color: #dbdee1; }
    </style>
""", unsafe_allow_html=True)

def check_password():
    """パスワードが正しいかチェックし、結果をセッションに保存する"""
    def password_entered():
        # ユーザー名の判定（HideまたはMaki）
        input_user = st.session_state["username_input"].strip().capitalize()
        input_pass = st.session_state["password_input"]

        if input_user in ["Hide", "Maki"] and input_pass == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            st.session_state["username"] = input_user
            del st.session_state["password_input"]  # セキュリティのため削除
            del st.session_state["username_input"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 初回表示
        st.title("🔐 M25-Chat Login")
        st.text_input("名前（Hide or Maki）", key="username_input")
        st.text_input("パスワード", type="password", key="password_input", on_change=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        # パスワード間違い
        st.title("🔐 M25-Chat Login")
        st.text_input("名前（Hide or Maki）", key="username_input")
        st.text_input("パスワード", type="password", key="password_input", on_change=password_entered)
        st.error("😕 名前かパスワードが違います")
        return False
    else:
        # ログイン成功
        return True

if check_password():
    # ログイン成功時、自動でチャット画面に切り替える
    st.success(f"ようこそ {st.session_state['username']} さん！")
    if st.button("チャットを開く"):
        st.switch_page("pages/chat.py")
    
    # ログイン直後に自動で遷移させたい場合はこちら
    st.switch_page("pages/chat.py")
