import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
from datetime import datetime, timedelta

# --- 1. アプリの基本設定 ---
st.set_page_config(page_title="M25", page_icon="💬", layout="wide")

# --- 2. データベース(Supabase)接続設定 ---
table_name = st.secrets.get("TABLE_NAME", "messages")

# --- 3. デザイン設定 ---
app_bg_color = "#313338" 
text_main_color = "#dbdee1"
sub_text_color = "#949ba4"

if table_name == "messages_test":
    status_label = " 🧪 TEST"
    input_placeholder = "テストメッセージを入力..."
else:
    status_label = ""
    input_placeholder = "メッセージを入力..."

st.markdown(f"""
    <style>
    .stApp {{ background-color: {app_bg_color}; color: {text_main_color}; }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    .stAppDeployButton {{display:none;}}
    [data-testid="bundle-viewer-container"] {{display: none !important;}}
    .block-container {{ padding-top: 1rem; padding-bottom: 80px !important; max-width: 100% !important; }}
    .chat-row {{ display: flex; flex-direction: column; margin-bottom: 16px; width: 100%; }}
    .chat-header {{ display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; font-size: 0.85rem; }}
    .message-text {{ font-size: 1.18rem; line-height: 1.5; font-weight: 450; white-space: pre-wrap; word-wrap: break-word; color: {text_main_color} !important; }}
    .align-right {{ align-items: flex-end; text-align: right; }}
    .align-left {{ align-items: flex-start; text-align: left; }}
    .name-maki {{ color: #ffa657 !important; font-weight: bold; }}
    .name-hide {{ color: #58a6ff !important; font-weight: bold; }}
    .timestamp {{ color: {sub_text_color}; font-size: 0.75rem; }}
    
    /* ハートのアニメーション設定 */
    @keyframes hearts {{
        0% {{ transform: translateY(0) rotate(0deg); opacity: 1; }}
        100% {{ transform: translateY(-100vh) rotate(360deg); opacity: 0; }}
    }}
    .heart {{
        position: fixed; bottom: -10%; font-size: 2rem;
        animation: hearts 4s linear forwards;
        z-index: 9999; pointer-events: none;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 4. 認証機能 ---
if "password_correct" not in st.session_state:
    st.write("🔒 Enter Password")
    pw = st.text_input("Password", type="password", key="login")
    if pw == "05250206":
        st.session_state["password_correct"] = True
        st.rerun()
    st.stop()

# --- 5. 設定 ---
if "page_offset" not in st.session_state:
    st.session_state["page_offset"] = 0

if "is_sending" not in st.session_state:
    st.session_state["is_sending"] = False

query_params = st.query_params
current_user_raw = query_params.get("user", "Hide")
current_user_upper = current_user_raw.upper()
supabase = create_client("https://kvqbwknrsdasoipttkpr.supabase.co", "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT")

# --- 6. ヘッダー ---
st.title(f"💬 M25-Chat{status_label}")
if table_name == "messages_test":
    st.info("⚠️ 現在は【テスト環境】です。投稿はMakiちゃんには届きません。")

auto_update = st.toggle("自動更新(5s)", value=True)
if auto_update and st.session_state["page_offset"] == 0:
    st_autorefresh(interval=5000, key="chat_ref")
st.divider()

# --- 7. ナビゲーション ---
col_prev, col_page, col_next = st.columns([1, 2, 1])
with col_prev:
    if st.button("⬅️ 前の20件"):
        st.session_state["page_offset"] += 20
        st.rerun()
with col_page:
    st.write(f"<div style='text-align:center; font-size:0.8rem; color:{sub_text_color};'>{st.session_state['page_offset']+1}〜件目</div>", unsafe_allow_html=True)
with col_next:
    if st.session_state["page_offset"] >= 20:
        if st.button("次の20件 ➡️"):
            st.session_state["page_offset"] -= 20
            st.rerun()

# --- 8. 表示 & ハートの判定 ---
try:
    res = supabase.table(table_name).select("*").order("created_at", desc=True).range(st.session_state["page_offset"], st.session_state["page_offset"] + 19).execute()
    messages = res.data[::-1]
    
    # 【追加機能】最新のメッセージにキーワードが含まれているかチェック
    if messages:
        latest_msg = messages[-1]["message_body"]
        if any(word in latest_msg for word in ["大好き", "ありがとう", "感謝"]):
            # ハートを降らせるJavaScriptを生成
            heart_js = ""
            for i in range(15):
                left = i * 7
                delay = i * 0.2
                heart_js += f'<div class="heart" style="left:{left}%; animation-delay:{delay}s;">❤️</div>'
            st.markdown(heart_js, unsafe_allow_html=True)

    for m in messages:
        utc_time = datetime.fromisoformat(m['created_at'].replace('Z', '+00:00'))
        jst_time = utc_time + timedelta(hours=9)
        time_display = jst_time.strftime('%H:%M')

        s_up = m['sender_name'].upper()
        align = "align-right" if s_up == current_user_upper else "align-left"
        h_style = "flex-direction: row-reverse;" if s_up == current_user_upper else ""
        n_class = "name-maki" if "MAKI" in s_up else "name-hide" if "HIDE" in s_up else ""
        
        st.markdown(f"""
            <div class="chat-row {align}">
                <div class="chat-header" style="{h_style}">
                    <span class="{n_class}">{m["sender_name"]}</span>
                    <span class="timestamp">{time_display}</span>
                </div>
                <div class="message-text">{m["message_body"]}</div>
            </div>
        """, unsafe_allow_html=True)
except:
    st.empty()

# --- 9. 送信 ---
prompt = st.chat_input(input_placeholder)
if prompt and not st.session_state["is_sending"]:
    st.session_state["is_sending"] = True
    try:
        supabase.table(table_name).insert({"sender_name": current_user_raw, "message_body": prompt}).execute()
        st.session_state["is_sending"] = False
        st.session_state["page_offset"] = 0
        st.rerun()
    except Exception as e:
        st.session_state["is_sending"] = False
        st.error(f"送信エラー: {e}")

# --- 10. スクロール ---
if st.session_state["page_offset"] == 0:
    components.html('<script>window.parent.document.querySelector(".main").scrollTo(0, 99999);</script>', height=0)