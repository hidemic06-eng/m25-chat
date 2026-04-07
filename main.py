import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
from datetime import datetime, timedelta, timezone
import random
import re
from PIL import Image, ImageOps  # ImageOpsを追加
import io
import uuid

# --- 1. アプリの基本設定 ---
st.set_page_config(page_title="M25", page_icon="💬", layout="wide")

# --- 2. データベース(Supabase)接続設定 ---
table_name = st.secrets.get("TABLE_NAME", "messages")
supabase_url = "https://kvqbwknrsdasoipttkpr.supabase.co"
supabase_key = st.secrets.get("SUPABASE_KEY", "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT")
supabase = create_client(supabase_url, supabase_key)

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
    .block-container {{ padding-top: 1rem; padding-bottom: 40px !important; max-width: 100% !important; }}
    [data-testid="stChatInput"] {{ margin-bottom: -10px; }}

    .stButton > button {{
        background-color: #424549 !important;
        color: white !important;
        border: 1px solid #4f545c !important;
    }}

    .chat-row {{ display: flex; flex-direction: column; margin-bottom: 20px; width: 100%; }}
    
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

    /* ポラロイド風フレームのデザイン */
    .chat-image {{
        max-width: 280px;
        border-radius: 4px;
        margin-top: 10px;
        /* 白いフチとしっかりめの影 */
        border: 8px solid #ffffff !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.4);
        /* わずかに傾けてランダムな配置感を出す */
        transform: rotate(-1.5deg);
        display: inline-block;
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
    
    /* --- アニメーション定義 --- */
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
    @keyframes marquee {{ 0% {{ transform: translateX(100vw); }} 100% {{ transform: translateX(-100vw); }} }}
    .marquee-wrapper {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9998; overflow: hidden; }}
    .marquee-text {{ position: absolute; white-space: nowrap; font-size: 2.5rem; font-weight: 800; color: rgba(255, 255, 255, 0.5); text-shadow: 2px 2px 4px rgba(0,0,0,0.5); animation: marquee 5s linear forwards; }}

    /* #専用：1時間ループテロップ用CSS */
    @keyframes marquee-infinite {{ 0% {{ transform: translateX(100vw); }} 100% {{ transform: translateX(-100vw); }} }}
    .fixed-marquee-wrapper {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9997; overflow: hidden; }}
    .fixed-marquee-text {{ position: absolute; white-space: nowrap; font-size: 1.8rem; font-weight: 700; text-shadow: 1px 1px 2px rgba(0,0,0,0.3); animation: marquee-infinite 15s linear infinite; }}

    @keyframes rainbow-text {{ 0% {{ color: #ff0000; text-shadow: 0 0 8px #ff0000; }} 17% {{ color: #ff8000; text-shadow: 0 0 8px #ff8000; }} 33% {{ color: #ffff00; text-shadow: 0 0 8px #ffff00; }} 50% {{ color: #00ff00; text-shadow: 0 0 8px #00ff00; }} 67% {{ color: #00ffff; text-shadow: 0 0 8px #00ffff; }} 83% {{ color: #0000ff; text-shadow: 0 0 8px #0000ff; }} 100% {{ color: #ff00ff; text-shadow: 0 0 8px #ff00ff; }} }}
    .rainbow-active {{ animation: rainbow-text 2s infinite linear !important; font-weight: 800 !important; }}
    @keyframes neon-flicker {{ 0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {{ color: #fff; text-shadow: 0 0 4px #fff, 0 0 10px #fff, 0 0 18px #ff00de, 0 0 30px #ff00de; }} 20%, 22%, 24%, 55% {{ color: #444; text-shadow: none; }} }}
    .neon-active {{ animation: neon-flicker 4s infinite alternate !important; font-weight: 700 !important; }}
    @keyframes marker-draw {{ 0% {{ background-size: 0% 100%; }} 100% {{ background-size: 100% 100%; }} }}
    .marker-active {{ background: linear-gradient(transparent 60%, rgba(255, 235, 59, 0.4) 0%) no-repeat !important; background-size: 100% 100%; animation: marker-draw 1.5s ease-out; display: inline; font-weight: 700 !important; }}
    @keyframes wave-text {{ 0%, 100% {{ transform: translateY(0); }} 25% {{ transform: translateY(-4px) rotate(-1deg); }} 75% {{ transform: translateY(4px) rotate(1deg); }} }}
    .wave-active {{ display: inline-block; animation: wave-text 2s infinite ease-in-out !important; }}
    @keyframes focus-text {{ 0% {{ filter: blur(8px); opacity: 0; }} 100% {{ filter: blur(0); opacity: 1; }} }}
    .mystery-active {{ animation: focus-text 4s forwards !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. 画像圧縮用関数 ---
def compress_image(uploaded_file):
    img = Image.open(uploaded_file)
    # 【追加】向き情報を読み取って自動回転させる
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGB": img = img.convert("RGB")
    if img.width > 1200:
        ratio = 1200 / img.width
        img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
    img_io = io.BytesIO()
    img.save(img_io, format="JPEG", quality=75, optimize=True)
    img_io.seek(0)
    return img_io

# --- 5. 認証機能 ---
if "password_correct" not in st.session_state:
    st.write("🔒 Enter Password")
    pw = st.text_input("Password", type="password", key="login")
    try:
        ua = st.context.headers.get("User-Agent", "")
        query_params = st.query_params
        url_user = query_params.get("user", None)
        os_info = "Unknown Device"; detected_user = "Unknown"
        if "Android" in ua: os_info = "Android"; detected_user = "Maki"
        elif "iPhone" in ua or "iPad" in ua: os_info = "iOS Device"; detected_user = "Hide"
        elif "Windows" in ua: os_info = "Windows"; detected_user = url_user if url_user else "Hide"
        st.write(f"👤 User: **{detected_user}**")
        st.caption(f"Device: {os_info}")
        st.session_state["username"] = detected_user
    except: pass
    if pw == "05250206":
        st.session_state["password_correct"] = True
        st.rerun()
    st.stop()

# --- 6. 設定 ---
if "page_offset" not in st.session_state: st.session_state["page_offset"] = 0
if "last_effect_id" not in st.session_state: st.session_state["last_effect_id"] = None
if "uploader_key" not in st.session_state: st.session_state["uploader_key"] = str(uuid.uuid4())
if "last_compression_info" not in st.session_state: st.session_state["last_compression_info"] = None

current_user_raw = st.session_state.get("username", "Hide")
current_user_upper = current_user_raw.upper()

# --- 7. ヘッダー ---
st.title(f"💬 M25-Chat{status_label}")
auto_update = st.toggle("自動更新(8s)", value=True)
if auto_update and st.session_state["page_offset"] == 0:
    st_autorefresh(interval=8000, key="chat_ref")
st.divider()

# --- 8. ナビゲーション ---
col_prev, col_page, col_next = st.columns([1, 2, 1])
with col_prev:
    if st.button("⬅️ 前の20件"):
        st.session_state["page_offset"] += 20
        st.rerun()
    if st.session_state["page_offset"] == 0:
        with st.expander("📷 写真をアップロード", expanded=False):
            if st.session_state["last_compression_info"]: st.info(st.session_state["last_compression_info"])
            img_file = st.file_uploader("画像選択", type=['png', 'jpg', 'jpeg'], key=st.session_state["uploader_key"])
            if img_file and st.button("🖼️ 画像を送信"):
                try:
                    with st.spinner("送信中..."):
                        original_size = img_file.size / 1024
                        compressed_data = compress_image(img_file)
                        compressed_size = compressed_data.getbuffer().nbytes / 1024
                        ext = img_file.name.split('.')[-1]
                        file_path = f"public/{uuid.uuid4()}.{ext}"
                        supabase.storage.from_("images").upload(file_path, compressed_data.getvalue(), {"content-type": f"image/{ext}"})
                        final_url = supabase.storage.from_("images").get_public_url(file_path)
                        supabase.table(table_name).insert({"sender_name": current_user_raw, "message_body": "", "image_url": final_url}).execute()
                        st.session_state["last_compression_info"] = f"✅ 送信完了！ {original_size:.1f}KB → {compressed_size:.1f}KB"
                        st.session_state["uploader_key"] = str(uuid.uuid4()); st.rerun()
                except Exception as e: st.error(f"Error: {e}")

with col_page:
    st.write(f"<div style='text-align:center; font-size:0.8rem;'>{st.session_state['page_offset']+1}〜件目</div>", unsafe_allow_html=True)
with col_next:
    if st.session_state["page_offset"] >= 20:
        if st.button("次の20件 ➡️"): st.session_state["page_offset"] -= 20; st.rerun()

# --- 9. 表示 & 演出の判定 ---
try:
    # --- 【修正箇所：過去ログ無限取得対応】 ---
    start_range = st.session_state["page_offset"]
    end_range = start_range + 50
    
    res_all = supabase.table(table_name).select("*").order("created_at", desc=True).range(start_range, end_range).execute()
    all_data = res_all.data
    # 表示用の20件を切り出し
    messages = all_data[:20][::-1]
    # ------------------------------------------
    
    # --- #付きメッセージを1時間流す機能 (完全ランダム位置版) ---
    if st.session_state["page_offset"] == 0:
        now = datetime.now(timezone.utc)
        one_hour_ago = now - timedelta(hours=1)
        
        pinned_msgs = [
            m for m in all_data 
            if m.get("message_body") and m["message_body"].startswith("#") 
            and datetime.fromisoformat(m['created_at'].replace('Z', '+00:00')) > one_hour_ago
        ]
        
        if pinned_msgs:
            fixed_marquee_html = '<div class="fixed-marquee-wrapper">'
            for idx, pm in enumerate(pinned_msgs):
                icon = random.choice(["🌈", "📢", "💡", "🚀", "🎉", "💡", "📌", "🐣", "🏃", "📣"])
                clean_text = f"{icon} {pm['message_body'].lstrip('#').strip()}"
                text_color = "rgba(255, 182, 193, 0.5)" if "MAKI" in pm["sender_name"].upper() else "rgba(135, 206, 235, 0.5)"
                top_pos = random.randint(5, 85) 
                delay = random.uniform(0, 15)
                fixed_marquee_html += f'<div class="fixed-marquee-text" style="top:{top_pos}vh; animation-delay:-{delay}s; color:{text_color};">{clean_text}</div>'
            st.markdown(fixed_marquee_html + '</div>', unsafe_allow_html=True)

    if messages and st.session_state["page_offset"] == 0:
        latest_msg = messages[-1]
        msg_id, msg_body, img_url_latest = latest_msg.get("id"), latest_msg.get("message_body", ""), latest_msg.get("image_url")
        
        if msg_id != st.session_state["last_effect_id"]:
            priority_emoji = None
            if img_url_latest:
                priority_emoji = "📷"
                components.html('<script>window.parent.document.querySelector(".stApp").classList.add("flash-screen"); setTimeout(() => { window.parent.document.querySelector(".stApp").classList.remove("flash-screen"); }, 600);</script>', height=0)
            else:
                emoji_in_text = re.findall(r'[\U00010000-\U0010ffff]', msg_body)
                if any(word in msg_body for word in ["大好き", "愛してる"]): priority_emoji = "💘"
                elif any(word in msg_body for word in ["好き", "ありがとう", "感謝", "ラブラブ"]): priority_emoji = "❤️"
                elif any(word in msg_body for word in ["お疲れ様", "おつかれさま", "お疲れ", "ちょい飲み", "ちょい呑み", "ビール", "酒"]): priority_emoji = "🍺"
                elif "おにぎり" in msg_body: priority_emoji = "🍙"
                elif any(word in msg_body for word in ["バドミントン", "練習", "試合"]): priority_emoji = "🏸"
                elif any(word in msg_body for word in ["ラーメン", "山岡家"]): priority_emoji = "🍜"
                elif any(word in msg_body for word in ["野菜", "サラダ", "レタス"]): priority_emoji = "🥬"
                elif any(word in msg_body for word in ["おやすみ", "眠い", "寝る"]): priority_emoji = "💤"
                elif any(word in msg_body for word in ["綺麗", "きれい", "すごい", "最高"]): priority_emoji = "✨"
                elif any(word in msg_body for word in ["コーヒー", "カフェ", "休憩"]): priority_emoji = "☕️"
                elif any(word in msg_body for word in ["ドライブ"]): priority_emoji = "🚗"
                elif any(word in msg_body for word in ["ワイン", "ハイボール", "乾杯"]): priority_emoji = "🥂"
                elif any(word in msg_body for word in ["花見", "さくら", "桜"]): priority_emoji = "🌸"
                elif any(word in msg_body for word in ["楽しみ", "ルンルン", "うれしい"]): priority_emoji = "🥳"
                elif any(word in msg_body for word in ["ケーキ", "スイーツ", "甘いもの"]): priority_emoji = "🍰"
                elif any(word in msg_body for word in ["ラッキー", "幸せ", "しあわせ", "ハッピー"]): priority_emoji = "🍀"
                elif any(word in msg_body for word in ["熊", "困った"]): priority_emoji = "🐻"
                elif any(word in msg_body for word in ["おやつ", "プリン"]): priority_emoji = "🍮"
                elif any(word in msg_body for word in ["バーガー", "マクド", "朝マック"]): priority_emoji = "🍔"
                elif any(word in msg_body for word in ["キノコ", "きのこ"]): priority_emoji = "🍄"

            if priority_emoji:
                effect_html = '<div class="rising-emoji">'
                for i in range(25):
                    left, size = random.randint(5, 95), (random.uniform(2.0, 5.5) if priority_emoji == "📷" else random.uniform(2.5, 4.5))
                    delay, duration = random.uniform(0, 0.5), random.uniform(5.5, 6.5)
                    effect_html += f'<div class="emoji-item" style="left:{left}%; font-size:{size}rem; animation-delay:{delay}s; animation-duration:{duration}s;">{priority_emoji}</div>'
                st.markdown(effect_html + '</div>', unsafe_allow_html=True)
            elif not img_url_latest and emoji_in_text:
                target_emoji = emoji_in_text[-1]
                peek_html = '<div>'
                for i in range(5):
                    side = random.choice(["left", "right"]); top = random.randint(20, 80)
                    delay, duration = random.uniform(0, 2.0), random.uniform(3.0, 4.0)
                    anim_name = "peek-left" if side == "left" else "peek-right"
                    peek_html += f'<div class="peek-item" style="{side}:-100px; top:{top}%; animation:{anim_name} {duration}s forwards; animation-delay:{delay}s;">{target_emoji}</div>'
                st.markdown(peek_html + '</div>', unsafe_allow_html=True)

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
            
            if any(word in msg_body for word in ["www", "笑", "草", "うける", "爆笑", "最高", "天才", "神", "優勝", "飲みに行", "ビール", "大好き"]):
                marquee_html = '<div class="marquee-wrapper">'
                display_text = (msg_body[:20] + '..') if len(msg_body) > 20 else msg_body
                for i in range(3):
                    top_pos = random.randint(10, 80); delay = i * 0.7
                    marquee_html += f'<div class="marquee-text" style="top:{top_pos}vh; animation-delay:{delay}s;">{display_text}</div>'
                st.markdown(marquee_html + '</div>', unsafe_allow_html=True)
            st.session_state["last_effect_id"] = msg_id

    # --- 9-2. チャットログ表示 ---
    wd_jp = ["月", "火", "水", "木", "金", "土", "日"]
    now_jst = datetime.now(timezone.utc) + timedelta(hours=9)
    today_str = now_jst.strftime('%Y-%m-%d')

    for m in messages:
        utc_time = datetime.fromisoformat(m['created_at'].replace('Z', '+00:00'))
        jst_time = utc_time + timedelta(hours=9)
        s_name = m['sender_name']
        s_up = s_name.upper()

        # --- 日付表示のロジック追加 ---
        msg_date_str = jst_time.strftime('%Y-%m-%d')
        if msg_date_str == today_str:
            time_display = jst_time.strftime('%H:%M')
        else:
            weekday = wd_jp[jst_time.weekday()]
            time_display = jst_time.strftime(f'%m/%d({weekday}) %H:%M')
        # ----------------------------

        align = "align-right" if s_up == current_user_upper else "align-left"
        h_style = "flex-direction: row-reverse;" if s_up == current_user_upper else ""
        n_class = "name-maki" if "MAKI" in s_up else "name-hide" if "HIDE" in s_up else ""
        m_body, img_url = m.get("message_body", ""), m.get("image_url")
        img_html = f'<div><img src="{img_url}" class="chat-image"></div>' if img_url else ""
        effect_class = ""
        if any(word in m_body for word in ["大好き", "くっつ", "最高", "優勝", "指輪"]): effect_class = "rainbow-active"
        elif any(word in m_body for word in ["駅ビル", "福島", "京橋", "居酒屋", "呑み", "打ち上げ", "呑みすぎ", "ビール", "乾杯"]): effect_class = "neon-active"
        elif any(word in m_body for word in ["予約", "集合", "待ち合わせ", "予定", "計画", "約束", "チケット", "行こう"]): effect_class = "marker-active"
        elif any(word in m_body for word in ["海", "水族館", "ゆらゆら", "おやすみ", "ねむい", "おはよー"]): effect_class = "wave-active"
        elif any(word in m_body for word in ["秘密", "実は", "わからない", "内緒", "おはよう", "本当"]): effect_class = "mystery-active"
        
        st.markdown(f"""
            <div class="chat-row {align}">
                <div class="chat-header" style="{h_style}">
                    <span class="{n_class}">{s_name}</span><span class="timestamp">{time_display}</span>
                </div>
                <div class="message-text {effect_class}">{m_body}</div>
                {img_html}
            </div>
        """, unsafe_allow_html=True)
except Exception as e: st.error(f"表示エラー: {e}")

# --- 10. 送信エリア ---
prompt = st.chat_input(input_placeholder)
if prompt:
    try:
        supabase.table(table_name).insert({"sender_name": current_user_raw, "message_body": prompt}).execute()
        st.session_state["last_compression_info"] = None
        st.session_state["page_offset"] = 0; st.rerun()
    except Exception as e: st.error(f"送信エラー: {e}")
if st.session_state["page_offset"] == 0:
    components.html('<script>window.parent.document.querySelector(".main").scrollTo(0, 99999);</script>', height=0)