# ===== 라이브러리 불러오기 =====
import streamlit as st
import pandas as pd
import plotly.express as px


# ===== 페이지 설정 =====
# [추가] 가장 먼저 실행되는 st 명령: 탭 제목과 넓은 화면 레이아웃 설정
st.set_page_config(page_title="Titanic 대시보드", layout="wide")


# ===== 데이터 불러오기 =====
# st.cache_data: 처음 한 번만 파일을 읽고, 그 뒤로는 저장해 둔 결과를 다시 사용
@st.cache_data
def load_data():
    # titanic.csv 파일 읽기
    return pd.read_csv("titanic.csv")


# ===== 함수: 필터 =====
# 조건에 맞는 승객만 골라내는 함수
def filter_data(df, sexes, classes, age_range):
    # 나이 범위의 최솟값과 최댓값 꺼내기
    min_age, max_age = age_range
    # 성별 목록에 포함되는지 확인
    cond_sex = df["sex"].isin(sexes)
    # 객실 등급(pclass) 목록에 포함되는지 확인
    cond_class = df["pclass"].isin(classes)
    # 나이가 범위 안에 있는지 확인 (양 끝 포함, 나이 결측치는 제외됨)
    cond_age = df["age"].between(min_age, max_age)
    # 세 조건을 모두 만족하는 행만 반환
    return df[cond_sex & cond_class & cond_age]


# ===== 함수: KPI =====
# 대시보드 상단 KPI 3개를 계산하는 함수
def kpi(df):
    # 데이터가 비어 있으면 0을 반환
    if df.empty:
        return 0, 0, 0
    # 승객 수 = 행 개수
    n_passengers = len(df)
    # 생존율(%) = survived 평균 × 100, 소수 첫째 자리 반올림
    survival_rate = round(df["survived"].mean() * 100, 1)
    # 평균 나이 (결측치는 자동 제외), 소수 첫째 자리 반올림
    mean_age = round(df["age"].mean(), 1)
    # 세 값을 함께 반환
    return n_passengers, survival_rate, mean_age


# ===== 함수: 차트 =====
# 객실 등급별 생존율(%) 막대그래프를 만드는 함수
def class_rate_bar(df):
    # 등급별 생존율(%) 계산 후 소수 첫째 자리 반올림
    rate = (df.groupby("pclass")["survived"].mean() * 100).round(1).reset_index()
    # 열 이름을 알아보기 쉽게 바꾸기
    rate.columns = ["등급", "생존율(%)"]
    # 숫자 등급을 "1등급" 같은 글자로 바꿔 축이 연속값으로 그려지지 않게 하기
    rate["등급"] = rate["등급"].astype(str) + "등급"
    # 막대그래프 만들기 (text로 막대 위에 값 표시)
    fig = px.bar(rate, x="등급", y="생존율(%)", text="생존율(%)",
                 title="객실 등급별 생존율")
    # 막대 바깥쪽(위)에 값 표시
    fig.update_traces(textposition="outside")
    # 그래프 반환
    return fig


# 생존 여부별 나이 히스토그램을 만드는 함수
def age_hist(df):
    # 원본을 건드리지 않도록 복사
    data = df.copy()
    # 0/1을 "사망"/"생존" 글자로 바꿔 범례를 읽기 쉽게 하기
    data["생존 여부"] = data["survived"].map({0: "사망", 1: "생존"})
    # 생존 여부로 색을 나눈 히스토그램 (겹쳐 그리기, 투명도 0.6)
    fig = px.histogram(data, x="age", color="생존 여부",
                       barmode="overlay", opacity=0.6,
                       title="생존 여부별 나이 분포")
    # 그래프 반환
    return fig


# ===== 화면: 제목 =====
# 데이터 불러오기 (캐시 사용)
df = load_data()

# 대시보드 제목 표시
st.title("타이타닉, 누가 살아남았나?")


# ===== 화면: 사이드바 =====
# 사이드바 제목
st.sidebar.header("필터")

# 성별 선택 (기본값: 모두 선택)
sexes = st.sidebar.multiselect("성별", ["male", "female"], default=["male", "female"])

# 객실 등급 선택 (기본값: 모두 선택)
classes = st.sidebar.multiselect("객실 등급", [1, 2, 3], default=[1, 2, 3])

# 나이 범위 선택 (0~80세, 기본값: 전체 범위)
age_range = st.sidebar.slider("나이 범위", 0, 80, (0, 80))


# ===== 화면: KPI =====
# 선택한 조건으로 데이터 필터하기
filtered = filter_data(df, sexes, classes, age_range)

# 필터된 데이터로 KPI 3개 계산
n_passengers, survival_rate, mean_age = kpi(filtered)

# 화면을 가로 3칸으로 나누기
col1, col2, col3 = st.columns(3)

# 첫째 칸: 승객 수
col1.metric("승객 수", f"{n_passengers}명")

# 둘째 칸: 생존율
col2.metric("생존율", f"{survival_rate}%")

# 셋째 칸: 평균 나이
col3.metric("평균 나이", f"{mean_age}세")


# ===== 화면: 차트 =====
# [추가] KPI 아래를 가로 2칸으로 나누기
left, right = st.columns(2)

# [추가] 왼쪽 칸: 객실 등급별 생존율 막대그래프
left.plotly_chart(class_rate_bar(filtered))

# [추가] 오른쪽 칸: 생존 여부별 나이 히스토그램
right.plotly_chart(age_hist(filtered))


# ===== 화면: 데이터 보기 =====
# [추가] 접었다 펼 수 있는 영역 만들기
with st.expander("데이터 보기"):
    # [추가] 필터된 표 보여 주기
    st.dataframe(filtered)
