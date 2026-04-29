import streamlit as st
from kiwipiepy import Kiwi
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 페이지 설정
st.set_page_config(page_title="아동 발달 분석기", layout="wide")

# 형태소 분석기 초기화
@st.cache_resource
def load_kiwi():
    return Kiwi()

kiwi = load_kiwi()

# --- 케이스별 예시 문장 데이터 ---
EXAMPLES = {
    "정상 발달 (2~3세)": """엄마 사탕 줘. 아빠 이거 뭐야? 멍멍이 예쁘다. 나 우유 먹어. 선생님 안녕. 뽀로로 보여줘. 이거 내 거야. 아기 자요. 물 많이 줘. 엄마 같이 가. 신발 신어. 까까 맛있어. 여기 앉아. 빵 더 줘. 저기 봐봐. 사과 빨개요. 아빠 일 가? 나 이거 할래. 멍멍이 무서워. 엄마 봐봐. 자동차 빵빵. 우유 다 먹었어. 할머니 좋아. 아파요 요기. 쉬 했어. 코 자자. 우와 크다. 양말 벗어. 비 와요. 나 잡아봐라.""",
    
    "언어 발달 지체 (명사 위주)": """엄마. 사탕. 물. 우유. 까까. 신발. 사과. 아빠. 멍멍이. 아기. 빵. 자동차. 할머니. 양말. 비. 나. 이거. 여기. 저거. 공. 모자. 포크. 수저. 컵. 집. 산. 달. 별. 꽃. 나비.""",
    
    "자폐 성향 (반향어 및 반복)": """사탕 줄까? 사탕 줄까? 뽀로로가 나타났다. 뽀로로가 나타났다. 이거 뭐야? 이거 뭐야? 문 닫아. 문 닫아. 치카해. 치카해. 맘마 먹자. 맘마 먹자. 빨간색. 빨간색. 빨간색. 1번. 2번. 3번. 4번. 5번. 나비 나비 나비 나비 나비 나비."""
}

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

st.divider()

# --- 2. 발화 내용 입력 및 예시 버튼 ---
st.subheader(f"💬 2. {child_name}의 발화 내용을 입력해주세요")

# 버튼 클릭 시 텍스트 영역에 넣을 값을 세션 상태에 저장
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

st.write("💡 아래 버튼을 누르면 테스트용 예시 문장이 자동으로 채워집니다.")
col_ex1, col_ex2, col_ex3 = st.columns(3)

if col_ex1.button("✅ 정상 발달 예시"):
    st.session_state.input_text = EXAMPLES["정상 발달 (2~3세)"]
    st.rerun()
if col_ex2.button("⚠️ 발달 지체 예시"):
    st.session_state.input_text = EXAMPLES["언어 발달 지체 (명사 위주)"]
    st.rerun()
if col_ex3.button("🧩 자폐 성향 예시"):
    st.session_state.input_text = EXAMPLES["자폐 성향 (반향어 및 반복)"]
    st.rerun()

user_input = st.text_area("문장을 직접 입력하거나 위 버튼을 눌러보세요.", 
                          value=st.session_state.input_text, height=150)

# 가상 또래 데이터
norm_data = {
    "24개월 미만": {"명사": 70, "동사": 20, "형용사": 10},
    "2~3세": {"명사": 50, "동사": 35, "형용사": 15},
    "3~4세": {"명사": 45, "동사": 40, "형용사": 15},
    "4~5세": {"명사": 40, "동사": 45, "형용사": 15},
}

if st.button("🚀 발달 수준 비교 분석 시작"):
    result = kiwi.analyze(user_input)
    tokens = [t.tag for res in result for t in res[0]]
    total = len(tokens)
    
    if total > 0:
        n_c = len([t for t in tokens if t.startswith('NN')])
        v_c = len([t for t in tokens if t.startswith('VV')])
        a_c = len([t for t in tokens if t.startswith('VA')])
        
        labels = ["명사", "동사", "형용사"]
        child_values = [n_c, v_c, a_c]
        norm_values = [norm_data[age_group]["명사"], norm_data[age_group]["동사"], norm_data[age_group]["형용사"]]

        st.subheader("📊 품사 구성 비중 비교 (또래 vs 우리 아이)")
        fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]],
                            subplot_titles=[f"📢 또래 평균 ({age_group})", f"✨ {child_name}의 결과"])

        fig.add_trace(go.Pie(labels=labels, values=norm_values, name="또래 평균", hole=.3), 1, 1)
        fig.add_trace(go.Pie(labels=labels, values=child_values, name=child_name, hole=.3), 1, 2)
        fig.update_layout(height=400, margin=dict(t=50, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

        # 결과 분석 메시지
        child_v_ratio = (v_c / total * 100)
        gap = child_v_ratio - norm_data[age_group]["동사"]
        
        st.divider()
        if gap < -10:
            st.warning(f"⚠️ {child_name}는 또래보다 동사 활용이 {abs(gap):.1f}%p 적습니다. 행동 묘사 놀이가 필요합니다.")
        else:
            st.success(f"✅ {child_name}는 또래 수준에 맞게 문장을 구성하고 있습니다.")
    else:
        st.error("분석할 문장을 입력해주세요.")

st.caption("본 도구는 수업 과제용 가상 수치로 분석합니다.")
