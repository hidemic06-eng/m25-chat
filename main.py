import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import random
import re

# --- 1. アプリの基本設定 ---
st.set_page_config(page_title="M25", page_icon="💬", layout="wide")

# 【PWA閉じてもユーザー維持ロジック】
# 起動時にLocalStorageを確認し、保存されたユーザーがいればURLを書き換えてリロードします
components.html("""
<script>
    const savedUser = localStorage.getItem('m25_user');
    const urlParams = new URLSearchParams(window.parent.location.search);
    const currentUserParam = urlParams.get('user');

    if (currentUserParam) {
        localStorage.setItem('m25_user', currentUserParam);
    } else if (savedUser) {
        const newUrl = window.parent.location.origin + window.parent.location.pathname + '?user=' + savedUser;
        window.parent.location.href = newUrl;
    }

    const metaApp = document.createElement('meta');
    metaApp.name = "apple-mobile-web-app-capable";
    metaApp.content = "yes";
    window.parent.document.getElementsByTagName('head')[0].appendChild(metaApp);
</script>
""", height=0)

# --- 2. データベース接続設定 ---
table_name = st.secrets.get("TABLE_NAME", "messages")

# --- 3. デザイン設定 (CSS) ---
app_bg_color = "#313338"
text_main_color = "#dbdee1"
sub_text_color = "#949ba4"

status_label = " 🧪 TEST" if table_name == "messages_test" else ""
input_placeholder = "テストメッセージを入力..." if table_name == "messages_test" else "メッセージを入力..."

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;700&display=swap');
    .stApp {{ background-color: {app_bg_color}; color: {text_main_color}; font-family: 'M PLUS Rounded 1c', sans-serif !important; }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    .stAppDeployButton {{display:none;}}
    .block-container {{ padding-top: 1rem; padding-bottom: 80px !important; max-width: 100% !important; }}
    .stButton > button {{ background-color: #424549 !important; color: white !important; border: 1px solid #4f545c !important; width: 100% !important; }}
    [data-testid="stMarkdownContainer"] p {{ color: {text_main_color} !important; }}
    .chat-row {{ display: flex; flex-direction: column; margin-bottom: 16px; width: 100%; }}
    .message-text {{ 
        font-family: 'M PLUS Rounded 1c', sans-serif !important;
        font-feature-settings: "palt" 1; font-size: 1.15rem; line-height: 1.35; font-weight: 500 !important; 
        letter-spacing: -0.04rem; max-width: 80%; white-space: pre-wrap; word-wrap: break-word; 
        color: {text_main_color} !important; 
    }}
    .align-right {{ align-items: flex-end; text-align: right; }}
    .align-left {{ align-items: flex-start; text-align: left; }}
    .chat-header {{ display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; font-size: 0.85rem; }}
    .name-maki {{ color: #ffa657 !important; font-weight: 700; }}
    .name-hide {{ color: #58a6ff !important; font-weight: 700; }}
    .timestamp {{ color: {sub_text_color}; font-size: 0.75rem; }}
    
    /* 演出用アニメーション全集 */
    @keyframes rise {{ 0% {{ transform: translateY(0); opacity: 0; }} 5% {{ opacity: 1; }} 85% {{ opacity: 1; }} 100% {{ transform: translateY(-125vh) rotate(360deg); opacity: 0; }} }}
    .rising-emoji {{ position: fixed; bottom: -12vh; left: 0; width: 100%; height: 0; z-index: 9999; pointer-events: none; }}
    .emoji-item {{ position: absolute; animation: rise linear forwards; }}
    @keyframes peek-left {{ 0% {{ left: -100px; opacity: 0; }} 20% {{ left: 20px; opacity: 1; }} 80% {{ left: 20px; opacity: 1; }} 100% {{ left: -100px; opacity: 0; }} }}
    @keyframes peek-right {{ 0% {{ right: -100px; opacity: 0; }} 20% {{ right: 20px; opacity: 1; }} 80% {{ right: 20px; opacity: 1; }} 100% {{ right: -100px; opacity: 0; }} }}
    .peek-item {{ position: fixed; z-index: 9999; pointer-events: none; font-size: 4rem; }}
    @keyframes shake {{ 0% {{ transform: translate(1px, 1px) rotate(0deg); }} 10% {{ transform: translate(-1px, -2px) rotate(-1deg); }} 30% {{ transform: translate(3px, 2px) rotate(0deg); }} 100% {{ transform: translate(1px, 1px) rotate(0deg); }} }}
    .shake-screen {{ animation: shake 0.5s; animation-iteration-count: 4; }}
    @keyframes fade-dark {{ 0% {{ filter: brightness(1); }} 20% {{ filter: brightness(0.4) sepia(0.6); }} 80% {{ filter: brightness(0.4) sepia(0.6); }} 100% {{ filter: brightness(1); }} }}
    .mood-dark {{ animation: fade-dark 3.5s ease-in-out; }}
    @keyframes bounce-screen {{ 0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }} 40% {{ transform: translateY(-40px) scaleY(1.05); }} 60% {{ transform: translateY(-20px) scaleY(1.02); }} }}
    .bounce-screen {{ animation: bounce-screen 0.8s ease; }}
    @keyframes flash-white {{ 0% {{ filter: brightness(1); }} 10% {{ filter: brightness(2.5) contrast(1.2); }} 100% {{ filter: brightness(1); }} }}
    .flash-screen {{ animation: flash-white 0.6s ease-out; }}
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

# --- 5. セッション & ユーザー確定 ---
if "page_offset" not in st.session_state: st.session_state["page_offset"] = 0
if "last_effect_id" not in st.session_state: st.session_state["last_effect_id"] = None
if "show_settings" not in st.session_state: st.session_state["show_settings"] = False

# URLからユーザーを取得
url_user = st.query_params.get("user")
if url_user:
    st.session_state["current_user"] = url_user

# セッションにユーザーがいなければデフォルトはHide
if "current_user" not in st.session_state:
    st.session_state["current_user"] = "Hide"

current_user_raw = st.session_state["current_user"]
current_user_upper = current_user_raw.upper()

supabase = create_client("https://kvqbwknrsdasoipttkpr.supabase.co", "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT")

# --- 6. ヘッダー & 設定 ---
h_col1, h_col2 = st.columns([4, 1])
with h_col1:
    st.markdown(f"### 💬 M25-Chat{status_label}")
with h_col2:
    if st.button("⚙️"):
        st.session_state["show_settings"] = not st.session_state["show_settings"]

if st.session_state["show_settings"]:
    with st.container(border=True):
        st.write(f"🔧 **アプリ設定** (ログイン: {current_user_raw})")
        user_list = ["Maki", "Hide"]
        default_idx = user_list.index(current_user_raw) if current_user_raw in user_list else 1
        selected_user = st.radio("表示ユーザー切替:", user_list, index=default_idx, horizontal=True)
        
        if selected_user != current_user_raw:
            st.session_state["current_user"] = selected_user
            components.html(f"""
                <script>
                    localStorage.setItem('m25_user', '{selected_user}');
                    window.parent.location.href = window.parent.location.origin + window.parent.location.pathname + '?user={selected_user}';
                </script>
            """, height=0)
            st.rerun()
        auto_update = st.toggle("自動更新(8s)", value=True)
else:
    auto_update = True

if auto_update and st.session_state["page_offset"] == 0:
    st_autorefresh(interval=8000, key="chat_ref")
st.divider()

# --- 7. メッセージ表示 & 演出ロジック (キーワード全維持) ---
try:
    res = supabase.table(table_name).select("*").order("created_at", desc=True).range(st.session_state["page_offset"], st.session_state["page_offset"] + 19).execute()
    messages = res.data[::-1]
    
    if messages and st.session_state["page_offset"] == 0:
        latest = messages[-1]
        msg_id, msg_body = latest.get("id"), latest["message_body"]
        
        if msg_id != st.session_state["last_effect_id"]:
            emoji_in_text = re.findall(r'[\U00010000-\U0010ffff]', msg_body)
            priority_emoji = None
            
            # 【演出キーワード判定：一切省略なし】
            if any(w in msg_body for w in ["大好き", "愛してる"]): priority_emoji = "💘"
            elif any(w in msg_body for w in ["好き", "ありがとう", "感謝", "ラブラブ"]): priority_emoji = "❤️"
            elif any(w in msg_body for w in ["お疲れ様", "おつかれさま", "お疲れ", "ちょい飲み", "ちょい呑み", "ビール", "酒"]): priority_emoji = "🍺"
            elif "おにぎり" in msg_body: priority_emoji = "🍙"
            elif any(w in msg_body for w in ["バドミントン", "練習", "試合"]): priority_emoji = "🏸"
            elif any(w in msg_body for w in ["ラーメン", "山岡家"]): priority_emoji = "🍜"
            elif any(w in msg_body for w in ["野菜", "サラダ", "レタス"]): priority_emoji = "🥬"
            elif any(w in msg_body for w in ["おやすみ", "眠い", "寝る"]): priority_emoji = "💤"
            elif any(w in msg_body for w in ["綺麗", "きれい", "すごい", "最高"]): priority_emoji = "✨"
            elif any(w in msg_body for w in ["コーヒー", "カフェ", "休憩"]): priority_emoji = "☕️"
            elif any(w in msg_body for w in ["ドライブ"]): priority_emoji = "🚗"
            elif any(w in msg_body for w in ["ワイン", "ハイボール", "乾杯"]): priority_emoji = "🥂"
            elif any(w in msg_body for w in ["花見", "さくら", "桜"]): priority_emoji = "🌸"
            elif any(w in msg_body for w in ["楽しみ", "ルンルン", "うれしい"]): priority_emoji = "🎶"
            elif any(w in msg_body for w in ["ケーキ", "スイーツ", "甘いもの"]): priority_emoji = "🍰"
            elif any(w in msg_body for w in ["ラッキー", "幸せ", "しあわせ", "ハッピー"]): priority_emoji = "🍀"
            elif any(w in msg_body for w in ["熊", "困った"]): priority_emoji = "🐻"
            elif any(w in msg_body for w in ["おやつ", "プリン"]): priority_emoji = "🍮"
            elif any(w in msg_body for w in ["バーガー", "マクド", "朝マック"]): priority_emoji = "🍔"

            if priority_emoji:
                html = f'<div class="rising-emoji">'
                for i in range(25):
                    l, s = random.randint(5,95), random.uniform(2.5, 4.5)
                    d, dur = random.uniform(0, 0.5), random.uniform(5.5, 6.5)
                    html += f'<div class="emoji-item" style="left:{l}%; font-size:{s}rem; animation-delay:{d}s; animation-duration:{dur}s;">{priority_emoji}</div>'
                st.markdown(html + '</div>', unsafe_allow_html=True)
            elif emoji_in_text:
                target, peek = emoji_in_text[-1], '<div>'
                for i in range(5):
                    side, top = random.choice(["left", "right"]), random.randint(20, 80)
                    delay, duration = random.uniform(0, 2.0), random.uniform(3.0, 4.0)
                    anim = "peek-left" if side == "left" else "peek-right"
                    peek += f'<div class="peek-item" style="{side}:-100px; top:{top}%; animation:{anim} {duration}s forwards; animation-delay:{delay}s;">{target}</div>'
                st.markdown(peek + '</div>', unsafe_allow_html=True)

            if any(w in msg_body for w in ["おめでとう", "祝", "記念日", "やったー"]): st.balloons()
            if any(w in msg_body for w in ["雪", "寒い", "冬", "クリスマス"]): st.snow()
            
            # 【JavaScript特殊演出】
            if any(w in msg_body for w in ["こら", "起きて", "え！", "びっくり", "地震", "怒"]):
                components.html('<script>window.parent.document.querySelector(".stApp").classList.add("shake-screen"); setTimeout(()=>{window.parent.document.querySelector(".stApp").classList.remove("shake-screen");}, 2000);</script>', height=0)
            if any(w in msg_body for w in ["さみしい", "淋しい", "悲しい", "疲れた"]):
                components.html('<script>window.parent.document.querySelector(".stApp").classList.add("mood-dark"); setTimeout(()=>{window.parent.document.querySelector(".stApp").classList.remove("mood-dark");}, 3500);</script>', height=0)
            if any(w in msg_body for w in ["マジで", "えー", "正解", "おー"]):
                components.html('<script>window.parent.document.querySelector(".stApp").classList.add("bounce-screen"); setTimeout(()=>{window.parent.document.querySelector(".stApp").classList.remove("bounce-screen");}, 1000);</script>', height=0)
            if any(w in msg_body for w in ["びっくり", "光る", "指輪"]):
                components.html('<script>window.parent.document.querySelector(".stApp").classList.add("flash-screen"); setTimeout(()=>{window.parent.document.querySelector(".stApp").classList.remove("flash-screen");}, 600);</script>', height=0)
            st.session_state["last_effect_id"] = msg_id

    for m in messages:
        utc = datetime.fromisoformat(m['created_at'].replace('Z', '+00:00'))
        ts, s_up = (utc + timedelta(hours=9)).strftime('%H:%M'), m['sender_name'].upper()
        align = "align-right" if s_up == current_user_upper else "align-left"
        h_style = "flex-direction: row-reverse;" if s_up == current_user_upper else ""
        n_cls = "name-maki" if "MAKI" in s_up else "name-hide" if "HIDE" in s_up else ""
        st.markdown(f'<div class="chat-row {align}"><div class="chat-header" style="{h_style}"><span class="{n_cls}">{m["sender_name"]}</span><span class="timestamp">{ts}</span></div><div class="message-text">{m["message_body"]}</div></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")

# --- 8. 送信エリア ---
prompt = st.chat_input(input_placeholder)
if prompt:
    supabase.table(table_name).insert({"sender_name": current_user_raw, "message_body": prompt}).execute()
    st.session_state["page_offset"] = 0
    st.rerun()

if st.session_state["page_offset"] == 0:
    components.html('<script>window.parent.document.querySelector(".main").scrollTo(0, 99999);</script>', height=0)