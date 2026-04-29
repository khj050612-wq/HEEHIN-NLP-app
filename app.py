import streamlit as st
from kiwipiepy import Kiwi
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="아동 발달 분석기", layout="wide")

# 형태소 분석기 초기화
kiwi = Kiwi()

st.title("👶 우리 아이 언어 발달 비교 분석기")
st.info("아이의 발화 내용을 입력하면 또래 수준과 비교해 드립니다.")

# --- 1. 아이 정보 입력 (메인 화면 상단) ---
st.subheader("📝 1. 아이 정보를 입력해주세요")
c1, c2, c3 = st.columns(3)

with c1:
    child_name = st.text_input("아이 이름", "우리 아이")
with c2:
    birth_date = st.date_input("출생년월일")
with c3:
    age_group = st.selectbox("비교군(또래 연령대) 선택", ["24개월 미만", "2~3세", "3~4세", "4~5세"])

st.divider()

# --- 2. 발화 내용 입력 ---
st.subheader(f"💬 2. {child_name}의 발화 내용을 입력해주세요")
user_input = st.text_area("여러 문장을 입력할수록 정확도가 높아집니다.", 
                          "엄마 사탕 줘. 학교에 가요. 멍멍이가 예뻐요.", height=150)

# 가상 또래 데이터 (과제용 표준 지표)
norm_data = {
    "24개월 미만": {"명사": 70, "동사": 20, "형용사": 10},
    "2~3세": {"명사": 50, "동사": 35, "형용사": 15},
    "3~4세": {"명사": 45, "동사": 40, "형용사": 15},
    "4~5세": {"명사": 40, "동사": 45, "형용사": 15},
}

if st.button("🚀 발달 수준 비교 분석 시작"):
    # 형태소 분석
    result = kiwi.analyze(user_input)
    tokens = [t.tag for res in result for t in res[0]]
    
    # 아이 데이터 계산
    total = len(tokens)
    if total > 0:
        noun_count = len([t for t in tokens if t.startswith('NN')])
        verb_count = len([t for t in tokens if t.startswith('VV')])
        adj_count = len([t for t in tokens if t.startswith('VA')])
        
        child_stats = {
            "명사": (noun_count / total * 100),
            "동사": (verb_count / total * 100),
            "형용사": (adj_count / total * 100),
        }

        # 3. 시각화 및 비교
        st.divider()
        st.subheader("📊 분석 결과 비교")
        
        col_chart, col_text = st.columns([2, 1])
        
        with col_chart:
            # 스트림릿 내장 차트 사용 (한글 깨짐 방지)
            comparison_df = pd.DataFrame({
                "항목": ["명사", "동사", "형용사"],
                "우리 아이": [child_stats["명사"], child_stats["동사"], child_stats["형용사"]],
                "또래 평균": [norm_data[age_group]["명사"], norm_data[age_group]["동사"], norm_data[age_group]["형용사"]]
            })
            st.bar_chart(comparison_df.set_index("항목"))

        with col_text:
            gap = child_stats["동사"] - norm_data[age_group]["동사"]
            st.metric("동사 활용도 차이", f"{child_stats['동사']:.1f}%", f"{gap:.1f}%")
            
            if gap < -10:
                st.warning("⚠️ 또래에 비해 동사 활용이 적습니다.")
                st.write("아이와 함께 행동을 묘사하는 놀이를 많이 해주세요!")
            else:
                st.success("✅ 또래 수준에 맞게 잘 발달하고 있습니다.")
                
        # 상세 품사 결과 표
        with st.expander("🔍 상세 품사 분석 결과 보기"):
            detailed_tokens = []
            for res in result:
                for token in res[0]:
                    detailed_tokens.append({"단어": token.form, "품사": token.tag})
            st.table(detailed_tokens)
    else:
        st.error("분석할 텍스트가 부족합니다. 문장을 더 입력해주세요.")

st.divider()
st.caption(f"본 도구는 언어치료와 자연어처리 수업 과제용으로 제작되었습니다. (비교 데이터는 가상 수치입니다.)")
