import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import random
import re

# --- 1. アプリの基本設定 ---
st.set_page_config(page_title="M25", page_icon="💬", layout="wide")

# 【魔法のスクリプト：PWA設定 ＆ 名前の自動復元】
# iPhoneのアイコンから起動してURLが削られていても、記憶から「?user=...」を復活させます
components.html("""
<script>
    // 1. PWA設定
    const metaApp = document.createElement('meta');
    metaApp.name = "apple-mobile-web-app-capable";
    metaApp.content = "yes";
    window.parent.document.getElementsByTagName('head')[0].appendChild(metaApp);

    const metaStatus = document.createElement('meta');
    metaStatus.name = "apple-mobile-web-app-status-bar-style";
    metaStatus.content = "black-translucent";
    window.parent.document.getElementsByTagName('head')[0].appendChild(metaStatus);

    const linkIcon = window.parent.document.createElement('link');
    linkIcon.rel = 'apple-touch-icon';
    linkIcon.href = 'https://cdn-icons-png.flaticon.com/512/5968/5968756.png'; 
    window.parent.document.getElementsByTagName('head')[0].appendChild(linkIcon);

    // 2. 名前の復元ロジック
    const urlParams = new URLSearchParams(window.parent.location.search);
    const userFromUrl = urlParams.get('user');
    const savedUser = localStorage.getItem('m25_persistent_user');

    if (!userFromUrl && savedUser) {
        // アイコンから起動して名前が消えている場合、記憶を使ってリロード
        const newUrl = window.parent.location.origin + window.parent.location.pathname + "?user=" + savedUser;
        window.parent.location.href = newUrl;
    } else if (userFromUrl) {
        // URLに名前がある場合は、最新の状態を記憶に刻む
        localStorage.setItem('m25_persistent_user', userFromUrl);
    }
</script>
""", height=0)

# --- 2. データベース(Supabase)接続設定 ---
table_name = st.secrets.get("TABLE_NAME", "messages")
supabase = create_client("https://kvqbwknrsdasoipttkpr.supabase.co", "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT")

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
    @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;700&display=swap');

    .stApp {{ background-color: {app_bg_color}; color: {text_main_color}; font-family: 'M PLUS Rounded 1c', sans-serif !important; }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    .stAppDeployButton {{display:none;}}
    .block-container {{ padding-top: 1rem; padding-bottom: 80px !important; max-width: 100% !important; }}
    
    .chat-row {{ display: flex; flex-direction: column; margin-bottom: 16px; width: 100%; }}
    .message-text {{ font-family: 'M PLUS Rounded 1c', sans-serif !important; font-feature-settings: "palt" 1; font-size: 1.15rem; line-height: 1.35; font-weight: 500 !important; letter-spacing: -0.04rem; max-width: 80%; white-space: pre-wrap; word-wrap: break-word; color: {text_main_color} !important; }}
    .align-right {{ align-items: flex-end; text-align: right; }}
    .align-left {{ align-items: flex-start; text-align: left; }}
    .chat-header {{ display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; font-size: 0.85rem; }}
    .name-maki {{ color: #ffa657 !important; font-weight: 700; }}
    .name-hide {{ color: #58a6ff !important; font-weight: 700; }}
    .timestamp {{ color: {sub_text_color}; font-size: 0.75rem; }}
    
    /* 演出アニメーション */
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

# --- 4. 認証 ＆ ユーザー選択 ---
query_params = st.query_params
initial_user = query_params.get("user", "Hide")

if "password_correct" not in st.session_state:
    st.write("🔒 Login")
    # ここで名前を選択させることでlocalStorageに保存します
    selected_user = st.radio("利用者はどちらですか？", ["Hide", "Maki"], index=0 if initial_user.upper() == "HIDE" else 1)
    pw = st.text_input("Password", type="password", key="login")
    if st.button("ログイン"):
        if pw == "05250206":
            # JSで記憶に刻み込み、URLを書き換えてリロード！
            components.html(f"""
            <script>
                localStorage.setItem('m25_persistent_user', '{selected_user}');
                window.parent.location.href = window.parent.location.origin + window.parent.location.pathname + "?user={selected_user}";
            </script>
            """, height=0)
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    st.stop()

# --- 5. ユーザー確定 ---
current_user_raw = query_params.get("user", "Hide")
current_user_upper = current_user_raw.upper()

if "page_offset" not in st.session_state: st.session_state["page_offset"] = 0
if "last_effect_id" not in st.session_state: st.session_state["last_effect_id"] = None

# --- 6. ヘッダー & サイドバー ---
st.title(f"💬 M25-Chat ({current_user_raw}){status_label}")
with st.sidebar:
    st.markdown("### ⚙️ 端末設定")
    if st.button("このスマホを Maki 用に固定"):
        components.html("<script>localStorage.setItem('m25_persistent_user', 'Maki'); window.parent.location.href = window.parent.location.origin + window.parent.location.pathname + '?user=Maki';</script>")
    if st.button("このスマホを Hide 用に固定"):
        components.html("<script>localStorage.setItem('m25_persistent_user', 'Hide'); window.parent.location.href = window.parent.location.origin + window.parent.location.pathname + '?user=Hide';</script>")
    st.divider()
    auto_update = st.toggle("自動更新(8s)", value=True)

if auto_update and st.session_state["page_offset"] == 0:
    st_autorefresh(interval=8000, key="chat_ref")

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
        msg_id, msg_body = latest_msg.get("id"), latest_msg["message_body"]
        
        if msg_id != st.session_state["last_effect_id"]:
            emoji_in_text = re.findall(r'[\U00010000-\U0010ffff]', msg_body)
            
            # 昇る演出判定（キーワード完全復活）
            priority_emoji = None
            if any(w in msg_body for w in ["好き", "ありがとう", "感謝", "ラブラブ"]): priority_emoji = "❤️"
            elif any(w in msg_body for w in ["大好き", "愛してる"]): priority_emoji = "💘"
            elif any(w in msg_body for w in ["お疲れ", "ビール", "酒", "乾杯"]): priority_emoji = "🍺"
            elif "おにぎり" in msg_body: priority_emoji = "🍙"
            elif any(w in msg_body for w in ["バドミントン", "練習", "試合"]): priority_emoji = "🏸"
            elif any(w in msg_body for w in ["ラーメン", "山岡家"]): priority_emoji = "🍜"
            elif any(w in msg_body for w in ["野菜", "サラダ", "レタス"]): priority_emoji = "🥬"
            elif any(w in msg_body for w in ["おやすみ", "眠い", "寝る"]): priority_emoji = "💤"
            elif any(w in msg_body for w in ["綺麗", "きれい", "すごい", "最高"]): priority_emoji = "✨"
            elif any(w in msg_body for w in ["コーヒー", "カフェ", "休憩"]): priority_emoji = "☕️"
            elif "ドライブ" in msg_body: priority_emoji = "🚗"
            elif any(w in msg_body for w in ["花見", "さくら", "桜"]): priority_emoji = "🌸"
            elif any(w in msg_body for w in ["楽しみ", "ルンルン", "うれしい"]): priority_emoji = "🎶"
            elif any(w in msg_body for w in ["ケーキ", "スイーツ"]): priority_emoji = "🍰"
            elif any(w in msg_body for w in ["幸せ", "しあわせ", "ハッピー"]): priority_emoji = "🍀"

            if priority_emoji:
                html = '<div class="rising-emoji">'
                for _ in range(25):
                    l, s = random.randint(5, 95), random.uniform(2.5, 4.5)
                    d, dur = random.uniform(0, 0.5), random.uniform(5.5, 6.5)
                    html += f'<div class="emoji-item" style="left:{l}%; font-size:{s}rem; animation-delay:{d}s; animation-duration:{dur}s;">{priority_emoji}</div>'
                st.markdown(html + '</div>', unsafe_allow_html=True)
            elif emoji_in_text:
                target = emoji_in_text[-1]
                side = random.choice(["left", "right"])
                anim = "peek-left" if side == "left" else "peek-right"
                st.markdown(f'<div class="peek-item" style="{side}:-100px; top:40%; animation:{anim} 3.5s forwards;">{target}</div>', unsafe_allow_html=True)

            # 画面全体アクション
            if any(w in msg_body for w in ["おめでとう", "祝", "記念日", "誕生日", "やったー"]): st.balloons()
            if any(w in msg_body for w in ["雪", "寒い", "冬"]): st.snow()
            
            if any(w in msg_body for w in ["こら", "起きて", "え！", "びっくり", "地震", "怒"]):
                components.html('<script>window.parent.document.querySelector(".stApp").classList.add("shake-screen"); setTimeout(() => { window.parent.document.querySelector(".stApp").classList.remove("shake-screen"); }, 2000);</script>', height=0)
            if any(w in msg_body for w in ["さみしい", "淋しい", "悲しい", "疲れた"]):
                components.html('<script>window.parent.document.querySelector(".stApp").classList.add("mood-dark"); setTimeout(() => { window.parent.document.querySelector(".stApp").classList.remove("mood-dark"); }, 3500);</script>', height=0)
            if any(w in msg_body for w in ["マジで", "えー", "正解", "おー"]):
                components.html('<script>window.parent.document.querySelector(".stApp").classList.add("bounce-screen"); setTimeout(() => { window.parent.document.querySelector(".stApp").classList.remove("bounce-screen"); }, 1000);</script>', height=0)

            st.session_state["last_effect_id"] = msg_id

    # チャット表示
    for m in messages:
        utc = datetime.fromisoformat(m['created_at'].replace('Z', '+00:00'))
        jst = (utc + timedelta(hours=9)).strftime('%H:%M')
        s_up = m['sender_name'].upper()
        align = "align-right" if s_up == current_user_upper else "align-left"
        h_style = "flex-direction: row-reverse;" if s_up == current_user_upper else ""
        n_class = "name-maki" if "MAKI" in s_up else "name-hide" if "HIDE" in s_up else ""
        st.markdown(f'<div class="chat-row {align}"><div class="chat-header" style="{h_style}"><span class="{n_class}">{m["sender_name"]}</span><span class="timestamp">{jst}</span></div><div class="message-text">{m["message_body"]}</div></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"表示エラー: {e}")

# --- 9. 送信エリア ---
prompt = st.chat_input(input_placeholder)
if prompt:
    supabase.table(table_name).insert({"sender_name": current_user_raw, "message_body": prompt}).execute()
    st.session_state["page_offset"] = 0
    st.rerun()

# --- 10. 自動スクロール ---
if st.session_state["page_offset"] == 0:
    components.html('<script>window.parent.document.querySelector(".main").scrollTo(0, 99999);</script>', height=0)