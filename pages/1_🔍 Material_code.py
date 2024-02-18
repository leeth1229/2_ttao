import streamlit as st
import pandas as pd, numpy as np
import re
import altair as alt
import os

from function_search import load_data
from function_search import sentence_processing
from function_search import vmi_processing
from function_search import vmi_list_find
from function_search import embedding_rank
from function_search import find_codes
from function_search import search_CODE_data
from function_search import search_SIZE_data
from function_search import search_SUB_SIZE_data
from function_search import search_RATING_data
from function_search import search_ITEM_data
from function_search import search_LIST_data
from function_search import Ai_search_ITEM_data
from function_search import add_to_cart

###################################################
# 설정 셋팅

st.set_page_config(
    layout="wide",
    page_title="Search_pro",
    page_icon="🔍",
)

# Read recipe inputs
df = load_data()
df_original = df
df_pro = pd.DataFrame()
df_cart = pd.DataFrame()
df_bulk = pd.DataFrame()
df_format = pd.DataFrame({"ITEM": ["pipe"], "SIZE": [2], "자재내역": ["smls, sch80, 304, pe"]}, index=[0])

###################################################

st.title('Ai Search Pro ver 1.0.0')
st.sidebar.title('AI Search')
# Create search box widget for 자재코드
search_code = st.sidebar.text_input('자재코드', value='', placeholder='Enter search term')

# Create search box widget for ITEM
# 드롭박스 생성
search_item = st.sidebar.multiselect('ITEM 선택', df["ITEM"].unique())
# Create search box widget for SIZE
search_size = st.sidebar.text_input('SIZE', value='', placeholder='Enter search term')
# Create search box widget for SUB_SIZE
search_sub_size = st.sidebar.text_input('SUB_SIZE', value='', placeholder='Enter search term')
# Create search box widget for RATING
search_rating = st.sidebar.text_input('RATING', value='', placeholder='Enter search term')
# Create search box widget for LIST
st.sidebar.title('자재내역 검색')
search_list= st.sidebar.text_input('정확히 일치하게 검색 ex) A106,smls,...', value='', placeholder='Enter search term')
# Create search box widget for Ai search
Ai_search_List = st.sidebar.text_input('검색 순서상관 없음 ex) smls,A106,...', value='', placeholder='Enter search term')

# 사이드바에 Bulk Data Upload 버튼 추가
uploaded_files = st.sidebar.file_uploader("Bulk Data Upload", accept_multiple_files=True)

# 업로드된 파일들을 처리하여 df_bulk에 추가
if st.sidebar.button('input to bulk list'):
    df_bulk = pd.DataFrame()
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith('.csv'):
            df_bulk_sum = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df_bulk_sum = pd.read_excel(uploaded_file)
        else:
            st.warning(f"{uploaded_file.name} is not a valid file type. Only CSV and Excel files are allowed.")
            continue
        df_bulk = pd.concat([df_bulk, df_bulk_sum], ignore_index=True)
    st.session_state.df_bulk = df_bulk
elif uploaded_files is None:
    st.session_state.df_bulk = pd.DataFrame()

# Download Upload format 버튼
if st.sidebar.button('Download format.xlsx'):
    df_format.to_excel('format.xlsx', index=False)
    st.success('Downloaded format.xlsx!')
###################################################

# Filter dataframe based on search query
if search_code != '': # 코드 검색
    df = search_CODE_data(df,search_code)
if search_item:
    df = search_ITEM_data(df,search_item)
if search_size != '': # 사이즈 검색
    df = search_SIZE_data(df,search_size)   
if search_sub_size != '': # 사이즈2 검색
    df = search_SUB_SIZE_data(df,search_sub_size)   
if search_rating != '': # 레이팅 검색
    df = search_RATING_data(df,search_rating)
if search_list != '': # 자재내역 검색
    df = search_LIST_data(df,search_list)
if search_item and search_size and Ai_search_List: # AI 검색
    Ai_search_List = ",".join([search_item[0], search_size[0], " ", Ai_search_List])
    df_pro = Ai_search_ITEM_data(df, Ai_search_List)
if search_item != "" and search_size == '' and Ai_search_List: # AI 검색
    Ai_search_List = re.sub("\t",",",Ai_search_List)
    df_pro = Ai_search_ITEM_data(df, Ai_search_List)

###################################################

# 노말 서치
st.title('Search List')
df['bool'] = False

st.dataframe(df, use_container_width=True)

# 초기화
if 'Cart_dataframe' not in st.session_state:
    st.session_state.Cart_dataframe = pd.DataFrame()

# 카트 추가 버튼 노말
if st.button('Added to cart'):
    df_cart = add_to_cart(df)
    st.session_state.Cart_dataframe = pd.concat([st.session_state.Cart_dataframe, df_cart]).reset_index(drop=True)
    st.success('Added to cart!')

# 인공지능 서치
df_pro['bool'] = False
if df_pro.empty:
    df_pro = pd.DataFrame()
st.title('AI Search List')
st.dataframe(df_pro, use_container_width=True)

# 카트 추가 버튼 ai
if st.button('Added to cart_'):
    df_cart = add_to_cart(df_pro)
    st.session_state.Cart_dataframe = pd.concat([st.session_state.Cart_dataframe, df_cart]).reset_index(drop=True)
    st.success('Added to cart!')

###################################################

# 장바구니 타이틀 추가
st.title('Cart List')

# Reset Cart 버튼
if st.button('Reset Cart'):
    st.session_state.Cart_dataframe = pd.DataFrame()

if st.button('Remove from Cart'):
    selected_product = st.session_state.Cart_dataframe
    if selected_product is not None:
        # 선택한 제품을 Cart_dataframe에서 삭제합니다.
        st.session_state.Cart_dataframe = st.session_state.Cart_dataframe.drop(selected_product.index, axis=0)
    if st.session_state.Cart_dataframe.empty:
        st.session_state.Cart_dataframe  = pd.DataFrame()

# 장바구니 테이블 추가
st.dataframe(st.session_state.Cart_dataframe,use_container_width=True)

# Download Excel 버튼
if st.button('Download Cart'):
    st.session_state.Cart_dataframe.to_excel('cart_list.xlsx', index=False)
    st.success('Downloaded cart_list.xlsx')

###################################################

# 화면에 벌크데이터 추가
st.title('Bulk List')

###################################################

# bulk search 버튼
if st.button('Bulk Search'):
    df_bulk = find_codes(st.session_state.df_bulk,df_original)
    st.session_state.df_bulk = df_bulk
    st.success('Ai Search Complete')

# bulk list
st.session_state.df_bulk = df_bulk
st.dataframe(st.session_state.df_bulk, use_container_width=True)

# Bulk Download Excel 버튼
if st.button('Download Bulk'):
    st.session_state.df_bulk.to_excel('bulk_list.xlsx', index=False)
    st.success('Downloaded bulk_list.xlsx')

###################################################

# bool 해결 -> 데이터 에디터 필요
# 아이템 드롭박스 / 했음, 실시간 반영 가능?
# 사이즈 드롭박스 ? 
# ai 검색 시, 자동 반영 
# bulk 리스트 수정 방법 고민
# 시각화 대시보드 를 통해 공지 등록 