import streamlit as st
from supabase import create_client

# --- 2. 設定と接続 (set_page_configは最初に行う必要があります) ---
st.set_page_config(page_title="M25", page_icon="💬", layout="wide")

# --- メニューと猫アイコンを非表示にする設定 ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)


# --- 1. パスワード認証機能 ---
def check_password():
    """正しいパスワードが入力されたら True を返す"""
    def password_entered():
        # パスワード設定
        if st.session_state["password"] == "05250206":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("パスワードを入力してください", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("パスワードが違います。再入力してください", type="password", on_change=password_entered, key="password")
        st.error("😕 パスワードが正しくありません")
        return False
    return True

if not check_password():
    st.stop()

# --- 2. URLパラメータから名前を取得 ---
# URLの末尾に ?user=HIDE や ?user=MAKI があればそれを読み込む
query_params = st.query_params
user_param = query_params.get("user", "HIDE") # 指定がない場合はデフォルトでHIDE

# --- 3. Supabaseの接続情報 ---
SUPABASE_URL = "https://kvqbwknrsdasoipttkpr.supabase.co"
SUPABASE_KEY = "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 画面のタイトル設定
st.set_page_config(page_title="M25-Chat", page_icon="💬")
st.title("💬 M25-Chat")
st.caption("HIDE-Lab プロジェクト第2弾: クラウドチャット")

# --- 4. メッセージの送信フォーム ---
with st.form("send_message", clear_on_submit=True):
    st.write("新しいメッセージを投稿")
    # URLパラメータから取得した名前を初期値に設定
    name = st.text_input("名前", value=user_param)
    msg = st.text_area("内容を入力してください...")
    submit = st.form_submit_button("送信する")

    if submit and msg:
        data = {"sender_name": name, "message_body": msg}
        try:
            supabase.table("messages").insert(data).execute()
            st.success("送信完了！")
            # 送信後、即座に画面を更新して履歴を反映させる
            st.rerun()
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# --- 5. 履歴の表示機能 ---
st.write("---")
st.subheader("📝 メッセージ履歴")

try:
    res = supabase.table("messages").select("*").order("created_at", desc=True).execute()
    
    for m in res.data:
        with st.container():
            # 名前と時間を表示
            st.write(f"**{m['sender_name']}** <small style='color:gray;'>({m['created_at'][:16]})</small>", unsafe_allow_html=True)
            # メッセージ本文を枠付き（info）で表示
            st.info(m['message_body'])
except Exception as e:
    st.write("履歴の読み込み中...")
