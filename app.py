import streamlit as st
import pandas as pd
import random
import urllib.parse

# 1. 페이지 설정
st.set_page_config(page_title="건대 맛집 랜덤 가이드", page_icon="🎓")

# 2. 데이터 불러오기 (한글 인코딩 및 공백 에러 방지)
@st.cache_data
def load_data():
    file_path = "restaurants.csv"
    try:
        # 윈도우용 한글 인코딩(CP949) 우선 시도
        df = pd.read_csv(file_path, encoding='cp949')
    except:
        try:
            # 실패 시 UTF-8 시도
            df = pd.read_csv(file_path, encoding='utf-8')
        except Exception as e:
            st.error(f"파일을 읽는 중 에러가 발생했습니다: {e}")
            return pd.DataFrame()
    
    # 데이터 전처리: 컬럼명 및 텍스트 앞뒤 공백 제거
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()
        
    return df

df = load_data()

# 3. 메인 화면 디자인
st.title("🍴 건대입구 맛집 가이드")
st.info("행정동과 메뉴를 선택해 오늘 점심을 정해보세요!")

if not df.empty:
    # 4. 사이드바 필터 설정
    with st.sidebar:
        st.header("⚙️ 검색 필터")
        
        # 행정동명 선택 (화양동, 자양동 등)
        dong_list = sorted(df['행정동명'].dropna().unique().tolist())
        selected_dong = st.selectbox("📍 동네 선택", ["전체"] + dong_list)
        
        # 업태명 선택 (한식, 중식 등)
        cat_list = sorted(df['업태명'].dropna().unique().tolist())
        selected_category = st.selectbox("🎯 메뉴 카테고리", ["전체"] + cat_list)
        
        # 제외 식당 입력
        exclude_input = st.text_input("🚫 제외할 식당 (쉼표 구분)", "")
        exclude_list = [x.strip() for x in exclude_input.split(",") if x.strip()]

    # 5. 필터링 로직
    query_df = df.copy()
    
    if selected_dong != "전체":
        query_df = query_df[query_df['행정동명'] == selected_dong]
        
    if selected_category != "전체":
        query_df = query_df[query_df['업태명'] == selected_category]
        
    if exclude_list:
        query_df = query_df[~query_df['업소명'].isin(exclude_list)]

    # 6. 결과 출력 (추천 버튼 클릭 시)
    if st.button("🍴 식당 추천받기"):
        if query_df.empty:
            st.warning("선택하신 조건에 맞는 식당이 없습니다! 필터를 조정해 보세요.")
        else:
            # 필터링된 데이터에서 무작위 1개 추출
            result = query_df.sample(n=