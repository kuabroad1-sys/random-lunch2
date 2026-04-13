import streamlit as st
import pandas as pd
import random
import urllib.parse
import os
import time

# 1. 페이지 설정
st.set_page_config(
    page_title="건대 맛집 랜덤 가이드", 
    page_icon="🐂", 
    layout="centered"
)

# 2. 데이터 불러오기 (로컬 CSV 기반)
@st.cache_data
def load_data():
    file_path = "restaurants.csv"
    if not os.path.exists(file_path):
        st.error(f"⚠️ '{file_path}' 파일을 찾을 수 없습니다. GitHub에 파일을 업로드했는지 확인해주세요.")
        return pd.DataFrame()

    # 다양한 한글 인코딩 시도
    for enc in ['cp949', 'utf-8-sig', 'utf-8', 'euc-kr']:
        try:
            # 주소 내 쉼표 문제를 방지하기 위해 quotechar 설정
            df = pd.read_csv(file_path, encoding=enc, quotechar='"', skipinitialspace=True)
            break
        except:
            continue
    else:
        st.error("❌ 파일 읽기에 실패했습니다. CSV 인코딩을 확인해주세요.")
        return pd.DataFrame()
    
    # 데이터 전처리: 컬럼명 및 텍스트 데이터 공백 제거
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
        
    return df

df = load_data()

# 3. 메인 화면 구성
st.title("🍴 건대입구 맛집 가이드")
st.markdown("### **건국대 황소가 추천하는 오늘의 점심!**")

if not df.empty:
    # 4. 사이드바 필터 설정
    with st.sidebar:
        st.header("⚙️ 검색 필터")
        
        # 행정동 필터
        dong_options = sorted([x for x in df['행정동명'].unique() if str(x) != 'nan'])
        selected_dong = st.selectbox("📍 동네 선택", ["전체"] + dong_options)
        
        # 업태 필터
        cat_options = sorted([x for x in df['업태명'].unique() if str(x) != 'nan'])
        selected_category = st.selectbox("🎯 메뉴 카테고리", ["전체"] + cat_options)
        
        # 제외 식당 입력
        exclude_input = st.text_input("🚫 제외할 식당 이름 (쉼표 구분)", "")
        exclude_list = [x.strip() for x in exclude_input.split(",") if x.strip()]

    # 5. 필터링 로직
    query_df = df.copy()
    if selected_dong != "전체":
        query_df = query_df[query_df['행정동명'] == selected_dong]
    if selected_category != "전체":
        query_df = query_df[query_df['업태명'] == selected_category]
    if exclude_list:
        query_df = query_df[~query_df['업소명'].isin(exclude_list)]

    # 6. 결과 출력 (황소 애니메이션 효과)