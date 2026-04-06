import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import random
import re  # 正規表現ライブラリを追加（絵文字抽出用）

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
    @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;700&display=swap');

    .stApp {{ 
        background-color: {app_bg_color}; 
        color: {text_main_color}; 
        font-family: 'M PLUS Rounded 1c', sans-serif !important; 
    }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    .stAppDeployButton {{display:none;}}
    [data-testid="bundle-viewer-container"] {{display: none !important;}}
    .block-container {{ padding-top: 1rem; padding-bottom: 80px !important; max-width: 100% !important; }}
    
    /* ボタンの色を固定（ライトモード対策） */
    .stButton > button {{
        background-color: #424549 !important;
        color: white !important;
        border: 1px solid #4f545c !important;
    }}

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
        padding: 0; 
    }}

    /* 入力エリアのフォント設定 */
    .stChatInput textarea {{
        font-family: 'M PLUS Rounded 1c', sans-serif !important;
    }}

    .align-right {{ align-items: flex-end; text-align: right; }}
    .align-left {{ align-items: flex-start; text-align: left; }}
    
    .chat-header {{ display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; font-size: 0.85rem; }}
    .name-maki {{ color: #ffa657 !important; font-weight: 700; }}
    .name-hide {{ color: #58a6ff !important; font-weight: 700; }}
    .timestamp {{ color: {sub_text_color}; font-size: 0.75rem; }}
    
    /* --- 演出用アニメーション定義 --- */
    
    /* A. 昇る演出 */
    @keyframes rise {{
        0% {{ transform: translateY(0); opacity: 0; }}
        5% {{ opacity: 1; }}
        85% {{ opacity: 1; }}
        100% {{ transform: translateY(-125vh) rotate(360deg); opacity: 0; }}
    }}
    .rising-emoji {{ position: fixed; bottom: -12vh; left: 0; width: 100%; height: 0; z-index: 9999; pointer-events: none; }}
    .emoji-item {{ position: absolute; animation: rise linear forwards; }}

    /* B. ひょっこり演出 */
    @keyframes peek-left {{
        0% {{ left: -100px; opacity: 0; }}
        20% {{ left: 20px; opacity: 1; }}
        80% {{ left: 20px; opacity: 1; }}
        100% {{ left: -100px; opacity: 0; }}
    }}
    @keyframes peek-right {{
        0% {{ right: -100px; opacity: 0; }}
        20% {{ right: 20px; opacity: 1; }}
        80% {{ right: 20px; opacity: 1; }}
        100% {{ right: -100px; opacity: 0; }}
    }}
    .peek-item {{ position: fixed; z-index: 9999; pointer-events: none; font-size: 4rem; }}

    /* C. 画面全体アクション */
    @keyframes shake {{
        0% {{ transform: translate(1px, 1px) rotate(0deg); }}
        10% {{ transform: translate(-1px, -2px) rotate(-1deg); }}
        30% {{ transform: translate(3px, 2px) rotate(0deg); }}
        100% {{ transform: translate(1px, 1px) rotate(0deg); }}
    }}
    .shake-screen {{ animation: shake 0.5s; animation-iteration-count: 4; }}

    @keyframes fade-dark {{
        0% {{ filter: brightness(1); }}
        20% {{ filter: brightness(0.4) sepia(0.6); }}
        80% {{ filter: brightness(0.4) sepia(0.6); }}
        100% {{ filter: brightness(1); }}
    }}
    .mood-dark {{ animation: fade-dark 3.5s ease-in-out; }}

    @keyframes bounce-screen {{
        0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
        40% {{ transform: translateY(-40px) scaleY(1.05); }}
        60% {{ transform: translateY(-20px) scaleY(1.02); }}
    }}
    .bounce-screen {{ animation: bounce-screen 0.8s ease; }}

    @keyframes flash-white {{
        0% {{ filter: brightness(1); }}
        10% {{ filter: brightness(2.5) contrast(1.2); }}
        100% {{ filter: brightness(1); }}
    }}
    .flash-screen {{ animation: flash-white 0.6s ease-out; }}

    /* D. 流れる文字演出（ニコニコ風） */
    @keyframes marquee {{
        0% {{ transform: translateX(100vw); }}
        100% {{ transform: translateX(-100vw); }}
    }}
    .marquee-wrapper {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9998;
        overflow: hidden;
    }}
    .marquee-text {{
        position: absolute;
        white-space: nowrap;
        font-size: 2.5rem;
        font-weight: 800;
        color: rgba(255, 255, 255, 0.5);
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        animation: marquee 5s linear forwards;
    }}

    /* E. シャトルが飛ぶ演出（スマッシュ） */
    @keyframes smash-hit {{
        0% {{ transform: translate(100vw, -100px) rotate(-45deg); opacity: 1; }}
        100% {{ transform: translate(-100px, 100vh) rotate(-45deg); opacity: 1; }}
    }}
    .shuttle-wrapper {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 10000;
        overflow: hidden;
    }}
    .shuttle-item {{
        position: absolute;
        font-size: 4rem;
        animation: smash-hit 0.4s ease-in forwards;
    }}

    </style>
""", unsafe_allow_html=True)

# --- 4. 認証機能 ---
if "password_correct" not in st.session_state:
    st.write("🔒 Enter Password")
    pw = st.text_input("Password", type="password", key="login")
    
    try:
        ua = st.context.headers.get("User-Agent", "")
        query_params = st.query_params
        url_user = query_params.get("user", None)
        
        os_info = "Unknown Device"
        detected_user = "Unknown"
        
        if "Android" in ua:
            os_info = "Android"
            detected_user = "Maki"
        elif "iPhone" in ua:
            os_info = "iPhone"
            detected_user = "Hide"
        elif "iPad" in ua:
            os_info = "iPad"
            detected_user = "Hide"
        elif "Windows" in ua:
            os_info = "Windows"
            if url_user:
                detected_user = url_user
            else:
                detected_user = "Hide"
        
        st.write(f"👤 User: **{detected_user}**")
        st.caption(f"Device: {os_info}")
        st.session_state["username"] = detected_user
    except:
        pass

    if pw == "05250206":
        st.session_state["password_correct"] = True
        st.rerun()
    st.stop()

# --- 5. 設定 ---
if "page_offset" not in st.session_state:
    st.session_state["page_offset"] = 0
if "last_effect_id" not in st.session_state:
    st.session_state["last_effect_id"] = None

current_user_raw = st.session_state.get("username", "Hide")
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
            emoji_in_text = re.findall(r'[\U00010000-\U0010ffff]', msg_body)
            
            # A. 昇る演出
            priority_emoji = None
            if any(word in msg_body for word in ["大好き", "愛してる"]): priority_emoji = "💘"
            elif any(word in msg_body for word in ["好き", "ありがとう", "感謝", "ラブラブ"]): priority_emoji = "❤️"
            elif any(word in msg_body for word in ["お疲れ様", "おつかれさま", "お疲れ", "ちょい飲み", "ちょい呑み", "ビール", "酒"]): priority_emoji = "🍺"
            elif "おにぎり" in msg_body: priority_emoji = "🍙"
#            elif any(word in msg_body for word in ["バドミントン", "練習", "試合"]): priority_emoji = "🏸"
            elif any(word in msg_body for word in ["ラーメン", "山岡家"]): priority_emoji = "🍜"
            elif any(word in msg_body for word in ["野菜", "サラダ", "レタス"]): priority_emoji = "🥬"
            elif any(word in msg_body for word in ["おやすみ", "眠い", "寝る"]): priority_emoji = "💤"
            elif any(word in msg_body for word in ["綺麗", "きれい", "すごい", "最高"]): priority_emoji = "✨"
            elif any(word in msg_body for word in ["コーヒー", "カフェ", "休憩"]): priority_emoji = "☕️"
            elif any(word in msg_body for word in ["ドライブ"]): priority_emoji = "🚗"
            elif any(word in msg_body for word in ["ワイン", "ハイボール", "乾杯"]): priority_emoji = "🥂"
            elif any(word in msg_body for word in ["花見", "さくら", "桜"]): priority_emoji = "🌸"
            elif any(word in msg_body for word in ["楽しみ", "ルンルン", "うれしい"]): priority_emoji = "🎶"
            elif any(word in msg_body for word in ["ケーキ", "スイーツ", "甘いもの"]): priority_emoji = "🍰"
            elif any(word in msg_body for word in ["ラッキー", "幸せ", "しあわせ", "ハッピー"]): priority_emoji = "🍀"
            elif any(word in msg_body for word in ["熊", "困った"]): priority_emoji = "🐻"
            elif any(word in msg_body for word in ["おやつ", "プリン"]): priority_emoji = "🍮"
            elif any(word in msg_body for word in ["バーガー", "マクド", "朝マック"]): priority_emoji = "🍔"

            if priority_emoji:
                effect_html = '<div class="rising-emoji">'
                for i in range(25):
                    left, size = random.randint(5, 95), random.uniform(2.5, 4.5)
                    delay, duration = random.uniform(0, 0.5), random.uniform(5.5, 6.5)
                    effect_html += f'<div class="emoji-item" style="left:{left}%; font-size:{size}rem; animation-delay:{delay}s; animation-duration:{duration}s;">{priority_emoji}</div>'
                st.markdown(effect_html + '</div>', unsafe_allow_html=True)
            
            # B. ひょっこり演出
            elif emoji_in_text:
                target_emoji = emoji_in_text[-1]
                peek_html = '<div>'
                for i in range(5):
                    side = random.choice(["left", "right"])
                    top = random.randint(20, 80)
                    delay = random.uniform(0, 2.0)
                    duration = random.uniform(3.0, 4.0)
                    anim_name = "peek-left" if side == "left" else "peek-right"
                    peek_html += f'<div class="peek-item" style="{side}:-100px; top:{top}%; animation:{anim_name} {duration}s forwards; animation-delay:{delay}s;">{target_emoji}</div>'
                st.markdown(peek_html + '</div>', unsafe_allow_html=True)

            # C. 画面全体のアクション
            if any(word in msg_body for word in ["おめでとう", "祝", "記念日", "誕生日", "やったー"]): st.balloons()
            if any(word in msg_body for word in ["雪", "寒い", "冬", "クリスマス"]): st.snow()
            
            if any(word in msg_body for word in ["こら", "起きて", "え！", "びっくり", "地震", "怒"]):
                components.html('<script>window.parent.document.querySelector(".stApp").classList.add("shake-screen"); setTimeout(() => { window.parent.document.querySelector(".stApp").classList.remove("shake-screen"); }, 2000);</script>', height=0)
            if any(word in msg_body for word in ["さみしい", "淋しい", "悲しい", "疲れた"]):
                components.html('<script>window.parent.document.querySelector(".stApp").classList.add("mood-dark"); setTimeout(() => { window.parent.document.querySelector(".stApp").classList.remove("mood-dark"); }, 3500);</script>', height=0)
            if any(word in msg_body for word in ["マジで", "えー", "正解", "おー"]):
                components.html('<script>window.parent.document.querySelector(".stApp").classList.add("bounce-screen"); setTimeout(() => { window.parent.document.querySelector(".stApp").classList.remove("bounce-screen"); }, 1000);</script>', height=0)
            if any(word in msg_body for word in ["びっくり", "すごい", "光る", "指輪"]):
                components.html('<script>window.parent.document.querySelector(".stApp").classList.add("flash-screen"); setTimeout(() => { window.parent.document.querySelector(".stApp").classList.remove("flash-screen"); }, 600);</script>', height=0)

            # D. 流れる文字演出（ニコニコ風）
            if any(word in msg_body for word in ["w", "笑", "草", "うける", "爆笑", "すご", "最高", "天才", "神", "優勝", "飲みに行", "ビール", "大好き"]):
                marquee_html = '<div class="marquee-wrapper">'
                display_text = (msg_body[:20] + '..') if len(msg_body) > 20 else msg_body
                for i in range(3):
                    top_pos = random.randint(10, 80)
                    delay = i * 0.7
                    marquee_html += f'<div class="marquee-text" style="top:{top_pos}vh; animation-delay:{delay}s;">{display_text}</div>'
                st.markdown(marquee_html + '</div>', unsafe_allow_html=True)

            # E. シャトル演出（スマッシュ）
            if any(word in msg_body for word in ["バド", "練習", "試合", "スマッシュ", "🏸"]):
                shuttle_html = '<div class="shuttle-wrapper"><div class="shuttle-item">🏸</div></div>'
                st.markdown(shuttle_html, unsafe_allow_html=True)

            st.session_state["last_effect_id"] = msg_id

    # チャットログ表示
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

# --- 9. 送信エリア ---
prompt = st.chat_input(input_placeholder)
if prompt:
    try:
        supabase.table(table_name).insert({"sender_name": current_user_raw, "message_body": prompt}).execute()
        st.session_state["page_offset"] = 0
        st.rerun()
    except Exception as e:
        st.error(f"送信エラー: {e}")

# --- 10. 自動スクロール ---
if st.session_state["page_offset"] == 0:
    components.html('<script>window.parent.document.querySelector(".main").scrollTo(0, 99999);</script>', height=0)