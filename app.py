import streamlit as st
from kiwipiepy import Kiwi
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

# 1. 페이지 설정
st.set_page_config(page_title="아동 발달 분석기", layout="wide")

@st.cache_resource
def load_kiwi():
    return Kiwi()

kiwi = load_kiwi()

# 2. 연령별/케이스별 예시 데이터
AGE_SPECIFIC_EXAMPLES = {
    "24개월 미만": {
        "A": "엄마 물. 아빠 가. 이거 뭐야? 멍멍이. 까까 줘. 어부바. 맘마 먹어. 빠빠이. 아니야. 나 이거.",
        "B": "엄마. 아빠. 물. 응. 어. 이거. 저거. 맘마. 쉬. 까까.",
        "C": "물. 물. 물. 이거 뭐야? 이거 뭐야? 엄마 엄마 엄마."
    },
    "2~3세": {
        "A": "엄마 사탕 줘. 아빠 이거 뭐야? 멍멍이 예쁘다. 나 우유 먹어. 선생님 안녕. 뽀로로 보여줘. 이거 내 거야. 아기 자요. 물 많이 줘. 엄마 같이 가.",
        "B": "엄마. 사탕. 물. 우유. 까까. 신발. 사과. 아빠. 멍멍이. 아기.",
        "C": "사탕 줄까? 사탕 줄까? 뽀로로가 나타났다. 뽀로로가 나타났다. 이거 뭐야? 이거 뭐야?"
    },
    "3~4세": {
        "A": "엄마 나 사탕 먹고 싶어. 아빠 오늘 어디 가요? 멍멍이가 멍멍 짖어요. 선생님이랑 같이 놀아요. 나도 비행기 타고 싶어.",
        "B": "사과 줘. 우유 먹어. 신발 신어. 아빠 와. 엄마 가. 멍멍이 예뻐. 사탕 좋아. 학교 가. 아기 자. 빵 먹어.",
        "C": "학교 가자 학교 가자. 사탕 먹어 사탕 먹어. 엄마가 그랬어 엄마가 그랬어."
    },
    "4~5세": {
        "A": "엄마 어제 유치원에서 친구랑 모래놀이 했어. 아빠 우리 내일은 놀이공원 가요? 나는 커서 멋진 소방관이 될 거야.",
        "B": "엄마 사탕 줘. 아빠 이거 뭐야. 멍멍이 예뻐. 나 우유 먹어. 이거 내 거야. 아기 자요. 물 줘.",
        "C": "내일 가자 내일 가자 내일 가자. 소방관 될 거야 소방관 될 거야."
    }
}

# 3. 메인 타이틀 및 목적
st.title("👶 우리 아이 언어 발달 비교 분석기")
st.caption("""
본 서비스는 인공지능 기술을 활용하여 학부모가 아이의 발화 데이터를 객관적으로 확인하고,  
또래 발달 수준과 비교해 볼 수 있도록 돕는 언어발달 모니터링 보조 도구입니다.
""")
st.divider()

# 4. 아이 정보 입력
st.subheader("📝 1. 아이 정보를 입력해주세요")
c1, c2, c3, c4 = st.columns([2, 1, 1, 2])

with c1:
    child_name = st.text_input("아이 이름", "엘리자베스")
with c2:
    this_year = datetime.date.today().year
    birth_year = st.selectbox("출생 연도", range(this_year, this_year - 11, -1), index=2)
with c3:
    birth_month = st.selectbox("출생 월", range(1, 13), index=datetime.date.today().month - 1)

total_months = (datetime.date.today().year - birth_year) * 12 + (datetime.date.today().month - birth_month)
if total_months < 24: auto_age_idx = 0
elif 24 <= total_months < 36: auto_age_idx = 1
elif 36 <= total_months < 48: auto_age_idx = 2
else: auto_age_idx = 3

with c4:
    age_groups = ["24개월 미만", "2~3세", "3~4세", "4~5세"]
    age_group = st.selectbox("비교군 자동 선택", age_groups, index=auto_age_idx)
    st.caption(f"💡 현재 아이는 약 **{total_months}개월**입니다.")

st.divider()

# 5. 발화 내용 입력 및 예시 버튼
st.subheader(f"💬 2. {child_name}의 발화 내용을 입력해주세요")

if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "current_case" not in st.session_state:
    st.session_state.current_case = "user"

st.write(f"💡 **[{age_group}]** 기준 예시 데이터가 자동으로 채워집니다.")
col_ex1, col_ex2, col_ex3 = st.columns(3)

if col_ex1.button("✅ 정상 발달 예시"):
    st.session_state.input_text = AGE_SPECIFIC_EXAMPLES[age_group]["A"]
    st.session_state.current_case = "normal"
    st.rerun()
if col_ex2.button("⚠️ 발달 지체 예시"):
    st.session_state.input_text = AGE_SPECIFIC_EXAMPLES[age_group]["B"]
    st.session_state.current_case = "delay"
    st.rerun()
if col_ex3.button("🧩 자폐 성향 예시"):
    st.session_state.input_text = AGE_SPECIFIC_EXAMPLES[age_group]["C"]
    st.session_state.current_case = "autism"
    st.rerun()

user_input = st.text_area("문장을 직접 입력하거나 위 버튼을 눌러보세요.", 
                          value=st.session_state.input_text, height=150)

# 가상 비교 데이터
norm_data = {
    "24개월 미만": {"명사": 70, "동사": 20, "형용사": 10},
    "2~3세": {"명사": 50, "동사": 35, "형용사": 15},
    "3~4세": {"명사": 45, "동사": 40, "형용사": 15},
    "4~5세": {"명사": 40, "동사": 45, "형용사": 15},
}

# 6. 분석 시작
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

        st.subheader("📊 품사 구성 비중 비교")
        fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]],
                            subplot_titles=[f"📢 또래 평균 ({age_group})", f"✨ {child_name}의 결과"])
        
        fig.add_trace(go.Pie(labels=labels, values=norm_values, name="또래 평균", hole=.3), 1, 1)
        fig.add_trace(go.Pie(labels=labels, values=child_values, name=child_name, hole=.3), 1, 2)
        fig.update_layout(height=400, margin=dict(t=50, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.write("#### ✨ 우리 아이 발달 특성 요약")

        if st.session_state.current_case == "autism":
            st.info("💡 **확인이 필요한 발화 패턴이 관찰됩니다**")
            st.write("상대방의 말을 그대로 따라 하거나 특정 문장을 반복하는 모습이 보입니다. 전문가와 편안하게 상담해 보시는 것을 추천드려요.")
        elif st.session_state.current_case == "delay":
            st.warning("💡 **문장 확장 연습이 도움이 될 수 있어요**")
            st.write(f"현재 {child_name}는 낱말 나열 단계에 머물러 있는 것 같습니다. 동사와 형용사를 섞어서 들려주시면 문장이 쑥쑥 자라날 거예요.")
        elif st.session_state.current_case == "normal":
            st.success("💡 **또래와 비슷하게 무럭무럭 자라고 있어요**")
            st.write(f"명사, 동사, 형용사를 골고루 사용하며 예쁘게 말하고 있네요! 지금처럼 풍부한 반응을 보여주세요.")
        else:
            st.write("입력하신 문장을 바탕으로 분석한 결과입니다.")
    else:
        st.error("분석할 문장을 입력해주세요.")

# 7. 하단 우측 수정 로그 배치
st.write("---")
log_c1, log_c2 = st.columns([5, 2]) # 오른쪽 칸(log_c2)을 작게 생성

with log_c2:
    with st.expander("🛠️ 개발 및 업데이트 로그"):
          st.info("해당 앱은 수업 과제용 가상 수치를 기준으로 통계화하는 방식으로 제작되었습니다.")
        st.markdown("""
        **1. 초기 모델 구축**
        - 기본적인 NLP 품사 분석 기능 구현
        - 또래 데이터와의 막대 그래프 비교

        **2. 시각화 및 UX 개선 (User Feedback)**
        - **병렬 원형 그래프**: 직관적 비교를 위해 막대형에서 원형(Pie)으로 변경 및 나란히 배치
        - **입력 간소화**: 생년월일 달력 선택을 연/월 드롭다운으로 변경

        **3. 기능 지능화**
        - **연령 자동 계산**: 생년월일 입력 시 현재 날짜 기준 개월 수 및 비교군 자동 매칭
        - **연령별 가변 예시**: 비교군 선택에 따라 예시 발화 내용이 연령 수준에 맞춰 자동 변경

        **4. 시나리오 및 안정성 보강**
        - **맞춤형 피드백**: '정상/지체/자폐' 각 케이스별 고유 분석 로직 및 부드러운 가이드 문구 적용
        - **KeyError 방지**: 데이터 매칭 로직을 세션 기반으로 안정화
        """)
      
