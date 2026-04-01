import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import random

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
    
    @keyframes fall {{
        0% {{ transform: translateY(-20vh) rotate(0deg); opacity: 0; }}
        10% {{ opacity: 1; }}
        90% {{ opacity: 1; }}
        100% {{ transform: translateY(110vh) rotate(720deg); opacity: 0; }}
    }}
    .falling-emoji {{
        position: fixed;
        top: -10%;
        animation: fall 5s linear forwards;
        z-index: 9999;
        pointer-events: none;
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

if "last_effect_id" not in st.session_state:
    st.session_state["last_effect_id"] = None

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

# --- 8. 表示 & 演出の判定 ---
try:
    res = supabase.table(table_name).select("*").order("created_at", desc=True).range(st.session_state["page_offset"], st.session_state["page_offset"] + 19).execute()
    messages = res.data[::-1]
    
    if messages and st.session_state["page_offset"] == 0:
        latest_msg = messages[-1]
        msg_id = latest_msg.get("id")
        msg_body = latest_msg["message_body"]
        sender = latest_msg["sender_name"]
        
        if msg_id != st.session_state["last_effect_id"]:
            if any(word in msg_body for word in ["おはよう", "おはよー", "おはよ"]):
                st.toast(f"{sender}さん、おはよう！☀️", icon="☀️")
            elif any(word in msg_body for word in ["大好き", "愛してる"]):
                st.toast(f"{sender}さんから愛が届きました！", icon="❤️")
            elif any(word in msg_body for word in ["ありがとう", "感謝"]):
                st.toast(f"{sender}さんが感謝しています", icon="✨")

            if any(word in msg_body for word in ["おめでとう", "祝", "記念日", "誕生日"]):
                st.balloons()
            if any(word in msg_body for word in ["雪", "寒い", "冬", "スキー"]):
                st.snow()

            emoji = None
            if any(word in msg_body for word in ["大好き", "ありがとう", "感謝", "愛してる"]):
                emoji = "❤️"
            elif any(word in msg_body for word in ["お疲れ様", "おつかれさま", "お疲れさま", "ちょい飲み", "ちょい呑み"]):
                emoji = "🍺"
            elif "おにぎり" in msg_body:
                emoji = "🍙"
            elif any(word in msg_body for word in ["バドミントン", "練習", "試合"]):
                emoji = "🏸"
            elif any(word in msg_body for word in ["ラーメン", "山岡家", "お腹すいた"]):
                emoji = "🍜"

            if emoji:
                effect_html = ""
                for i in range(25):
                    left = random.randint(0, 95)
                    size = random.uniform(1.5, 4.0)
                    delay = random.uniform(0.0, 3.0)
                    duration = random.uniform(4.0, 7.0)
                    effect_html += f'<div class="falling-emoji" style="left:{left}%; font-size:{size}rem; animation-delay:{delay}s; animation-duration:{duration}s;">{emoji}</div>'
                st.markdown(effect_html, unsafe_allow_html=True)

            st.session_state["last_effect_id"] = msg_id

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
except Exception as e:
    st.error(f"表示エラー: {e}")

# --- 9. 送信 ---
prompt = st.chat_input(input_placeholder)
if prompt:
    try:
        supabase.table(table_name).insert({"sender_name": current_user_raw, "message_body": prompt}).execute()
        st.session_state["page_offset"] = 0
        st.rerun()
    except Exception as e:
        st.error(f"送信エラー: {e}")

# --- 10. スクロール ---
if st.session_state["page_offset"] == 0:
    components.html('<script>window.parent.document.querySelector(".main").scrollTo(0, 99999);</script>', height=0)
