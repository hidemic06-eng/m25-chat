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
    /* M PLUS Rounded 1c の読み込み */
    @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;700&display=swap');

    .stApp {{ 
        background-color: {app_bg_color}; 
        color: {text_main_color}; 
        font-family: 'M PLUS Rounded 1c', sans-serif !important; 
    }}
    
    /* 強力な非表示設定（王冠、メニュー、ヘッダー） */
    #MainMenu, footer, header, .stAppDeployButton, [data-testid="bundle-viewer-container"] {{
        visibility: hidden !important;
        display: none !important;
    }}
    
    .block-container {{ padding-top: 1rem; padding-bottom: 80px !important; max-width: 100% !important; }}
    
    /* レイアウト：左右の振り分け */
    .chat-row {{ display: flex; flex-direction: column; margin-bottom: 16px; width: 100%; }}
    
    .message-text {{ 
        font-family: 'M PLUS Rounded 1c', sans-serif !important;
        font-feature-settings: "palt" 1; 
        font-size: 1.15rem; 
        line-height: 1.35; 
        font-weight: 500 !important; 
        letter-spacing: -0.04rem; 
        max-width: 80%; 
        white-space: pre-wrap; 
        word-wrap: break-word; 
        color: {text_main_color} !important; 
    }}

    .stChatInput textarea {{
        font-family: 'M PLUS Rounded 1c', sans-serif !important;
    }}

    .align-right {{ align-items: flex-end; text-align: right; }}
    .align-left {{ align-items: flex-start; text-align: left; }}
    
    .chat-header {{ display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; font-size: 0.85rem; }}
    .name-maki {{ color: #ffa657 !important; font-weight: 700; }}
    .name-hide {{ color: #58a6ff !important; font-weight: 700; }}
    .timestamp {{ color: {sub_text_color}; font-size: 0.75rem; }}
    
    /* アニメーション */
    @keyframes shake {{
        0% {{ transform: translate(1px, 1px) rotate(0deg); }}
        10% {{ transform: translate(-1px, -2px) rotate(-1deg); }}
        100% {{ transform: translate(1px, 1px) rotate(0deg); }}
    }}
    .shake-screen {{ animation: shake 0.5s; animation-iteration-count: 4; }}
    @keyframes rise {{
        0% {{ transform: translateY(0); opacity: 0; }}
        5% {{ opacity: 1; }}
        100% {{ transform: translateY(-125vh) rotate(360deg); opacity: 0; }}
    }}
    .rising-emoji {{ position: fixed; bottom: -12vh; left: 0; width: 100%; height: 0; z-index: 9999; pointer-events: none; }}
    .emoji-item {{ position: absolute; animation: rise linear forwards; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. 認証機能 (セッション保持版) ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.write("🔒 Enter Password")
    pw = st.text_input("Password", type="password", key="login_pass")
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
auto_update = st.toggle("自動更新(8s)", value=True)
if auto_update and st.session_state["page_offset"] == 0:
    st_autorefresh(interval=8000, key="chat_ref")
st.divider()

# --- 7. ナビゲーション ---
col_prev, col_page, col_next = st.columns([1, 2, 1])
with col_prev:
    if st.button("⬅️ 前の20件"):
        st.session_state["page_offset"] += 20
        st.rerun()
with col_page:
    st.write(f"<div style='text-align:center; font-size:0.8rem;'>{st.session_state['page_offset']+1}〜件目</div>", unsafe_allow_html=True)
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
        
        if msg_id != st.session_state["last_effect_id"]:
            emoji = None
            if any(word in msg_body for word in ["大好き", "好き", "ありがとう", "感謝", "愛してる", "ラブラブ"]): emoji = "❤️"
            # ビール演出の復活 (キーワード追加)
            elif any(word in msg_body for word in ["お疲れ様", "おつかれさま", "お疲れ", "ちょい飲み", "ちょい呑み", "ビール", "乾杯", "酒"]): emoji = "🍺"
            elif "おにぎり" in msg_body: emoji = "🍙"
            elif any(word in msg_body for word in ["バドミントン", "練習", "試合"]): emoji = "🏸"
            elif any(word in msg_body for word in ["ラーメン", "山岡家"]): emoji = "🍜"
            elif any(word in msg_body for word in ["野菜", "サラダ", "レタス"]): emoji = "🥬"
            elif any(word in msg_body for word in ["おやすみ", "眠い", "寝る"]): emoji = "💤"
            elif any(word in msg_body for word in ["綺麗", "きれい", "すごい", "最高"]): emoji = "✨"
            elif any(word in msg_body for word in ["コーヒー", "カフェ", "休憩"]): emoji = "☕️"
            elif any(word in msg_body for word in ["ドライブ"]): emoji = "🚗"
            elif any(word in msg_body for word in ["ワイン", "ハイボール"]): emoji = "🥂"
            elif any(word in msg_body for word in ["花見", "さくら", "桜"]): emoji = "🌸"
            elif any(word in msg_body for word in ["楽しみ", "ルンルン", "うれしい"]): emoji = "🎶"
            elif any(word in msg_body for word in ["ケーキ", "スイーツ", "甘いもの"]): emoji = "🍰"
            elif any(word in msg_body for word in ["ラッキー", "幸せ", "しあわせ", "ハッピー"]): emoji = "🍀"
            elif any(word in msg_body for word in ["熊", "困った"]): emoji = "🐻"

            if any(word in msg_body for word in ["おめでとう", "祝", "記念日", "誕生日"]): st.balloons()
            if any(word in msg_body for word in ["雪", "寒い", "冬", "クリスマス"]): st.snow()
            
            if any(word in msg_body for word in ["こら", "起きて", "びっくり", "地震", "怒"]):
                components.html('<script>window.parent.document.querySelector(".stApp").classList.add("shake-screen"); setTimeout(() => { window.parent.document.querySelector(".stApp").classList.remove("shake-screen"); }, 2000);</script>', height=0)

            if emoji:
                effect_html = '<div class="rising-emoji">'
                for i in range(25):
                    left = random.randint(5, 95)
                    size = random.uniform(2.5, 4.5)
                    delay = random.uniform(0, 0.5)
                    duration = random.uniform(5.5, 6.5)
                    effect_html += f'<div class="emoji-item" style="left:{left}%; font-size:{size}rem; animation-delay:{delay}s; animation-duration:{duration}s;">{emoji}</div>'
                effect_html += '</div>'
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