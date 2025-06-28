import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import matplotlib.pyplot as plt
import re

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

if "diagnosis_count" not in st.session_state:
    st.session_state.diagnosis_count = 0

st.title("🧠 政治的バイアス診断アプリ")
st.markdown("SNS投稿や自身の意見などから政治的意見を入力してください（100字以内）例:『憲法改正は必要だと思う』『夫婦別姓制度は導入されるべきだ』")

user_input = st.text_area("投稿内容", key="user_input")

if st.button("診断する") and user_input:
    if st.session_state.diagnosis_count >= 5:
        st.warning("プロトタイプでは1人5回までの診断に制限されています。")
    else:
        prompt = f"""
以下のSNS投稿から、以下の3つを出力してください：

1. 政治的傾向スコア（-1.0=保守、+1.0=リベラル）
2. バイアス強度スコア（0.0〜1.0）
3. コメント（なぜそのスコアになったか、該当箇所を指摘して必ず事実ベースでハルシネーションを起こさないようになるべく中立的に200文字程度で）

投稿内容: {user_input}

出力フォーマット:
傾向スコア: 数値
強さスコア: 数値
コメント: ○○○○
"""

        with st.spinner("診断中..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            result = response.choices[0].message.content
            st.code(result)

        st.session_state.diagnosis_count += 1

        try:
            bias_match = re.search(r"傾向スコア[:：]\s*(-?\d+\.?\d*)", result)
            strength_match = re.search(r"強さスコア[:：]\s*(\d+\.?\d*)", result)
            comment_match = re.search(r"コメント[:：]\s*(.*)", result, re.DOTALL)

            if bias_match and strength_match and comment_match:
                bias_score = float(bias_match.group(1))
                strength_score = float(strength_match.group(1))
                comment = comment_match.group(1).strip()

                st.markdown(f"**傾向スコア:** {bias_score} **強さスコア:** {strength_score}")
                st.markdown(f"**コメント:** {comment}")

                fig, ax = plt.subplots()
                ax.scatter(bias_score, strength_score, color="blue")
                ax.set_xlim(-1.0, 1.0)
                ax.set_ylim(0.0, 1.0)
                ax.set_xlabel("Political Bias Score (-1.0 = Conservative, +1.0 = Liberal)")
                ax.set_ylabel("Strength Score (0.0 = Mild, 1.0 = Strong)")
                ax.grid(True)

                st.pyplot(fig)
            else:
                st.error("診断結果の解析に失敗しました。フォーマットを確認してください。")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

st.info(f"診断回数: {st.session_state.diagnosis_count}/5")
