import streamlit as st
import pandas as pd
import random
import urllib.parse
import os

# 1. 페이지 설정
st.set_page_config(page_title="건대 맛집 랜덤 가이드", page_icon="🎓")

# 2. 데이터 불러오기 함수 (경로 및 인코딩 에러 집중 해결)
@st.cache_data
def load_data():
    file_name = "restaurants.csv"
    
    # 파일이 실제로 존재하는지 확인
    if not os.path.exists(file_name):
        st.error(f"❌ '{file_name}' 파일을 찾을 수 없습니다. GitHub 리포지토리에 파일이 있는지 확인해주세요.")
        return pd.DataFrame()

    # 여러 인코딩 방식을 순차적으로 시도 (한글 깨짐 및 에러 방지)
    encodings = ['cp949', 'utf-8', 'euc-kr', 'utf-8-sig']
    df = None
    
    for enc in encodings:
        try:
            df = pd.read_csv(file_name, encoding=enc)
            break # 성공하면 루프 탈출
        except:
            continue
            
    if df is None:
        st.error("❌ 파일 읽기에 실패했습니다. CSV 파일의 형식을 확인해주세요.")
        return pd.DataFrame()
    
    # 데이터 전처리: 컬럼명 및 텍스트 앞뒤 공백 제거
    df.columns = df.columns.str.strip()
    # 텍스트 데이터인 컬럼만 골라서 공백 제거
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
        
    return df

# 데이터 로드
df = load_data()

# 3. 메인 화면
st.title("🍴 건대입구 맛집 가이드")

if df.empty:
    st.warning("데이터가 비어있습니다. CSV 파일을 확인해주세요.")
else:
    # 4. 사이드바 필터
    with st.sidebar:
        st.header("⚙️ 검색 필터")
        
        # 행정동명 (데이터에 있는 값 자동 추출)
        if '행정동명' in df.columns:
            dong_list = sorted(df['행정동명'].unique().tolist())
            selected_dong = st.selectbox("📍 동네 선택", ["전체"] + dong_list)
        else:
            st.error("'행정동명' 컬럼이 파일에 없습니다.")
            selected_dong = "전체"

        # 업태명
        if '업태명' in df.columns:
            cat_list = sorted(df['업태명'].unique().tolist())
            selected_category = st.selectbox("🎯 메뉴 카테고리", ["전체"] + cat_list)
        else:
            selected_category = "전체"

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

    # 6. 결과 출력
    if st.button("🍴 식당 추천받기"):
        if query_df.empty:
            st.warning("선택하신 조건에 맞는 식당이 없습니다.")
        else:
            result = query_df.sample(n=1).iloc[0]
            st.balloons()
            
            # 카드 디자인
            st.markdown(f"""
                <div style="background-color: #f9f9f9; padding: 25px; border-radius: 15px; text-align: center; border: 2px solid #006940; margin-top: 20px;">
                    <span style="background-color: #006940; color: white; padding: 5px 12px; border-radius: 50px; font-size: 0.8em;">{result.get('행정동명', '')}</span>
                    <h1 style="color: #006940; margin: 15px 0;">{result.get('업소명', '이름 없음')}</h1>
                    <p style="font-size: 1.1em; color: #333;">오늘의 메뉴: <b>{result.get('주된음식', '정보 없음')}</b></p>
                    <p style="font-size: 0.9em; color: #666;">📍 {result.get('소재지도로명', '주소 정보 없음')}</p>
                </div>
            """, unsafe_allow