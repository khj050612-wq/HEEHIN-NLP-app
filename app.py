import streamlit as st
from kiwipiepy import Kiwi
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

# 1. 페이지 설정 및 분석기 초기화
st.set_page_config(page_title="아동 발달 분석기", layout="wide")

@st.cache_resource
def load_kiwi():
    return Kiwi()

kiwi = load_kiwi()

# 2. 시나리오별 데이터 설정
EXAMPLES = {
    "A": "엄마 사탕 줘. 아빠 이거 뭐야? 멍멍이 예쁘다. 나 우유 먹어. 선생님 안녕. 뽀로로 보여줘. 이거 내 거야. 아기 자요. 물 많이 줘. 엄마 같이 가.", 
    "B": "엄마. 사탕. 물. 우유. 까까. 신발. 사과. 아빠. 멍멍이. 아기.", 
    "C": "사탕 줄까? 사탕 줄까? 뽀로로가 나타났다. 뽀로로가 나타났다. 이거 뭐야? 이거 뭐야?" 
}

# 3. 메인 타이틀 및 서비스 목적 (회색 멘트)
st.title("👶 우리 아이 언어 발달 비교 분석기")
st.caption("""
본 서비스는 인공지능 기술을 활용하여 학부모가 아이의 발화 데이터를 객관적으로 확인하고,  
또래 발달 수준과 비교해 볼 수 있도록 돕는 언어발달 모니터링 보조 도구입니다.  

아이의 언어 환경을 이해하고 건강한 성장을 지원하는 기초 자료로 활용해 보세요.
""")
st.divider()

# 4. 아이 정보 입력 (자동 연령 계산)
st.subheader("📝 1. 아이 정보를 입력해주세요")
c1, c2, c3, c4 = st.columns([2, 1, 1, 2])

with c1:
    child_name = st.text_input("아이 이름", "엘리자베스")
with c2:
    this_year = datetime.date.today().year
    birth_year = st.selectbox("출생 연도", range(this_year, this_year - 11, -1), index=2)
with c3:
    birth_month = st.selectbox("출생 월", range(1, 13), index=datetime.date.today().month - 1)

# 개월 수 계산 및 비교군 자동 매칭
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

st.write("💡 아래 버튼을 누르면 각 발달 유형별 예시 데이터가 자동으로 채워집니다.")
col_ex1, col_ex2, col_ex3 = st.columns(3)

if col_ex1.button("✅ 정상 발달 예시"):
    st.session_state.input_text = EXAMPLES["A"]
    st.session_state.current_case = "normal"
    st.rerun()
if col_ex2.button("⚠️ 발달 지체 예시"):
    st.session_state.input_text = EXAMPLES["B"]
    st.session_state.current_case = "delay"
    st.rerun()
if col_ex3.button("🧩 자폐 성향 예시"):
    st.session_state.input_text = EXAMPLES["C"]
    st.session_state.current_case = "autism"
    st.rerun()

user_input = st.text_area("문장을 직접 입력하거나 위 버튼을 눌러보세요.", 
                          value=st.session_state.input_text, height=150)

# 가상 비교 데이터 수치
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
        
        # 그래프 데이터 설정
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

        # 7. 맞춤형 결과 분석 메시지 (부드러운 버전)
        st.divider()
        st.write("#### ✨ 우리 아이 발달 특성 요약")

        if st.session_state.current_case == "autism":
            st.info("💡 **확인이 필요한 발화 패턴이 관찰됩니다**")
            st.write("""
            상대방의 말을 그대로 따라 하거나 특정 문장을 반복하는 모습이 보입니다.  
            이러한 **반향어** 패턴은 아이가 의사소통의 의도를 찾아가는 과정일 수 있으나,  
            조금 더 정확한 이해를 위해 전문가와 편안하게 상담해 보시는 것을 추천드려요.
            """)
        elif st.session_state.current_case == "delay":
            st.warning("💡 **문장 확장 연습이 도움이 될 수 있어요**")
            st.write(f"""
            현재 {child_name}는 이름이나 사물(명사)을 말하는 것에 익숙해진 단계인 것 같아요.  
            '사과'라고 말할 때 **'사과 먹자', '사과 맛있다'**처럼 움직임이나 상태를 나타내는 말을  
            조금 더 섞어서 들려주시면 문장이 쑥쑥 자라날 거예요.
            """)
        elif st.session_state.current_case == "normal":
            st.success("💡 **또래와 비슷하게 무럭무럭 자라고 있어요**")
            st.write(f"""
            명사, 동사, 형용사를 골고루 사용하며 예쁘게 말하고 있네요!  
            지금처럼 {child_name}의 말에 귀 기울여 주시고, 풍부한 반응을 보여주시는 것만으로도  
            아이에겐 가장 좋은 언어 교육이 됩니다.
            """)
        else:
            st.write("입력하신 문장을 바탕으로 분석한 결과입니다. 구체적인 수치는 상단 그래프를 참고해 주세요.")
            
    else:
        st.error("분석할 문장을 입력해주세요.")

st.divider()
st.info("⚠️ 해당 분석은 수업 과제용 가상 연령별 수치를 기준으로 분석한 결과입니다.")
