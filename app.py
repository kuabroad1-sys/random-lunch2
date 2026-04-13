import streamlit as st
import pandas as pd
import random
import urllib.parse

# 1. 페이지 설정
st.set_page_config(page_title="건대 맛집 랜덤 가이드", page_icon="🎓")

# 2. 데이터 불러오기 (에러 방지용 인코딩 처리)
@st.cache_data
def load_data():
    file_path = "restaurants.csv"
    try:
        # 윈도우 계열 한글 인코딩(CP949)으로 먼저 시도
        df = pd.read_csv(file_path, encoding='cp949')
    except:
        try:
            # 실패 시 UTF-8로 시도
            df = pd.read_csv(file_path, encoding='utf-8')
        except Exception as e:
            st.error(f"파일을 읽는 중 에러가 발생했습니다: {e}")
            return pd.DataFrame()
    
    # 데이터 양쪽 공백 제거 (매칭 에러 방지)
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
        # 데이터에 NaN(결측치)이 있을 경우를 대비해 처리
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

    # 6. 결과 출력
    if st.button("🍴 식당 추천받기"):
        if query_df.empty:
            st.warning("선택하신 조건에 맞는 식당이 없습니다! 필터를 조정해 보세요.")
        else:
            # 랜덤 선택
            result = query_df.sample(n=1).iloc[0]
            
            st.balloons()
            
            # 결과 카드 디자인
            st.markdown(f"""
                <div style="background-color: #f9f9f9; padding: 25px; border-radius: 15px; text-align: center; border: 2px solid #006940; margin-top: 20px;">
                    <span style="background-color: #006940; color: white; padding: 5px 12px; border-radius: 50px; font-size: 0.8em;">{result['행정동명']}</span>
                    <h1 style="color: #006940; margin: 15px 0;">{result['업소명']}</h1>
                    <p style="font-size: 1.1em; color: #333;">오늘의 메뉴: <b>{result['주된음식']}</b></p>
                    <p style="font-size: 0.9em; color: #666;">📍 {result['소재지도로명']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # 지도 연결
            search_query = f"광진구 {result['업소명']}"
            naver_url = f"https://map.naver.com/v5/search/{urllib.parse.quote(search_query)}"
            st.link_button("📍 네이버 지도에서 위치 보기", naver_url)

    # 하단 데이터 미리보기 (선택 사항)
    with st.expander("현재 조건에 맞는 식당 전체 보기"):
        st.dataframe(query_df[['업소명', '업태명', '주된음식', '행정동명', '소재지도로명']])

else:
    st.error("데이터를 불러오지 못했습니다. 파일명과 인코딩을 확인해주세요.")

st.markdown("---")
st.caption("© 2026 Konkuk University Staff Helper")