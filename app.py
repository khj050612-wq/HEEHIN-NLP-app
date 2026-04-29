import streamlit as st
from kiwipiepy import Kiwi

# 한국어 형태소 분석기 초기화
kiwi = Kiwi()

st.title("🔍 한국어 정밀 문장 분석기")
st.info("단순 띄어쓰기가 아닌 어근, 어미, 고유명사를 구분합니다.")

user_input = st.text_area("문장을 입력하세요", "철수가 학교에 가고 있어요.")

if st.button("정밀 분석 시작"):
    # Kiwi를 사용하여 형태소 분석
    result = kiwi.analyze(user_input)
    
    # 분석된 결과에서 단어와 품사 추출
    tokens = []
    for res in result:
        for token in res[0]:
            # 고유명사(NNP), 일반명사(NNG), 어근(XR), 어미(E..) 등을 구분해서 보여줌
            tokens.append({"단어": token.form, "품사": token.tag})
    
    st.subheader("📝 형태소 분석 결과")
    st.table(tokens)
    
    # 간단한 요약
    st.subheader("💡 분석 요약")
    nnps = [t['단어'] for t in tokens if t['품사'] == 'NNP']
    nngs = [t['단어'] for t in tokens if t['품사'] == 'NNG']
    
    if nnps:
        st.write(f"📍 **고유명사(이름 등):** {', '.join(set(nnps))}")
    if nngs:
        st.write(f"📚 **일반명사(사물 등):** {', '.join(set(nngs))}")
