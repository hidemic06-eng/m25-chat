import streamlit as st
from supabase import create_client

# --- パスワード認証機能 ---
def check_password():
    """正しいパスワードが入力されたら True を返す"""
    def password_entered():
        if st.session_state["password"] == "05250206":  # ← ここに好きなパスワードを設定！
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # セッションから削除して安全に
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 初回表示：パスワード入力欄
        st.text_input("パスワードを入力してください", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # 間違った場合：再入力
        st.text_input("パスワードが違います。再入力してください", type="password", on_change=password_entered, key="password")
        st.error("😕 パスワードが正しくありません")
        return False
    else:
        # 正解
        return True

# パスワードチェックが通らない限り、これ以降のコードは実行されない
if not check_password():
    st.stop()

# --- ここから下の既存コードはそのまま ---
# 1. Supabaseの接続情報...

# 1. Supabaseの接続情報（HIDEさんの専用キーを設定済み）
SUPABASE_URL = "https://kvqbwknrsdasoipttkpr.supabase.co"
SUPABASE_KEY = "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT"

# Supabaseクライアントの初期化
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 画面のタイトル設定
st.set_page_config(page_title="M25-Chat", page_icon="💬")
st.title("💬 M25-Chat")
st.caption("HIDE-Lab プロジェクト第2弾: クラウドチャット")

# 2. メッセージの送信フォーム
with st.form("send_message", clear_on_submit=True):
    st.write("新しいメッセージを投稿")
    name = st.text_input("名前", value="HIDE")
    msg = st.text_area("内容を入力してください...")
    submit = st.form_submit_button("送信する")

    if submit and msg:
        # データベース「messages」テーブルに保存
        data = {"sender_name": name, "message_body": msg}
        try:
            supabase.table("messages").insert(data).execute()
            st.success("送信完了！")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# 3. 履歴の表示機能
st.write("---")
st.subheader("📝 メッセージ履歴")

# データベースから最新順に取得
try:
    res = supabase.table("messages").select("*").order("created_at", desc=True).execute()
    
    for m in res.data:
        # メッセージを枠で囲んで表示
        with st.container():
            st.write(f"**{m['sender_name']}** <small style='color:gray;'>({m['created_at'][:16]})</small>", unsafe_allow_html=True)
            st.info(m['message_body'])
except Exception as e:
    st.write("履歴の読み込み待ち、またはエラーです。")