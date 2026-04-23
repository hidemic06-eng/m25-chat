import streamlit as st
import os

# 1. そもそも設定が効いているか確認
st.title("環境設定の確認")
st.write(f"現在の最大アップロードサイズ設定: {os.environ.get('STREAMLIT_SERVER_MAX_UPLOAD_SIZE', '未設定')} MB")

# 2. 最小限のアップロードテスト
img = st.file_uploader("2MB以上のファイルを選んでください", type=['png', 'jpg', 'jpeg'])

if img:
    st.success(f"ファイルを受け取りました！ 名前: {img.name}, サイズ: {img.size / 1024 / 1024:.2f} MB")
    # ここで落ちなければ「環境設定」は成功、かつ「通信経路」も正常です。