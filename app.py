import streamlit as st
from kiwipiepy import Kiwi
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="아동 발달 분석기", layout="wide")
kiwi = Kiwi()

st.title("👶 우리 아이 언어 발달 비교 분석기")

# --- 1. 아이 정보 입력 ---
st.subheader("📝 1. 아이 정보를 입력해주세요")
c1, c2, c3 = st.columns(3)
with c1:
    child_name = st.text_input("아이 이름", "우리 아이")
with c2:
    birth_date = st.date_input("출생년월일")
with c3:
    age_group = st.selectbox("비교군(또래 연령대) 선택", ["24개월 미만", "2~3세", "3~4세", "4~5세"])

# 가상 또래 데이터
norm_data = {
    "24개월 미만": {"명사": 70, "동사": 20, "형용사": 10},
    "2~3세": {"명사": 50, "동사": 35, "형용사": 15},
    "3~4세": {"명사": 45, "동사": 40, "형용사": 15},
    "4~5세": {"명사": 40, "동사": 45, "형용사": 15},
}

st.divider()

# --- 2. 발화 내용 입력 ---
st.subheader(f"💬 2. {child_name}의 발화 내용을 입력해주세요")
user_input = st.text_area("문장을 입력하세요.", "엄마 사탕 줘. 학교에 가요. 멍멍이가 예뻐요.", height=100)

if st.button("🚀 발달 수준 비교 분석 시작"):
    result = kiwi.analyze(user_input)
    tokens = [t.tag for res in result for t in res[0]]
    total = len(tokens)
    
    if total > 0:
        n_c = len([t for t in tokens if t.startswith('NN')])
        v_c = len([t for t in tokens if t.startswith('VV')])
        a_c = len([t for t in tokens if t.startswith('VA')])
        
        # 비율 계산
        child_ratios = [n_c, v_c, a_c]
        norm_ratios = [norm_data[age_group]["명사"], norm_data[age_group]["동사"], norm_data[age_group]["형용사"]]
        labels = ["명사", "동사", "형용사"]

        # --- 3. 원형 그래프 2개 나란히 배치 ---
        st.subheader("📊 품사 구성 비중 비교 (또래 vs 우리 아이)")
        
        # Plotly 서브플롯 생성 (1행 2열)
        fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]],
                            subplot_titles=[f"📢 또래 평균 ({age_group})", f"✨ {child_name}의 결과"])

        # 왼쪽: 또래 평균
        fig.add_trace(go.Pie(labels=labels, values=norm_ratios, name="또래 평균", hole=.3), 1, 1)
        # 오른쪽: 우리 아이
        fig.add_trace(go.Pie(labels=labels, values=child_ratios, name=child_name, hole=.3), 1, 2)

        fig.update_layout(height=450, margin=dict(t=50, b=50, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

        # --- 4. 결과 분석 메시지 ---
        child_v_ratio = (v_c / total * 100)
        gap = child_v_ratio - norm_data[age_group]["동사"]
        
        st.divider()
        if gap < -10:
            st.warning(f"⚠️ {child_name}는 또래보다 동사 활용이 {abs(gap):.1f}%p 적습니다. 행동 묘사 놀이를 추천해요!")
        else:
            st.success(f"✅ {child_name}는 또래 수준에 맞게 아주 잘 말하고 있어요!")
            
    else:
        st.error("분석할 문장을 입력해주세요.")
