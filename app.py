import streamlit as st
import pandas as pd
import random
import urllib.parse
import requests
import time

# 1. 페이지 설정
st.set_page_config(
    page_title="건대 맛집 랜덤 가이드", 
    page_icon="🐂", 
    layout="centered"
)

# 2. 실시간 공공데이터 API 불러오기 (서울 열린데이터 광장)
@st.cache_data(ttl=3600) # 1시간 동안 데이터 캐싱
def load_data_from_api():
    # 서울 열린데이터 광장 API (광진구 모범음식점 지정 현황)
    # 실제 배포 시 'sample' 대신 본인의 인증키 사용을 권장합니다.
    api_key = "sample" 
    url = f"http://openapi.seoul.go.kr:8088/{api_key}/json/GwangjinModelRestaurantDesignate/1/500/"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if 'GwangjinModelRestaurantDesignate' in data:
            rows = data['GwangjinModelRestaurantDesignate']['row']
            df = pd.DataFrame(rows)
            
            # API 영문 컬럼명을 기존 기획서의 한글 명칭으로 매핑
            column_mapping = {
                'UPSO_NM': '업소명',
                'UPTAE_NM': '업태명',
                'H_DONG': '행정동명',
                'MAIN_ED': '주된음식',
                'SITE_ADDR_RD': '소재지도로명'
            }
            df = df.rename(columns=column_mapping)
            
            # 데이터 전처리: 결측치 제거 및 앞뒤 공백 제거
            df = df.dropna(subset=['업소명', '행정동명'])
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str).str.strip()
                
            return df
        else:
            return pd.DataFrame()
    except:
        return pd.DataFrame()

df = load_data_from_api()

# 3. 메인 화면 구성
st.title("🍴 건대입구 맛집 가이드")
st.markdown("### **건국대 황소가 추천하는 오늘의 점심!**")

if not df.empty:
    # 4. 사이드바 필터 설정
    with st.sidebar:
        st.header("⚙️ 검색 필터")
        
        # 행정동 필터
        dong_options = sorted(df['행정동명'].unique().tolist())
        selected_dong = st.selectbox("📍 동네 선택", ["전체"] + dong_options)
        
        # 업태 필터
        cat_options = sorted(df['업태명'].unique().tolist())
        selected_category = st.selectbox("🎯 메뉴 카테고리", ["전체"] + cat_options)
        
        # 특정 식당 제외
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

    # 6. 황소 애니메이션 및 결과 출력
    if st.button("🐂 황소를 불러 맛집 찾기!", use_container_width=True):
        if query_df.empty:
            st.warning("선택하신 조건에 맞는 식당이 없습니다. 필터를 조정해 주세요!")
        else:
            # 랜덤 추천 식당 선정
            result = query_df.sample(n=1).iloc[0]
            
            # --- 황소 로딩 시뮬레이션 ---
            msg_placeholder = st.empty()
            with msg_placeholder.container():
                st.write("### 🐂 건국대 황소가 맛집을 향해 달려가는 중...")
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.005)
                    progress_bar.progress(i + 1)
            msg_placeholder.empty() # 로딩 문구 제거

            # --- 결과 카드 디자인 ---
            col1, col2 = st.columns([1, 2.5])
            
            with col1:
                # 건국대 공식 UI/황소 로고 이미지
                st.image("https://www.konkuk.ac.kr/images/sub/s01_05_02_img01.png", use_container_width=True)
            
            with col2:
                st.markdown(f"""
                    <div style="background-color: #f9f9f9; padding: 20px; border-radius: 15px; border: 3px solid #006940;">
                        <p style="color: #006940; font-weight: bold; margin-bottom: 5px;">🐂 황소가 콕 찍은 맛집!</p>
                        <h2 style="margin: 0; color: #333;">{result['업소명']}</h2>
                        <hr style="margin: 10px 0;">
                        <p style="margin: 5px 0;"><b>🍴 메뉴:</b> {result['주된음식']}</p>
                        <p style="margin: 5px 0;"><b>📍 위치:</b> {result['행정동명']}</p>
                        <p style="margin: 5px 0; font-size: 0.85em; color: #666;">{result['소재지도로명']}</p>
                    </div>
                """, unsafe_allow_html=True)

            # 지도 연결 버튼
            st.write("")
            search_query = f"광진구 {result['업소명']}"
            naver_url = f"https://map.naver.com/v5/search/{urllib.parse.quote(search_query)}"
            st.link_button("📍 네이버 지도에서 위치 확인하기", naver_url, use_container_width=True)

else:
    st.error("데이터를 불러오지 못했습니다. API 설정이나 네트워크 상태를 확인해주세요.")

st.markdown("---")
st.caption("© 2026 Konkuk University Language Education Center Helper")