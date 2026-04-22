import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
from datetime import datetime, timedelta, timezone
import random
import re
from PIL import Image, ImageOps
import io
import uuid

# ==========================================================
# 1. ページ設定 & ログインガード
# ==========================================================
st.set_page_config(page_title="M25-Chat", page_icon="💬", layout="wide")

# 未ログイン時はメイン（main_app.py）へ戻す
if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
    st.warning("セッションが切れました。再度ログインしてください。")
    if st.button("ログイン画面へ"):
        st.switch_page("main_app.py")
    st.stop()

# ==========================================================
# 2. 基本設定
# ==========================================================
table_name = st.secrets.get("TABLE_NAME", "messages")
supabase_url = "https://kvqbwknrsdasoipttkpr.supabase.co"
supabase_key = st.secrets.get("SUPABASE_KEY", "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT")
supabase = create_client(supabase_url, supabase_key)

app_bg_color = "#313338"
text_main_color = "#dbdee1"
sub_text_color = "#949ba4"
status_label = " 🧪 TEST" if table_name == "messages_test" else ""
input_placeholder = "テストメッセージを入力..." if table_name == "messages_test" else "メッセージを入力..."

# --- 演出用CSS適用（元のコードを完全維持） ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;700&display=swap');
    .stApp {{ background-color: {app_bg_color}; color: {text_main_color}; font-family: 'M PLUS Rounded 1c', sans-serif !important; }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    .stAppDeployButton {{display:none;}}
    [data-testid="bundle-viewer-container"] {{display: none !important;}}
    .block-container {{ padding-top: 1rem; padding-bottom: 40px !important; max-width: 100% !important; }}
    [data-testid="stChatInput"] {{ margin-bottom: -10px; }}
    .stButton > button {{ background-color: #424549 !important; color: white !important; border: 1px solid #4f545c !important; }}
    .chat-row {{ display: flex; flex-direction: column; margin-bottom: 20px; width: 100%; }}
    .message-text {{ 
        font-family: 'M PLUS Rounded 1c', sans-serif !important; font-feature-settings: "palt" 1; 
        font-size: 1.15rem; line-height: 1.35; font-weight: 500 !important; letter-spacing: -0.04rem; 
        max-width: 80%; white-space: pre-wrap; word-wrap: break-word; color: {text_main_color} !important; 
    }}
    .chat-image {{ max-width: 280px; border-radius: 4px; margin-top: 10px; border: 8px solid #ffffff !important; box-shadow: 0 6px 12px rgba(0,0,0,0.4); transform: rotate(-1.5deg); display: inline-block; }}
    .align-right {{ align-items: flex-end; text-align: right; }}
    .align-left {{ align-items: flex-start; text-align: left; }}
    .chat-header {{ display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; font-size: 0.85rem; }}
    .name-maki {{ color: #ffa657 !important; font-weight: 700; }}
    .name-hide {{ color: #58a6ff !important; font-weight: 700; }}
    .timestamp {{ color: {sub_text_color}; font-size: 0.75rem; }}

    /* アニメーション演出群 */
    .typewriter-char {{ display: inline-block; opacity: 0; animation: char-reveal 0.1s forwards; }}
    @keyframes char-reveal {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
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
    @keyframes marquee-infinite {{ 0% {{ transform: translateX(100vw); }} 100% {{ transform: translateX(-100vw); }} }}
    .fixed-marquee-wrapper {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9997; overflow: hidden; }}
    .fixed-marquee-text {{ position: absolute; white-space: nowrap; font-size: 1.8rem; font-weight: 700; text-shadow: 1px 1px 2px rgba(0,0,0,0.3); animation: marquee-infinite 15s linear infinite; }}

    /* テキストエフェクト */
    @keyframes rainbow-text {{ 0% {{ color: #ff0000; text-shadow: 0 0 8px #ff0000; }} 17% {{ color: #ff8000; text-shadow: 0 0 8px #ff8000; }} 33% {{ color: #ffff00; text-shadow: 0 0 8px #ffff00; }} 50% {{ color: #00ff00; text-shadow: 0 0 8px #00ff00; }} 67% {{ color: #00ffff; text-shadow: 0 0 8px #00ffff; }} 83% {{ color: #0000ff; text-shadow: 0 0 8px #0000ff; }} 100% {{ color: #ff00ff; text-shadow: 0 0 8px #ff00ff; }} }}
    .rainbow-active {{ animation: rainbow-text 2s infinite linear !important; font-weight: 800 !important; }}
    @keyframes neon-flicker {{ 0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {{ color: #fff; text-shadow: 0 0 4px #fff, 0 0 10px #fff, 0 0 18px #ff00de, 0 0 30px #ff00de; }} 20%, 22%, 24%, 55% {{ color: #444; text-shadow: none; }} }}
    .neon-active {{ animation: neon-flicker 4s infinite alternate !important; font-weight: 700 !important; }}
    @keyframes marker-draw {{ 0% {{ background-size: 0% 100%; }} 100% {{ background-size: 100% 100%; }} }}
    .marker-active {{ background: linear-gradient(transparent 60%, rgba(255, 235, 59, 0.4) 0%) no-repeat !important; background-size: 100% 100%; animation: marker-draw 1.5s ease-out; display: inline; font-weight: 700 !important; }}
    .marker-pink-active {{ background: linear-gradient(transparent 60%, rgba(255, 105, 180, 0.4) 0%) no-repeat !important; background-size: 100% 100%; animation: marker-draw 1.5s ease-out; display: inline; font-weight: 700 !important; }}
    .marker-blue-active {{ background: linear-gradient(transparent 60%, rgba(0, 191, 255, 0.4) 0%) no-repeat !important; background-size: 100% 100%; animation: marker-draw 1.5s ease-out; display: inline; font-weight: 700 !important; }}
    @keyframes wave-text {{ 0%, 100% {{ transform: translateY(0); }} 25% {{ transform: translateY(-4px) rotate(-1deg); }} 75% {{ transform: translateY(4px) rotate(1deg); }} }}
    .wave-active {{ display: inline-block; animation: wave-text 2s infinite ease-in-out !important; }}
    @keyframes focus-text {{ 0% {{ filter: blur(8px); opacity: 0; }} 100% {{ filter: blur(0); opacity: 1; }} }}
    .mystery-active {{ animation: focus-text 4s forwards !important; }}
    @keyframes pulse-text {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.2); }} 100% {{ transform: scale(1); }} }}
    .pulse-active {{ display: inline-block; animation: pulse-text 1.5s infinite ease-in-out !important; font-weight: 700 !important; }}
    </style>
""", unsafe_allow_html=True)

# ヘルパー関数: 画像圧縮
def compress_image(uploaded_file):
    img = Image.open(uploaded_file)
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGB": img = img.convert("RGB")
    if img.width > 1200:
        ratio = 1200 / img.width
        img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
    img_io = io.BytesIO()
    img.save(img_io, format="JPEG", quality=75, optimize=True)
    img_io.seek(0)
    return img_io

# 状態初期化
if "page_offset" not in st.session_state: st.session_state["page_offset"] = 0
if "last_effect_id" not in st.session_state: st.session_state["last_effect_id"] = None
if "uploader_key" not in st.session_state: st.session_state["uploader_key"] = str(uuid.uuid4())
if "last_compression_info" not in st.session_state: st.session_state["last_compression_info"] = None
if "shown_ids" not in st.session_state: st.session_state["shown_ids"] = set()

current_user_raw = st.session_state.get("username", "Hide")
current_user_upper = current_user_raw.upper()

# メイン表示
st.title(f"💬 M25-Chat{status_label}")
auto_update = st.toggle("自動更新(8s)", value=True)
if auto_update and st.session_state["page_offset"] == 0:
    st_autorefresh(interval=8000, key="chat_ref")
st.divider()

# --- ナビゲーション ---
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

# --- チャットログ表示・演出ロジック ---
try:
    start_range = st.session_state["page_offset"]
    end_range = start_range + 50
    res_all = supabase.table(table_name).select("*").order("created_at", desc=True).range(start_range, end_range).execute()
    all_data = res_all.data
    messages = all_data[:20][::-1]

    # #付きメッセージ（流れる文字）
    if st.session_state["page_offset"] == 0:
        now = datetime.now(timezone.utc)
        one_hour_ago = now - timedelta(hours=1)
        pinned_msgs = [m for m in all_data if m.get("message_body", "").startswith("#") and datetime.fromisoformat(m['created_at'].replace('Z', '+00:00')) > one_hour_ago]
        if pinned_msgs:
            fixed_marquee_html = '<div class="fixed-marquee-wrapper">'
            for pm in pinned_msgs:
                icon = random.choice(["🌈", "📢", "💡", "🚀", "🎉", "📌", "🏃"])
                clean_text = f"{icon} {pm['message_body'].lstrip('#').strip()}"
                text_color = "rgba(255, 182, 193, 0.5)" if "MAKI" in pm["sender_name"].upper() else "rgba(135, 206, 235, 0.5)"
                fixed_marquee_html += f'<div class="fixed-marquee-text" style="top:{random.randint(5, 85)}vh; animation-delay:-{random.uniform(0, 15)}s; color:{text_color};">{clean_text}</div>'
            st.markdown(fixed_marquee_html + '</div>', unsafe_allow_html=True)

    # メイン演出 (エフェクト発動判定)
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
                elif any(word in msg_body for word in ["お疲れ様", "お疲れ", "ちょい飲み", "ビール", "酒"]): priority_emoji = "🍺"
                elif "おにぎり" in msg_body: priority_emoji = "🍙"
                elif any(word in msg_body for word in ["バドミントン", "練習", "試合"]): priority_emoji = "🏸"
                elif any(word in msg_body for word in ["ラーメン", "山岡家"]): priority_emoji = "🍜"
                elif any(word in msg_body for word in ["野菜", "サラダ", "レタス"]): priority_emoji = "🥬"
                elif any(word in msg_body for word in ["おやすみ", "眠い", "寝る"]): priority_emoji = "💤"
                elif any(word in msg_body for word in ["綺麗", "きれい", "すごい", "最高"]): priority_emoji = "✨"
                elif any(word in msg_body for word in ["コーヒー", "カフェ", "休憩"]): priority_emoji = "☕️"
                elif "ドライブ" in msg_body: priority_emoji = "🚗"
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
                for i in range(12):
                    size = (random.uniform(2.0, 5.5) if priority_emoji == "📷" else random.uniform(2.5, 4.5))
                    effect_html += f'<div class="emoji-item" style="left:{random.randint(5, 95)}%; font-size:{size}rem; animation-delay:{random.uniform(0, 0.5)}s; animation-duration:{random.uniform(5.5, 6.5)}s;">{priority_emoji}</div>'
                st.markdown(effect_html + '</div>', unsafe_allow_html=True)
            elif not img_url_latest and emoji_in_text:
                target_emoji = emoji_in_text[-1]
                peek_html = '<div>'
                for i in range(5):
                    side = random.choice(["left", "right"])
                    anim_name = "peek-left" if side == "left" else "peek-right"
                    peek_html += f'<div class="peek-item" style="{side}:-100px; top:{random.randint(20, 80)}%; animation:{anim_name} {random.uniform(3.0, 4.0)}s forwards; animation-delay:{random.uniform(0, 2.0)}s;">{target_emoji}</div>'
                st.markdown(peek_html + '</div>', unsafe_allow_html=True)

            if any(word in msg_body for word in ["おめでとう", "祝", "記念日", "誕生日", "やったー"]): st.balloons()
            if any(word in msg_body for word in ["雪", "寒い", "冬", "クリスマス"]): st.snow()
            if any(word in msg_body for word in ["こら", "起きて", "え！", "びっくり", "地震", "怒"]):
                components.html('<script>window.parent.document.querySelector(".stApp").classList.add("shake-screen"); setTimeout(() => { window.parent.document.querySelector(".stApp").classList.remove("shake-screen"); }, 2000);</script>', height=0)
            if any(word in msg_body for word in ["さみしい", "淋しい", "悲しい", "疲れた"]):
                components.html('<script>window.parent.document.querySelector(".stApp").classList.add("mood-dark"); setTimeout(() => { window.parent.document.querySelector(".stApp").classList.remove("mood-dark"); }, 3500);</script>', height=0)
            if any(word in msg_body for word in ["マジで", "えー", "正解", "おー"]):
                components.html('<script>window.parent.document.querySelector(".stApp").classList.add("bounce-screen"); setTimeout(() => { window.parent.document.querySelector(".stApp").classList.remove("bounce-screen"); }, 1000);</script>', height=0)
            if any(word in msg_body for word in ["www", "笑", "草", "うける", "爆笑", "最高", "天才", "神", "優勝", "ビール", "大好き"]):
                marquee_html = '<div class="marquee-wrapper">'
                display_text = (msg_body[:20] + '..') if len(msg_body) > 20 else msg_body
                for i in range(3): marquee_html += f'<div class="marquee-text" style="top:{random.randint(10, 80)}vh; animation-delay:{i * 0.7}s;">{display_text}</div>'
                st.markdown(marquee_html + '</div>', unsafe_allow_html=True)
            st.session_state["last_effect_id"] = msg_id

    # チャットログ描画部
    wd_en = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    now_jst = datetime.now(timezone.utc) + timedelta(hours=9)
    today_str = now_jst.strftime('%Y-%m-%d')
    latest_id = messages[-1].get("id") if messages else None

    for m in messages:
        jst_time = datetime.fromisoformat(m['created_at'].replace('Z', '+00:00')) + timedelta(hours=9)
        msg_date_str = jst_time.strftime('%Y-%m-%d')
        time_display = jst_time.strftime('%H:%M') if msg_date_str == today_str else jst_time.strftime(f'%m/%d({wd_en[jst_time.weekday()]}) %H:%M')
        s_name, s_up, m_id = m['sender_name'], m['sender_name'].upper(), m.get("id")
        align = "align-right" if s_up == current_user_upper else "align-left"
        h_style = "flex-direction: row-reverse;" if s_up == current_user_upper else ""
        n_class = "name-maki" if "MAKI" in s_up else "name-hide" if "HIDE" in s_up else ""
        m_body, img_url = m.get("message_body", ""), m.get("image_url")
        
        is_new = (m_id == latest_id) and (st.session_state["page_offset"] == 0) and (m_id not in st.session_state["shown_ids"])
        if is_new:
            display_body = "".join([f'<span class="typewriter-char" style="animation-delay:{i*0.05}s;">{"<br>" if char=="\\n" else char}</span>' for i, char in enumerate(m_body)])
            st.session_state["shown_ids"].add(m_id)
        else:
            display_body = m_body.replace("\n", "<br>")

        eff_class = ""
        if any(w in m_body for w in ["大好き", "くっつ", "最高", "優勝", "指輪"]): eff_class = "rainbow-active"
        elif any(w in m_body for w in ["福島", "京橋", "居酒屋", "ビール", "ちょい飲み"]): eff_class = "neon-active"
        elif any(w in m_body for w in ["ドキドキ", "ワクワク", "楽しみ", "待ってる"]): eff_class = "pulse-active"
        elif any(w in m_body for w in ["デート", "ランチ", "会いたい"]): eff_class = "marker-pink-active"
        elif any(w in m_body for w in ["仕事", "会議", "出張", "資料"]): eff_class = "marker-blue-active"
        elif any(w in m_body for w in ["予約", "集合", "予定", "計画"]): eff_class = "marker-active"
        elif any(w in m_body for w in ["海", "お風呂", "ゆらゆら", "おやすみ"]): eff_class = "wave-active"
        elif any(w in m_body for w in ["秘密", "実は", "わからない", "内緒"]): eff_class = "mystery-active"

        st.markdown(f"""
            <div class="chat-row {align}">
                <div class="chat-header" style="{h_style}">
                    <span class="{n_class}">{s_name}</span><span class="timestamp">{time_display}</span>
                </div>
                <div class="message-text {eff_class}">{display_body}</div>
                {f'<div><img src="{img_url}" class="chat-image"></div>' if img_url else ""}
            </div>
        """, unsafe_allow_html=True)
except Exception as e: st.error(f"表示エラー: {e}")

# 送信エリア
prompt = st.chat_input(input_placeholder)
if prompt:
    try:
        supabase.table(table_name).insert({"sender_name": current_user_raw, "message_body": prompt}).execute()
        st.session_state["last_compression_info"] = None
        st.session_state["page_offset"] = 0; st.rerun()
    except Exception as e: st.error(f"送信エラー: {e}")

if st.session_state["page_offset"] == 0:
    components.html('<script>window.parent.document.querySelector(".main").scrollTo(0, 99999);</script>', height=0)
