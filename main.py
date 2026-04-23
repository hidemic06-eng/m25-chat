import streamlit as st

st.title("最終切り分けテスト")

# ただファイルを受け取るだけ。中身は見ない。
img = st.file_uploader("テスト", type=['png', 'jpg'])

if img:
    # 圧縮も、Supabaseも、Image.openも一切しない。
    # ただ「受け取ったよ」という文字を出すだけ。
    st.write(f"ファイル名: {img.name}")