import streamlit as st

st.title("🍎 초간단 문장 분석기")
st.info("비전공자도 할 수 있는 자연어 처리 과제입니다.")

text = st.text_area("분석할 문장을 입력하세요", "여기에 문장을 입력하면 분석이 시작됩니다.")

if st.button("분석하기"):
    words = text.split()
    st.success(f"전체 단어 수: {len(words)}개")
    st.success(f"전체 글자 수(공백 포함): {len(text)}자")
    
    st.subheader("사용한 단어 목록")
    st.write(list(set(words)))
