import streamlit as st
import random
from supabase import create_client

# Supabase 接続
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("📘 単語4択学習アプリ（Supabase版）")

# セッション初期化
if "question" not in st.session_state:
    st.session_state.question = None

# -------------------------
# 単語登録
# -------------------------
st.header("✏️ 単語登録")

with st.form("word_form"):
    word = st.text_input("単語")
    correct = st.text_input("正解の意味")
    choice1 = st.text_input("誤答1")
    choice2 = st.text_input("誤答2")
    choice3 = st.text_input("誤答3")

    submitted = st.form_submit_button("登録")

    if submitted:
        if word and correct:
            supabase.table("words").insert({
                "word": word,
                "correct": correct,
                "choice1": choice1,
                "choice2": choice2,
                "choice3": choice3
            }).execute()
            st.success("✅ 登録しました")
        else:
            st.error("⚠️ 単語と正解は必須です")

# -------------------------
# クイズ機能
# -------------------------
st.header("🎮 クイズ")

data = supabase.table("words").select("*").execute().data

if len(data) == 0:
    st.info("まずは単語を登録してください")
else:
    if st.session_state.question is None:
        st.session_state.question = random.choice(data)

    q = st.session_state.question

    st.subheader(f"Q. {q['word']} の意味は？")

    choices = [q["correct"], q["choice1"], q["choice2"], q["choice3"]]
    random.shuffle(choices)

    selected = st.radio("選択してください", choices)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("回答"):
            is_correct = selected == q["correct"]

            # 履歴保存
            supabase.table("history").insert({
                "word": q["word"],
                "selected": selected,
                "correct": q["correct"],
                "is_correct": is_correct
            }).execute()

            if is_correct:
                st.success("🎉 正解！")
            else:
                st.error(f"❌ 不正解。正解は「{q['correct']}」")

    with col2:
        if st.button("次の問題へ"):
            st.session_state.question = random.choice(data)
            st.rerun()

# -------------------------
# 履歴表示
# -------------------------
st.header("📊 学習履歴")

history = supabase.table("history").select("*").order("created_at", desc=True).execute().data
st.dataframe(history)
# -------------------------
# 正答率の集計
# -------------------------
st.header("📈 学習成績")

if len(history) == 0:
    st.info("まだ学習履歴がありません")
else:
    total = len(history)
    correct_count = sum(1 for h in history if h["is_correct"])
    accuracy = correct_count / total * 100

    st.metric("回答数", total)
    st.metric("正解数", correct_count)
    st.metric("正答率", f"{accuracy:.1f}%")
