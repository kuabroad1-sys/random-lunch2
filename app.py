import streamlit as st
import pandas as pd
import random
import urllib.parse

# 1. 페이지 설정
st.set_page_config(page_title="건대 맛집 랜덤 가이드", page_icon="🎓")

# 2. 데이터 불러오기 (엑셀/CSV 파일)
@st.cache_data # 데이터를 매번 읽지 않고 캐싱하여 속도 향상
def load_data():
    try:
        # CSV 파일을 읽어옵니다. (파일명이 restaurants.csv여야 함)
        df = pd.read_csv("restaurants.csv")
        # 카테고리별로 리스트화
        menu_dict = df.groupby('category')['name'].apply(list).to_dict()
        return menu_dict
    except FileNotFoundError:
        st.error("⚠️ 'restaurants.csv' 파일을 찾을 수 없습니다. 파일을 업로드해주세요!")
        return {}

menu_data = load_data()

# 3. 메인 디자인
st.title("🍴 건대입구 맛집 가이드 (Excel 연동형)")
st.info("엑셀 파일에 등록된 맛집 중 오늘 갈 곳을 골라드립니다.")

if menu_data:
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        category = st.selectbox("🎯 카테고리 선택", ["전체"] + list(menu_data.keys()))
        exclude_input = st.text_input("🚫 제외할 식당 (쉼표 구분)", "")
        exclude_list = [x.strip() for x in exclude_input.split(",") if x.strip()]

    # 필터링 로직
    candidates = []
    if category == "전체":
        for items in menu_data.values():
            candidates.extend(items)
    else:
        candidates = menu_data[category]

    final_list = [res for res in candidates if res not in exclude_list]

    # 추첨 버튼
    if st.button("어떤 맛집을 갈까요?"):
        if not final_list:
            st.error("조건에 맞는 식당이 없습니다!")
        else:
            selected = random.choice(final_list)
            st.balloons()
            
            st.success(f"오늘의 추천 메뉴는? **[{selected}]** 입니다!")
            
            # 네이버 지도 링크
            search_query = f"건대 {selected}"
            naver_url = f"https://map.naver.com/v5/search/{urllib.parse.quote(search_query)}"
            st.link_button("📍 네이버 지도에서 위치 확인하기", naver_url)

st.markdown("---")
st.caption("© 2026 Konkuk Language Education Center")