import streamlit as st
import pandas as pd
import random
import urllib.parse

# 1. 페이지 설정
st.set_page_config(page_title="건대 맛집 랜덤 가이드", page_icon="🎓")

# 2. 데이터 불러오기 (캐싱 처리)
@st.cache_data
def load_data():
    try:
        # 업로드한 파일 인코딩에 맞게 읽기 (EUC-KR/CP949 가능성 높음)
        df = pd.read_csv("restaurants.csv", encoding='cp949')
    except UnicodeDecodeError:
        df = pd.read_csv("restaurants.csv", encoding='utf-8')
    except FileNotFoundError:
        st.error("⚠️ 'restaurants.csv' 파일을 찾을 수 없습니다.")
        return pd.DataFrame()
    return df

df = load_data()

# 3. 메인 디자인
st.title("🍴 건대입구 맛집 가이드")
st.info("지역과 메뉴를 선택해 오늘 점심 메뉴를 정해보세요!")

if not df.empty:
    # 4. 사이드바 설정 (필터링)
    with st.sidebar:
        st.header("⚙️ 검색 필터")
        
        # 행정동명 필터 (화양동, 자양동 등)
        all_dong = ["전체"] + sorted(df['행정동명'].unique().tolist())
        selected_dong = st.selectbox("📍 동네 선택", all_dong)
        
        # 업태명 필터 (한식, 중식 등)
        all_categories = ["전체"] + sorted(df['업태명'].unique().tolist())
        selected_category = st.selectbox("🎯 메뉴 카테고리", all_categories)
        
        # 예외 식당
        exclude_input = st.text_input("🚫 제외할 식당 이름", "")
        exclude_list = [x.strip() for x in exclude_input.split(",") if x.strip()]

    # 5. 데이터 필터링 로직
    filtered_df = df.copy()
    
    if selected_dong != "전체":
        filtered_df = filtered_df[filtered_df['행정동명'] == selected_dong]
        
    if selected_category != "전체":
        filtered_df = filtered_df[filtered_df['업태명'] == selected_category]
        
    # 예외 식당 제거
    if exclude_list:
        filtered_df = filtered_df[~filtered_df['업소명'].isin(exclude_list)]

    # 6. 결과 출력
    if st.button("어떤 맛집을 갈까요?"):
        if filtered_df.empty:
            st.warning("선택하신 조건에 맞는 식당이 없습니다. 필터를 조정해 주세요!")
        else:
            # 필터링된 결과 중 랜덤 하나 선택
            target_row = filtered_df.sample(n=1).iloc[0]
            selected_name = target_row['업소명']
            selected_food = target_row['주된음식']
            selected_addr = target_row['소재지도로명']
            
            st.balloons()
            
            # 결과 박스 디자인
            st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #006940;">
                    <h4 style="margin: 0; color: #666;">추천 맛집</h4>
                    <h1 style="color: #006940; margin: 10px 0;">{selected_name}</h1>
                    <p style="margin: 5px 0;"><b>주요 메뉴:</b> {selected_food}</p>
                    <p style="margin: 5px 0; font-size: 0.9em; color: #555;">{selected_addr}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # 네이버 지도 링크
            search_query = f"광진구 {selected_name}"
            naver_url = f"https://map.naver.com/v5/search/{urllib.parse.quote(search_query)}"
            st.link_button("📍 네이버 지도에서 위치 확인하기", naver_url)
            
            # (추가 기능) 현재 조건의 식당 목록 보기
            with st.expander("현재 조건의 다른 식당들 보기"):
                st.write(filtered_df[['업소명', '업태명', '주된음식', '행정동명']])

st.markdown("---")
st.caption("건국대 주변 행정동 데이터를 기반으로 필터링합니다.")