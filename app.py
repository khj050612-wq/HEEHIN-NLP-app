import streamlit as st
from kiwipiepy import Kiwi
import pandas as pd
import matplotlib.pyplot as plt

# 한글 폰트 설정 (스트림릿 클라우드 환경에서는 폰트 문제가 있을 수 있어 영문 태그 병기)
kiwi = Kiwi()

st.set_page_config(page_title="아동 발달 분석기", layout="wide")

st.title("👶 우리 아이 언어 발달 비교 분석기")
st.write("아이의 발화 내용을 입력하면 또래 수준과 비교해 드립니다.")

# 1. 사이드바 - 아이 정보 입력
with st.sidebar:
    st.header("📝 아이 정보")
    child_name = st.text_input("아이 이름", "우리 아이")
    birth_date = st.date_input("출생년월일")
    age_group = st.selectbox("비교할 연령대", ["24개월 미만", "2~3세", "3~4세", "4~5세"])

# 2. 메인 화면 - 발화 내용 입력
st.subheader(f"💬 {child_name}의 발화 내용을 입력해주세요")
user_input = st.text_area("여러 문장을 입력할수록 정확도가 높아집니다.", 
                          "엄마 사탕 줘. 학교에 가요. 멍멍이가 예뻐요.", height=150)

# 3. 가상 또래 데이터 (과제용 표준 지표)
# 명사, 동사, 형용사 비율 (연령별 가상 수치)
norm_data = {
    "24개월 미만": {"명사": 70, "동사": 20, "형용사": 10},
    "2~3세": {"명사": 50, "동사": 35, "형용사": 15},
    "3~4세": {"명사": 45, "동사": 40, "형용사": 15},
    "4~5세": {"명사": 40, "동사": 45, "형용사": 15},
}

if st.button("발달 수준 비교 분석 시작"):
    # 형태소 분석
    result = kiwi.analyze(user_input)
    tokens = [t.tag for res in result for t in res[0]]
    
    # 아이 데이터 계산
    total = len(tokens)
    noun_count = len([t for t in tokens if t.startswith('NN')])
    verb_count = len([t for t in tokens if t.startswith('VV')])
    adj_count = len([t for t in tokens if t.startswith('VA')])
    
    child_stats = {
        "명사": (noun_count / total * 100) if total > 0 else 0,
        "동사": (verb_count / total * 100) if total > 0 else 0,
        "형용사": (adj_count / total * 100) if total > 0 else 0,
    }

    # 4. 시각화 및 비교
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 품사 사용 비율 비교")
        comparison_df = pd.DataFrame({
            "항목": ["명사", "동사", "형용사"],
            "우리 아이": [child_stats["명사"], child_stats["동사"], child_stats["형용사"]],
            "또래 평균": [norm_data[age_group]["명사"], norm_data[age_group]["동사"], norm_data[age_group]["형용사"]]
        })
        st.bar_chart(comparison_df.set_index("항목"))

    with col2:
        st.subheader("📋 상세 분석 결과")
        # 동사 사용률 비교로 수준 파악 (예시 로직)
        gap = child_stats["동사"] - norm_data[age_group]["동사"]
        
        st.metric("동사 사용 다양성", f"{child_stats['동사']:.1f}%", f"{gap:.1f}%")
        
        if gap < -10:
            st.warning(f"또래에 비해 동사(움직임 말) 활용이 조금 적은 편입니다.")
            st.write("💡 팁: 아이와 놀이할 때 '먹다', '자다', '뛰다' 등의 행동을 말로 더 자주 들려주세요!")
        else:
            st.success(f"또래 수준에 맞게 골고루 단어를 사용하고 있습니다.")

    st.divider()
    st.info(f"* 위 분석은 {age_group} 표준 데이터와 비교한 가이드이며, 정확한 진단은 전문가와 상담하세요.")
