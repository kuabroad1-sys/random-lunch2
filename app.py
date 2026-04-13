import streamlit as st
import pandas as pd
import random
import urllib.parse

# 1. 페이지 설정
st.set_page_config(page_title="건대 맛집 랜덤 가이드", page_icon="🎓")

# 2. 데이터 불러오기 (실제 CSV 형식 반영)
@st.cache_data
def load_data():
    try:
        # 업로드하신 파일은 콤마(,) 구분자이며, 한글 인코딩(CP949 또는 EUC-KR)일 확률이 높습니다.
        # 만약 에러가 나면 encoding='utf-8'로 바꿔보세요.
        df = pd.read_csv("restaurants.csv", encoding='utf-8') 
        
        # 필요한 컬럼만 추출 (업소명 -> name, 업태명 -> category)
        # 만약 파일의 컬럼명이 '업소명', '업태명'이 맞는지 확인해주세요.
        menu_dict = df.groupby('업태명')['업소명'].apply(list).to_dict()
        return menu_dict
    except FileNotFoundError:
        st.error("⚠️ 'restaurants.csv' 파일을 찾을 수 없습니다.")
        return {}
    except UnicodeDecodeError:
        # 한글 깨짐 방지용 (CP949로 재시도)
        df = pd.read_csv("restaurants.csv", encoding='cp949')
        menu_dict = df.groupby('업태명')['업소명'].apply(list).to_dict()
        return menu_dict

menu_data = load_data()

# 3. 메인 디자인
st.title("🍴 건대입구 맛집 가이드")
st.info("실제 데이터 기반으로 맛집을 추천해드립니다.")

if menu_data:
    with st.sidebar:
        st.header("⚙️ 설정")
        # '업태명' 리스트 (한식, 일식, 중식 등)
        category = st.selectbox("🎯 카테고리 선택", ["전체"] + list(menu_data.keys()))
        exclude_input = st.text_input("🚫 제외할 식당", "")
        exclude_list = [x.strip() for x in exclude_input.split(",") if x.strip()]

    candidates = []
    if category == "전체":
        for items in menu_data.values():
            candidates.extend(items)
    else:
        candidates = menu_data[category]

    final_list = [res for res in candidates if res not in exclude_list]

    if st.button("어떤 맛집을 갈까요?"):
        if not final_list:
            st.error("조건에 맞는 식당이 없습니다!")
        else:
            selected = random.choice(final_list)
            st.balloons()
            
            st.success(f"오늘의 추천 메뉴는? **[{selected}]** 입니다!")
            
            # 네이버 지도 링크 (검색어 보강)
            search_query = f"광진구 {selected}" 
            naver_url = f"https://map.naver.com/v5/search/{urllib.parse.quote(search_query)}"
            st.link_button("📍 네이버 지도에서 위치 확인하기", naver_url)

st.markdown("---")
st.caption("건국대 주변 모범음식점 데이터를 기반으로 합니다.")