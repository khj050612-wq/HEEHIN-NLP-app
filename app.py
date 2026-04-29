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

# --- 케이스별 예시 문장 데이터 (결과값 유도형) ---
EXAMPLES = {
    "그룹 A (정상 발달)": "엄마 사탕 줘. 아빠 이거 뭐야? 멍멍이 예쁘다. 나 우유 먹어. 선생님 안녕. 뽀로로 보여줘. 이거 내 거야. 아기 자요. 물 많이 줘. 엄마 같이 가.", # 명사/동사/형용사 골고루
    "그룹 B (발달 지체)": "엄마. 사탕. 물. 우유. 까까. 신발. 사과. 아빠. 멍멍이. 아기.", # 명사만 100% (동사 부족 유도)
    "그룹 C (자폐 성향)": "사탕 줄까? 사탕 줄까? 뽀로로가 나타났다. 뽀로로가 나타났다. 이거 뭐야? 이거 뭐야?" # 동일 문장 반복 (반복 패턴 유도)
}

st.title("👶 우리 아이 언어 발달 비교 분석기")
st.title("👶 우리 아이 언어 발달 비교 분석기")

# 깔끔한 회색 텍스트로 목적 설명
st.caption("""
본 서비스는 인공지능 기술을 활용하여 학부모가 아이의 발화 데이터를 객관적으로 확인하고, 
또래 발달 수준과 비교해 볼 수 있도록 돕는 언어발달 모니터링 보조 도구입니다. \n
아이의 언어 환경을 이해하고 건강한 성장을 지원하는 기초 자료로 활용해 보세요.
""")
st.divider()

import datetime

# --- 1. 아이 정보 입력 (자동 연령 계산 버전) ---
st.subheader("📝 1. 아이 정보를 입력해주세요")
c1, c2, c3, c4 = st.columns([2, 1, 1, 2])

with c1:
    child_name = st.text_input("아이 이름", "엘리자베스")
with c2:
    this_year = datetime.date.today().year
    birth_year = st.selectbox("출생 연도", range(this_year, this_year - 11, -1), index=2) # 기본값 2년 전
with c3:
    birth_month = st.selectbox("출생 월", range(1, 13), index=datetime.date.today().month - 1)

# --- [자동 연령 계산 로직] ---
today = datetime.date.today()
# 대략적인 개월 수 계산
total_months = (today.year - birth_year) * 12 + (today.month - birth_month)

# 개월 수에 따른 비교군 자동 설정
if total_months < 24:
    auto_age_index = 0  # 24개월 미만
elif 24 <= total_months < 36:
    auto_age_index = 1  # 2~3세
elif 36 <= total_months < 48:
    auto_age_index = 2  # 3~4세
else:
    auto_age_index = 3  # 4~5세

with c4:
    # index를 auto_age_index로 설정하여 자동 선택되게 함
    age_groups = ["24개월 미만", "2~3세", "3~4세", "4~5세"]
    age_group = st.selectbox("비교군(또래 연령대) 자동 선택", age_groups, index=auto_age_index)
    st.caption(f"💡 현재 아이는 약 **{total_months}개월**입니다.")

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

        # --- 4. 고정된 3가지 결과 메시지 로직 ---
        st.divider()
        
        # 품사 계산 수치를 바탕으로 결과 판정
        noun_ratio = (n_c / total * 100)
        verb_ratio = (v_c / total * 100)
        
        # 중복 문장 비율 계산 (자폐 성향 체크용)
        unique_sentences = set([s.strip() for s in user_input.split('.') if s.strip()])
        sentence_count = len([s.strip() for s in user_input.split('.') if s.strip()])
        repetition_ratio = (1 - len(unique_sentences) / sentence_count) if sentence_count > 0 else 0

        # 결과 출력 시나리오
        if repetition_ratio > 0.3: # 동일 문장 반복이 많을 때
            st.error("### 🧩 [결과] 특이 발화 패턴(반향어/반복) 관찰")
            st.write("상대방의 말을 그대로 따라 하거나 특정 문장을 반복하는 양상이 두드러집니다. 이는 자폐 스펙트럼의 대표적 특징인 '반향어'일 가능성이 있으니 전문 기관의 정밀 검사를 권장합니다.")
            
        elif verb_ratio < 15: # 동사 비중이 극히 낮을 때 (B그룹 유도)
            st.warning("### ⚠️ [결과] 언어 발달 지체(낱말 나열 수준) 의심")
            st.write("현재 문장 형태가 아닌 명사 위주의 낱말 나열 단계에 머물러 있습니다. 또래에 비해 동사 활용도가 현저히 낮으므로, 사물 이름보다는 '먹다, 가다, 예쁘다' 등 움직임과 상태를 나타내는 표현을 의도적으로 들려주어야 합니다.")
            
        else: # 정상적인 품사 분포 (A그룹 유도)
            st.success("### ✅ [결과] 연령 수준에 적합한 정상 발달")
            st.write("명사, 동사, 형용사가 골고루 사용되고 있으며 문장 구성 능력이 또래 수준에 부합합니다. 아이의 요구에 적절히 반응하며 자연스러운 대화를 지속해 주시는 것만으로도 훌륭한 언어 자극이 됩니다.")

st.caption("주의: 해당 분석은 수업 과제용 가상 연령별 수치를 기준으로 분석한 결과입니다. 실제 진단은 전문가와 상담하시기 바랍니다.")
