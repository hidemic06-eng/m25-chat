import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# --- 1. アプリの基本設定 ---
# デフォルトのタイトルを設定
st.set_page_config(page_title="M25", page_icon="💬", layout="wide")

# --- 2. データベース(Supabase)接続設定 ---
table_name = st.secrets.get("TABLE_NAME", "messages")

# --- 3. デザイン設定 (いつものダークモードに固定) ---
app_bg_color = "#313338"  # いつものDiscord風グレー
text_main_color = "#dbdee1"
sub_text_color = "#949ba4"

# テストラベルとプレースホルダーの設定
if table_name == "messages_test":
    status_label = " 🧪 TEST"
    input_placeholder = "テストメッセージを入力..."
else:
    status_label = ""
    input_placeholder = "メッセージを入力..."

st.markdown(f"""
    <style>
    /* 背景色と基本文字色 */
    .stApp {{ background-color: {app_bg_color}; color: {text_main_color}; }}
    
    /* 標準のヘッダーやフッターを隠す */
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    .stAppDeployButton {{display:none;}}
    [data-testid="bundle-viewer-container"] {{display: none !important;}}

    .block-container {{ 
        padding-top: 1rem; 
        padding-bottom: 80px !important; 
        max-width: 100% !important; 
    }}

    .chat-row {{ display: flex; flex-direction: column; margin-bottom: 16px; width: 100%; }}
    .chat-header {{ display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; font-size: 0.85rem; }}
    
    /* メッセージの文字サイズを維持 */
    .message-text {{ 
        font-size: 1.18rem; 
        line-height: 1.5; 
        font-weight: 450;
        white-space: pre-wrap; 
        word-wrap: break-word; 
        max-width: 85%; 
        color: {text_main_color} !important;
    }}

    .align-right {{ align-items: flex-end; text-align: right; }}
    .align-left {{ align-items: flex-start; text-align: left; }}
    .name-maki {{ color: #ffa657 !important; font-weight: bold; }}
    .name-hide {{ color: #58a6ff !important; font-weight: bold; }}
    .timestamp {{ color: {sub_text_color}; font-size: 0.75rem; }}
    
    div[data-testid="stChatInput"] {{ padding-bottom: 0px !important; }}

    .stButton > button {{
        height: 30px !important;
        padding: 0 10px !important;
        font-size: 0.8rem !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 4. 認証機能 ---
if "password_correct" not in st.session_state:
    st.write("🔒 Enter Password")
    pw = st.text_input("Password", type="password", key="final_stable_login")

    if pw == "05250206":
        st.session_state["password_correct"] = True
        st.rerun()
    elif len(pw) >= 8:
        st.error("❌")
    st.stop()

# --- 5. ページ管理・URLパラメータ ---
if "page_offset" not in st.session_state:
    st.session_state["page_offset"] = 0

query_params = st.query_params
current_user_raw = query_params.get("user", "Hide")
current_user_upper = current_user_raw.upper()

# Supabaseクライアントの初期化
supabase = create_client("https://kvqbwknrsdasoipttkpr.supabase.co", "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT")

# --- 6. 画面上部の操作パネル ---
st.title(f"💬 M25-Chat{status_label}")

if table_name == "messages_test":
    st.info("⚠️ 現在は【テスト環境】です。投稿はMakiちゃんには届きません。")

auto_update = st.toggle("自動更新(5s)", value=True)

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
    current_range = f"{st.session_state['page_offset'] + 1}〜{st.session_state['page_offset'] + 20}件目"
    st.write(f"<div style='text-align:center; font-size:0.8rem; color:{sub_text_color};'>{current_range}</div>", unsafe_allow_html=True)
with col_next:
    if st.session_state["page_offset"] >= 20:
        if st.button("次の20件 ➡️"):
            st.session_state["page_offset"] -= 20
            st.rerun()
    else:
        st.button("最新です", disabled=True)

# --- 8. メッセージ表示処理 ---
try:
    res = supabase.table(table_name) \
        .select("*") \
        .order("created_at", desc=True) \
        .range(st.session_state["page_offset"], st.session_state["page_offset"] + 19) \
        .execute()
    
    messages = res.data[::-1]

    # --- 【追加】新着判定ロジック ---
    if messages:
        latest_msg = messages[-1]
        # セッションに「最後に見たID」を保存
        if "last_seen_id" not in st.session_state:
            st.session_state["last_seen_id"] = latest_msg['id']
        
        # 新しいメッセージがあり、かつ送信者が自分ではない場合
        if latest_msg['id'] > st.session_state['last_seen_id'] and latest_msg['sender_name'] != current_user_raw:
            # ブラウザのタブタイトルを「新着あり」に変更するスクリプトを発動させる準備
            new_msg_flag = True
        else:
            new_msg_flag = False

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
                <div class="message-text">{m['message_body']}</div>
            </div>
        """, unsafe_allow_html=True)
except Exception as e:
    st.empty()

# --- 9. メッセージ入力・送信処理 ---
prompt = st.chat_input(input_placeholder)
if prompt:
    res = supabase.table(table_name).insert({"sender_name": current_user_raw, "message_body": prompt}).execute()
    # 自分が送信した時は、そのIDを「既読」とする
    if res.data:
        st.session_state["last_seen_id"] = res.data[0]['id']
    st.session_state["page_offset"] = 0
    st.rerun()

# --- 10. スクロール制御 & 新着リセット (JavaScript) ---
if st.session_state["page_offset"] == 0:
    # 新着があればタイトルを✨に、スクロールしたら💬に戻す
    title_script = 'window.parent.document.title = "✨ 新着あり！ M25";' if 'new_msg_flag' in locals() and new_msg_flag else 'window.parent.document.title = "💬 M25";'
    
    components.html(
        f"""<script>
        // 一番下までスクロール
        window.parent.document.querySelector(".main").scrollTo(0, 99999);
        // タイトルの制御
        {title_script}
        </script>""", height=0
    )
    
    # 画面を表示（スクロール実行）したので、最後に見たIDを最新に更新
    if 'messages' in locals() and messages:
        st.session_state["last_seen_id"] = messages[-1]['id']