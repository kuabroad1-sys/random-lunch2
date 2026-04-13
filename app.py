import streamlit as st
import pandas as pd
import random
import urllib.parse
import os

# 1. 페이지 설정
st.set_page_config(page_title="건대 맛집 랜덤 가이드", page_icon="🍴")

# 2. 데이터 불러오기 (따옴표 포함된 CSV 세부 설정 적용)
@st.cache_data
def load_data():
    file_name = "restaurants.csv"
    
    if not os.path.exists(file_name):
        st.error(f"❌ '{file_name}' 파일을 찾을 수 없습니다.")
        return pd.DataFrame()

    # 인코딩 순차 시도
    for enc in ['cp949', 'utf-8-sig', 'utf-8', 'euc-kr']:
        try:
            # quotechar를 지정하여 주소 안의 쉼표 때문에 칸이 밀리는 현상 방지
            df = pd.read_csv(file_name, encoding=enc, quotechar='"', skipinitialspace=True)
            break
        except:
            continue
    else:
        st.error("❌ 파일 인코딩 문제로 읽기에 실패했습니다.")
        return pd.DataFrame()
    
    # 데이터 정리: 컬럼명 및 값 앞뒤 공백 제거
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
        
    return df

df = load_data()

# 3. 메인 화면
st.title("🍴 건대입구 맛집 가이드")
st.info("행정동과 메뉴를 선택해 오늘 점심을 정해보세요!")

if not df.empty:
    # 4. 사이드바 필터
    with st.sidebar:
        st.header("⚙️ 검색 필터")
        
        # 행정동명 추출 (결측치 제거)
        dong_options = sorted([x for x in df['행정동명'].unique() if str(x) != 'nan'])
        selected_dong = st.selectbox("📍 동네 선택", ["전체"] + dong_options)
        
        # 업태명 추출
        cat_options = sorted([x for x in df['업태명'].unique() if str(x) != 'nan'])
        selected_category = st.selectbox("🎯 메뉴 카테고리", ["전체"] + cat_options)
        
        exclude_input = st.text_input("🚫 제외할 식당 (쉼표 구분)", "")
        exclude_list = [x.strip() for x in exclude_input.split(",") if x.strip()]

    # 5. 필터링 로직
    query_df = df.copy()
    
    if selected_dong != "전체":
        query_df = query_df[query_df['행정