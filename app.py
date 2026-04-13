import streamlit as st
import pandas as pd
import random
import urllib.parse
import requests
import time

# 1. 페이지 설정
st.set_page_config(page_title="건대 맛집 랜덤 가이드", page_icon="🎓")

# 2. 데이터 불러오기 (API 연동)
@st.cache_data(ttl=3600)
def load_data_from_api():
    api_key = "sample" # 실사용 시 본인의 인증키로 교체 권장
    url = f"http://openapi.seoul.go.kr:8088/{api_key}/json/GwangjinModelRestaurantDesignate/1/500/"
    
    try:
        response = requests.get(url)
        data = response.json()
        if 'GwangjinModelRestaurantDesignate' in data:
            rows = data['GwangjinModelRestaurantDesignate']['row']
            df = pd.DataFrame(rows)
            # 컬럼 매핑
            df = df.rename(columns={
                'UPSO_NM': '업소명', 'UPTAE_NM': '업태명',
                'H_DONG': '행정동명', 'MAIN_ED': '주된음식',
                'SITE_ADDR_RD': '소재지도로명'
            })
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

df = load_data_from_api()

# 3. 메인 화면
st.title("🍴 건대입구 맛집 가이드")

if not df.empty:
    with st.sidebar:
        st.header("⚙️ 검색 필터")
        dong_list = sorted([x for x in df['행정동명'].unique() if x and str(x) != 'nan'])
        selected_dong = st.selectbox("📍 동네 선택", ["전체"] + dong_list)
        
        cat_list = sorted([x for x in df['업태명'].unique() if x and str(x) != 'nan'])
        selected_category = st.selectbox("🎯 메뉴 카테고리", ["전체"] + cat_list)

    # 4. 결과 출력 로직
    if st.button("🐂 황소를 불러 맛집 찾기!"):
        # 필터링
        query_df = df.copy()
        if selected_dong != "전체":
            query_df = query_df[query_df['행정동명'] == selected_dong]
        if selected_category != "전체":
            query_df = query_df[query_df['업태명'] == selected_category]
            
        if query_df.empty:
            st.warning("조건에 맞는 식당이 없습니다.")
        else:
            result = query_df.sample(n=1).iloc[0]
            
            # --- 황소 달려오는 애니메이션 효과 시뮬레이션 ---
            placeholder = st.empty()
            with placeholder.container():
                st.write("### 🐂 건국대 황소가 맛집을 향해 달려가는 중...")
                # 황소 이미지가 왼쪽에서 오른쪽으로 이동하는 느낌의 진행 바
                progress_bar = st.progress(0)
                for percent_complete in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(percent_complete + 1)
            
            # 애니메이션 후 결과 출력
            placeholder.empty() # 로딩 문구 제거
            
            # 결과 카드 및 황소 이미지 출력
            col1, col2 = st.columns([1, 3])
            with col1:
                # 건국대 공식 황소 로고 또는 캐릭터 이미지 URL
                st.image("https://www.konkuk.ac.kr/images/sub/s01_05_02_img01.png", width=150)
            
            with col2:
                st.markdown(f"""
                    <div style="background-color: #f9f9f9; padding: 20px; border-radius: 15px; border: 3px solid #006940;">
                        <h4 style="color: #006940; margin: 0;">황소가 찾은 오늘의 맛집!</h4>
                        <h1 style="margin: 10px 0;">{result['업소명']}</h1>
                        <p><b>메뉴:</b> {result['주된음식']} | <b>위치:</b> {result['행정동명']}</p>
                    </div>
                """, unsafe_allow_html=True)

            search_query = f"광진구 {result['업소명']}"
            naver_url = f"https://map.naver.com/v5/search/{urllib.parse.quote(search_query)}"
            st.link_button("📍 네이버 지도에서 위치 확인하기", naver_url)

st.markdown("---")
st.caption("© 2026 Konkuk University Staff Helper")