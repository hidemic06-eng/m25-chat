import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import random

# --- 1. アプリの基本設定 ---
# ページタイトルやアイコン、レイアウト（ワイドモード）を設定
st.set_page_config(page_title="M25", page_icon="💬", layout="wide")

# --- 2. データベース(Supabase)接続設定 ---
# st.secrets からテーブル名を取得。未設定ならデフォルトの "messages" を使用
table_name = st.secrets.get("TABLE_NAME", "messages")

# --- 3. デザイン設定（CSS） ---
# Discord風のダークモードカラーを定義
app_bg_color = "#313338"     # 背景：ダークグレー
text_main_color = "#dbdee1"  # 文字：明るいグレー
sub_text_color = "#949ba4"   # 補助：落ち着いたグレー

# テスト用DBか本番用DBかでラベルとプレースホルダーを切り替え
if table_name == "messages_test":
    status_label = " 🧪 TEST"
    input_placeholder = "テストメッセージを入力..."
else:
    status_label = ""
    input_placeholder = "メッセージを入力..."

# HTML/CSSを直接注入してデザインをカスタマイズ
st.markdown(f"""
    <style>
    /* Google Fontsから丸ゴシック体「M PLUS Rounded 1c」をインポート */
    @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;700&display=swap');

    /* アプリ全体の背景色と基本フォントの設定 */
    .stApp {{ 
        background-color: {app_bg_color}; 
        color: {text_main_color}; 
        font-family: 'M PLUS Rounded 1c', sans-serif !important; 
    }}
    
    /* Streamlit標準のヘッダー・フッター・メニューを非表示にして「アプリ感」を出す */
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    .stAppDeployButton {{display:none;}}
    [data-testid="bundle-viewer-container"] {{display: none !important;}}
    
    /* メインコンテンツの余白調整（下部にチャット入力欄があるため padding-bottom を多めに確保） */
    .block-container {{ padding-top: 1rem; padding-bottom: 80px !important; max-width: 100% !important; }}
    
    /* 1つの発言（名前＋本文）を囲むコンテナ */
    .chat-row {{ 
        display: flex; 
        flex-direction: column; 
        margin-bottom: 16px; 
        width: 100%; 
    }}
    
    /* メッセージ本文のスタイル設定（カーニングや行間を調整） */
    .message-text {{ 
        font-family: 'M PLUS Rounded 1c', sans-serif !important;
        font-feature-settings: "palt" 1; /* プロポーショナルメトリクス：文字詰め */
        font-size: 1.15rem; 
        line-height: 1.35; 
        font-weight: 500 !important; 
        letter-spacing: -0.04rem; 
        max-width: 80%; 
        white-space: pre-wrap; /* 改行を反映 */
        word-wrap: break-word; /* 長い英単語を折り返し */
        color: {text_main_color} !important; 
        background-color: transparent !important;
        padding: 0; 
    }}

    /* チャット入力エリア（st.chat_input）のフォントも合わせる */
    .stChatInput textarea {{
        font-family: 'M PLUS Rounded 1c', sans-serif !important;
        font-feature-settings: "palt" 1 !important;
        letter-spacing: -0.02rem !important;
        font-size: 1rem !important;
    }}
    .stChatInput textarea::placeholder {{
        font-family: 'M PLUS Rounded 1c', sans-serif !important;
        opacity: 0.7;
    }}

    /* 送信者が自分（Hide）なら右寄せ */
    .align-right {{ align-items: flex-end; text-align: right; }}
    .align-right .message-text {{ text-align: right; }}

    /* 送信者が相手（Maki）なら左寄せ */
    .align-left {{ align-items: flex-start; text-align: left; }}
    .align-left .message-text {{ text-align: left; }}
    
    /* 名前と時刻を表示するヘッダー部分 */
    .chat-header {{ display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; font-size: 0.85rem; }}
    .name-maki {{ color: #ffa657 !important; font-weight: 700; }} /* Makiさん：オレンジ */
    .name-hide {{ color: #58a6ff !important; font-weight: 700; }} /* Hideさん：ブルー */
    .timestamp {{ color: {sub_text_color}; font-size: 0.75rem; }}
    
    /* 【演出】画面を揺らすシェイクアニメーション */
    @keyframes shake {{
        0% {{ transform: translate(1px, 1px) rotate(0deg); }}
        10% {{ transform: translate(-1px, -2px) rotate(-1deg); }}
        30% {{ transform: translate(3px, 2px) rotate(0deg); }}
        50% {{ transform: translate(-1px, 2px) rotate(-1deg); }}
        100% {{ transform: translate(1px, 1px) rotate(0deg); }}
    }}
    .shake-screen {{ animation: shake 0.5s; animation-iteration-count: 4; }}

    /* 【演出】絵文字が下から上に昇るアニメーション */
    @keyframes rise {{
        0% {{ transform: translateY(0); opacity: 0; }}
        5% {{ opacity: 1; }}
        85% {{ opacity: 1; }}
        100% {{ transform: translateY(-125vh) rotate(360deg); opacity: 0; }}
    }}
    .rising-emoji {{ position: fixed; bottom: -12vh; left: 0; width: 100%; height: 0; z-index: 9999; pointer-events: none; }}
    .emoji-item {{ position: absolute; animation: rise linear forwards; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. 認証機能 ---
# パスワードが正しいか session_state で管理。正しくなければ処理を停止(stop)
if "password_correct" not in st.session_state:
    st.write("🔒 Enter Password")
    pw = st.text_input("Password", type="password", key="login")
    if pw == "05250206":
        st.session_state["password_correct"] = True
        st.rerun()
    st.stop()

# --- 5. セッション & DB接続の初期化 ---
# ページ番号（オフセット）や、最後に演出を実行したメッセージIDを保持
if "page_offset" not in st.session_state:
    st.session_state["page_offset"] = 0
if "last_effect_id" not in st.session_state:
    st.session_state["last_effect_id"] = None

# URLパラメータからユーザー名（Hide/Maki）を取得
query_params = st.query_params
current_user_raw = query_params.get("user", "Hide")
current_user_upper = current_user_raw.upper()

# Supabaseクライアントの生成
supabase = create_client("https://kvqbwknrsdasoipttkpr.supabase.co", "sb_publishable_rm5x4m4thlpmVY9pKJ5Nug_aTO32nsT")

# --- 6. ヘッダー表示 ---
st.title(f"💬 M25-Chat{status_label}")
auto_update = st.toggle("自動更新(8s)", value=True)
# 最新ページを表示している時のみ、8秒ごとに自動更新（st_autorefresh）
if auto_update and st.session_state["page_offset"] == 0:
    st_autorefresh(interval=8000, key="chat_ref")
st.divider()

# --- 7. ページネーション（過去ログ閲覧ナビ） ---
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

# --- 8. メッセージ表示 & 演出の判定ロジック ---
try:
    # Supabaseから最新20件を取得
    res = supabase.table(table_name).select("*").order("created_at", desc=True).range(st.session_state["page_offset"], st.session_state["page_offset"] + 19).execute()
    messages = res.data[::-1] # 表示用に古い順に並び替え
    
    # 演出の判定（最新メッセージが未実行のIDだった場合のみ実行）
    if messages and st.session_state["page_offset"] == 0:
        latest_msg = messages[-1]
        msg_id = latest_msg.get("id")
        msg_body = latest_msg["message_body"]
        
        if msg_id != st.session_state["last_effect_id"]:
            # キーワードに応じて絵文字を選択
            emoji = None
            if any(word in msg_body for word in ["大好き", "好き", "ありがとう", "感謝", "愛してる", "ラブラブ"]): emoji = "❤️"
            elif any(word in msg_body for word in ["お疲れ様", "おつかれさま", "お疲れ", "ちょい飲み", "ちょい呑み"]): emoji = "🍺"
            elif "おにぎり" in msg_body: emoji = "🍙"
            elif any(word in msg_body for word in ["バドミントン", "練習", "試合"]): emoji = "🏸"
            elif any(word in msg_body for word in ["ラーメン", "山岡家"]): emoji = "🍜"
            elif any(word in msg_body for word in ["野菜", "サラダ", "レタス"]): emoji = "🥬"
            elif any(word in msg_body for word in ["おやすみ", "眠い", "寝る"]): emoji = "💤"
            elif any(word in msg_body for word in ["綺麗", "きれい", "すごい", "最高"]): emoji = "✨"
            elif any(word in msg_body for word in ["コーヒー", "カフェ", "休憩"]): emoji = "☕️"
            elif any(word in msg_body for word in ["ドライブ"]): emoji = "🚗"
            elif any(word in msg_body for word in ["乾杯", "ワイン", "ハイボール"]): emoji = "🥂"
            elif any(word in msg_body for word in ["花見", "さくら", "桜"]): emoji = "🌸"
            elif any(word in msg_body for word in ["楽しみ", "ルンルン", "うれしい"]): emoji = "🎶"
            elif any(word in msg_body for word in ["ケーキ", "スイーツ", "甘いもの"]): emoji = "🍰"
            elif any(word in msg_body for word in ["ラッキー", "幸せ", "しあわせ", "ハッピー"]): emoji = "🍀"
            elif any(word in msg_body for word in ["熊", "困った"]): emoji = "🐻"

            # バルーン演出
            if any(word in msg_body for word in ["おめでとう", "祝", "記念日", "誕生日"]): st.balloons()
            # 雪演出
            if any(word in msg_body for word in ["雪", "寒い", "冬", "クリスマス"]): st.snow()
            
            # JavaScriptを注入して画面を揺らす（shake-screenクラスを追加）
            if any(word in msg_body for word in ["こら", "起きて", "びっくり", "地震", "怒"]):
                components.html('<script>window.parent.document.querySelector(".stApp").classList.add("shake-screen"); setTimeout(() => { window.parent.document.querySelector(".stApp").classList.remove("shake-screen"); }, 2000);</script>', height=0)

            # 絵文字上昇演出のHTML生成
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

            # IDを記録して重複実行を防止
            st.session_state["last_effect_id"] = msg_id

    # 取得したメッセージをループで1つずつ描画
    for m in messages:
        # 時刻をJST(日本標準時)に変換
        utc_time = datetime.fromisoformat(m['created_at'].replace('Z', '+00:00'))
        jst_time = utc_time + timedelta(hours=9)
        time_display = jst_time.strftime('%H:%M')
        
        s_up = m['sender_name'].upper()
        # 自分の発言か相手の発言かでクラスを切り替え
        align = "align-right" if s_up == current_user_upper else "align-left"
        h_style = "flex-direction: row-reverse;" if s_up == current_user_upper else ""
        n_class = "name-maki" if "MAKI" in s_up else "name-hide" if "HIDE" in s_up else ""
        
        # メッセージのHTMLを書き出し
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

# --- 9. メッセージ送信エリア ---
prompt = st.chat_input(input_placeholder)
if prompt:
    try:
        # Supabaseへレコード挿入
        supabase.table(table_name).insert({"sender_name": current_user_raw, "message_body": prompt}).execute()
        # ページを最新に戻して再描画
        st.session_state["page_offset"] = 0
        st.rerun()
    except Exception as e:
        st.error(f"送信エラー: {e}")

# --- 10. 最下部への自動スクロール ---
# 最新表示(offset=0)のときのみ、JavaScriptで画面の一番下までスクロールさせる
if st.session_state["page_offset"] == 0:
    components.html('<script>window.parent.document.querySelector(".main").scrollTo(0, 99999);</script>', height=0)