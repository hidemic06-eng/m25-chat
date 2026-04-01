import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# --- 1. アプリの基本設定 ---
st.set_page_config(page_title="M25", page_icon="💬", layout="wide")

# --- 2. デザイン設定 (CSS) ---
# Discord風のダークテーマと、スマホ向けのレイアウト調整
st.markdown("""
    <style>
    /* 全体の背景色と文字色をダークモードに設定 */
    .stApp { background-color: #313338; color: #dbdee1; }
    
    /* 標準のヘッダーやフッターを隠してアプリ感を出す */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="bundle-viewer-container"] {display: none !important;}

    /* メッセージ表示エリアの余白調整（下部にチャット入力欄のスペースを確保） */
    .block-container { 
        padding-top: 1rem; 
        padding-bottom: 80px !important; 
        max-width: 100% !important; 
    }

    /* チャットメッセージの見た目（吹き出し風）の設定 */
    .chat-row { display: flex; flex-direction: column; margin-bottom: 16px; width: 100%; }
    .chat-header { display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; font-size: 0.85rem; }
    .message-text { font-size: 1.05rem; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; max-width: 85%; }
    
    /* 左右の寄せ（自分と相手で切り替え） */
    .align-right { align-items: flex-end; text-align: right; }
    .align-left { align-items: flex-start; text-align: left; }
    
    /* 名前ごとの色分け */
    .name-maki { color: #ffa657 !important; font-weight: bold; }
    .name-hide { color: #58a6ff !important; font-weight: bold; }
    .timestamp { color: #949ba4; font-size: 0.75rem; }
    .text-content { color: #e6edf3; }
    
    /* 入力欄の余白微調整 */
    div[data-testid="stChatInput"] { padding-bottom: 0px !important; }

    /* ページめくりボタンを押しやすいサイズに */
    .stButton > button {
        height: 30px !important;
        padding: 0 10px !important;
        font-size: 0.8rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 認証機能 (簡易パスワードゲート) ---
if "password_correct" not in st.session_state:
    st.write("🔒 Enter Password")
    # type="password" を使うことで伏せ字にし、ブラウザの自動補完（過去の入力履歴）も防止
    pw = st.text_input("Password", type="password", key="final_stable_login")

    # パスワードが一致したらセッションにフラグを立てて再読み込み
    if pw == "05250206":
        st.session_state["password_correct"] = True
        st.rerun()
    # 8文字以上入力されて間違っている場合のみエラーを表示
    elif len(pw) >= 8:
        st.error("❌")
    
    st.stop() # 認証されるまでこれ以降のコードは実行しない

# --- 4. ページ管理設定 ---
# 過去ログを遡るためのオフセット値を管理
if "page_offset" not in st.session_state:
    st.session_state["page_offset"] = 0

# --- 5. データベース(Supabase)接続設定 ---
# 【重要】環境に合わせてテーブル名を切り替える仕掛け
# Secretsに TABLE_NAME の設定があればそれを使い、なければ本番用の "messages" を使用する
table_name = st.secrets.get("TABLE_NAME", "messages")

# URLからユーザー名を取得（?user=Maki など）
query_params = st.query_params
current_user_raw = query_params.get("user", "Hide")
current_user_upper = current_user_raw.upper()

# Supabaseクライアントの初期化
supabase = create_client("https://kvqbwknrsdasoipttkpr.supabase.co", "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT")

# --- 6. 画面上部の操作パネル ---
st.title("💬 M25-Chat")
# 自動更新のON/OFF切り替え
auto_update = st.toggle("自動更新(5s)", value=True)

# 最新ページを表示している時だけ5秒おきにリフレッシュを実行
if auto_update and st.session_state["page_offset"] == 0:
    st_autorefresh(interval=5000, key="chat_ref")

st.divider()

# --- 7. ページ切り替えナビゲーション ---
col_prev, col_page, col_next = st.columns([1, 2, 1])
with col_prev:
    if st.button("⬅️ 前の20件"):
        st.session_state["page_offset"] += 20
        st.rerun()
with col_page:
    # 現在表示中の範囲を計算して表示
    current_range = f"{st.session_state['page_offset'] + 1}〜{st.session_state['page_offset'] + 20}件目"
    st.write(f"<div style='text-align:center; font-size:0.8rem; color:#949ba4;'>{current_range}</div>", unsafe_allow_html=True)
with col_next:
    # 最新ページより先にいかないよう制御
    if st.session_state["page_offset"] >= 20:
        if st.button("次の20件 ➡️"):
            st.session_state["page_offset"] -= 20
            st.rerun()
    else:
        st.button("最新です", disabled=True)

# --- 8. メッセージ表示処理 ---
try:
    # 指定されたテーブルから最新の20件を取得
    res = supabase.table(table_name) \
        .select("*") \
        .order("created_at", desc=True) \
        .range(st.session_state["page_offset"], st.session_state["page_offset"] + 19) \
        .execute()
    
    # 取得したデータは「新しい順」なので、チャット表示用に「古い順」に並び替える
    messages = res.data[::-1]

    for m in messages:
        sender_name = m['sender_name']
        s_up = sender_name.upper()
        
        # 自分が送ったメッセージか相手かによって、左右の寄せと名前の色を切り替える
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
except Exception as e:
    # エラー時は何も表示しない（空の状態を維持）
    st.empty()

# --- 9. メッセージ入力・送信処理 ---
prompt = st.chat_input("メッセージを入力...")
if prompt:
    # Supabaseに新しいメッセージを保存
    supabase.table(table_name).insert({"sender_name": current_user_raw, "message_body": prompt}).execute()
    # 送信後は強制的に最新ページ（offset=0）に戻して再読み込み
    st.session_state["page_offset"] = 0
    st.rerun()

# --- 10. スクロール制御 (JavaScript) ---
# 最新メッセージを表示しているときのみ、画面の最下部まで自動スクロールさせる
if st.session_state["page_offset"] == 0:
    components.html(
        """<script>
        window.parent.document.querySelector(".main").scrollTo(0, 99999);
        </script>""", height=0
    )
