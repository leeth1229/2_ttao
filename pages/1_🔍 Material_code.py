import streamlit as st
import dataiku
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
from function_search import search_SPEC_CLASS_data
from function_search import search_ITEM_data
from function_search import search_SIZE_data
from function_search import search_SUB_SIZE_data
from function_search import search_BASIC_MATERIAL_data
from function_search import search_RATING_data
from function_search import search_LIST_data
from function_search import Ai_search_ITEM_data
from function_search import Ai_search_ITEM_data_
from function_search import add_to_cart

##################### 설정 web #####################

st.set_page_config(
    layout="wide",
    page_title="Search_pro",
    page_icon="🔍",
)

##################### Data Load #####################

df_materail_original = load_data()
df_materail = df_materail_original
df_materail["bool"] = False

##################### sidebar web #####################

st.sidebar.title('AI Search :rocket:')

# 초기화
if 'df_materail' not in st.session_state:
    st.session_state.df_materail = df_materail

# 초기화
if 'df_materail_pro' not in st.session_state:
    st.session_state.df_materail_pro = pd.DataFrame()

# Create search box widget for 자재코드
search_code = st.sidebar.text_input('자재코드', value='', placeholder='Enter search term')
if search_code != '': # 코드 검색
    df_materail = search_CODE_data(df_materail,search_code)
        
# Create search box widget for SPEC_CLASS
search_class = st.sidebar.multiselect('SPEC_CLASS 선택', df_materail["SPEC_CLASS"].unique())
if search_class:
    df_materail = search_SPEC_CLASS_data(df_materail,search_class)

# Create search box widget for ITEM
search_item = st.sidebar.multiselect('ITEM 선택', df_materail["ITEM"].unique())
if search_item:
    df_materail = search_ITEM_data(df_materail,search_item)

# Create search box widget for SIZE
search_size = st.sidebar.selectbox('SIZE', ["All"] + sorted(df_materail["SIZE"].unique()))
if search_size != "All":
    df_materail = search_SIZE_data(df_materail,search_size)  

# Create search box widget for SUB_SIZE
search_sub_size = st.sidebar.selectbox('SUB_SIZE', ["All"] + sorted(df_materail["SUB_SIZE"].unique()))
if search_sub_size != "All": # 사이즈2 검색
    df_materail = search_SUB_SIZE_data(df_materail,search_sub_size)

# Create search box widget for BASIC_MATERIAL
search_basic_material = st.sidebar.multiselect('BASIC_MATERIAL 선택', df_materail["BASIC_MATERIAL"].unique())
if search_basic_material:
    df_materail = search_BASIC_MATERIAL_data(df_materail,search_basic_material)

# Create search box widget for RATING
search_rating = st.sidebar.text_input('RATING', value='', placeholder='Enter search term')
if search_rating != '': # 레이팅 검색
    df_materail = search_RATING_data(df_materail,search_rating)

# Create search box widget for LIST
search_list= st.sidebar.text_input('자재내역 검색', value='', placeholder='Enter search term')
if search_list != '': # 자재내역 검색
    df_materail = search_LIST_data(df_materail,search_list)

# Create search box widget for Ai search
st.sidebar.title('자재내역 Ai 검색 :fire:')
Ai_search_List = st.sidebar.text_input('*상단 Item 및 Size 선택 시 정확도 상승*', value='', placeholder='ex) 4inch,smls,A106,pipe....')
st.sidebar.write("*:white_check_mark: Ai Searchs 'Item & Size' are required!*")
df_materail_pro = pd.DataFrame()
if st.sidebar.button('검색'):
    if Ai_search_List != "":
        if search_item != "" and search_size != "All" : # 아이템이 공란이 아니고, 사이즈가 올이 아닐때
            Ai_search_List = ",".join([str(search_item[0])] + [search_size + "B"] + [Ai_search_List])
            df_materail_pro, search_term_processing = Ai_search_ITEM_data(df_materail, Ai_search_List)
            st.session_state.df_materail_pro  = df_materail_pro
        else:
            re.sub("\t", ",", Ai_search_List)
            df_materail_pro, search_term_processing = Ai_search_ITEM_data_(df_materail, Ai_search_List)
            st.session_state.df_materail_pro  = df_materail_pro
        st.sidebar.write(",".join(search_term_processing))

        df_materail_pro["bool"] = False
    else:
        st.session_state.df_materail_pro  = pd.DataFrame()

# Create Bulk Data button 추가
st.sidebar.title('Bulk Data Upload')
uploaded_files = st.sidebar.file_uploader("Bulk Data Upload", accept_multiple_files=True)

df_materail_bulk = pd.DataFrame()
# Create df_materail_bulk frame 
if st.sidebar.button('Input to Bulk list'):
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith('.csv'):
            df_materail_bulk_sum = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df_materail_bulk_sum = pd.read_excel(uploaded_file)
        else:
            st.warning(f"{uploaded_file.name} is not a valid file type. Only CSV and Excel files are allowed.")
            continue
        df_materail_bulk = pd.concat([df_materail_bulk, df_materail_bulk_sum], ignore_index=True)
    st.session_state.df_materail_bulk_list = df_materail_bulk

elif uploaded_files is None:
    st.session_state.df_materail_bulk_list = pd.DataFrame()

# Download Upload format button
with open("format.xlsx", 'rb') as my_file:
    df_materail_format = pd.DataFrame({"ITEM": ["pipe"], "SIZE": [2], "자재내역": ["smls, sch80, 304, pe"]}, index=[0])
    df_materail_format.to_excel('format.xlsx', index=False)
    st.sidebar.download_button(label = 'Download format', data = my_file, file_name = 'format.xlsx', mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# if st.sidebar.button('Download format.xlsx'):
#     st.session_state.Cart_dataframe.to_excel('format.xlsx', index=False)
#     st.download_button(label = 'Download Cart', data = my_file, file_name = 'format.xlsx', mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     st.success('Downloaded format.xlsx!')

##################### Main web #####################

# _Search Pro_
st.title('_Search Pro_ :blue[Ai] :man-running:')
# Search List
st.header('Search List :smiley_cat:')
st.write("Total", df_materail.shape[0])
edited_df_materail = st.data_editor(df_materail, key='df_materail_editor', use_container_width=True) #####################
if edited_df_materail is not None:
    df_materail = edited_df_materail

# 카트 추가 버튼 노말
if st.button('Add to cart'):
    df_materail_cart = add_to_cart(df_materail)
    st.session_state.Cart_dataframe = pd.concat([st.session_state.Cart_dataframe, df_materail_cart]).reset_index(drop=True)
    st.success('Add to cart!')

# 초기화
if 'Cart_dataframe' not in st.session_state:
    st.session_state.Cart_dataframe = pd.DataFrame()

# 인공지능 서치    
st.title('AI Search List :mag:')

edited_df_materail_pro = st.data_editor(st.session_state.df_materail_pro, key='df_materail_pro_editor', use_container_width=True) #####################
if edited_df_materail_pro is not None:
    df_materail_pro = edited_df_materail_pro

# 카트 추가 버튼 ai
if st.button('Add to cart.'):
    df_materail_cart = add_to_cart(df_materail_pro)
    st.session_state.Cart_dataframe = pd.concat([st.session_state.Cart_dataframe, df_materail_cart]).reset_index(drop=True)
    st.success('Add to cart!')

# 장바구니 타이틀 추가
st.header('Cart List :shopping_trolley:') 

# Reset Cart 버튼
if st.button('Reset Cart'):
    df_materail_cart = pd.DataFrame()
    st.session_state.Cart_dataframe = pd.DataFrame()

# # Selection Remove 버튼
# if st.button('Selection Remove from Cart'):
#     # 선택한 제품을 Cart_dataframe에서 삭제합니다.
#     selected_products = st.session_state.Cart_dataframe[st.session_state.Cart_dataframe['bool']]
#     if not selected_products.empty:
#         st.session_state.Cart_dataframe = st.session_state.Cart_dataframe.drop(selected_products.index, axis=0)
#     else:
#         st.warning('제품을 선택해주세요.')

# Display the cart dataframe
edited_cart_df_materail = st.data_editor(st.session_state.Cart_dataframe, num_rows="dynamic",key='cart_editor', use_container_width=True) #####################
if edited_cart_df_materail is not None:
    st.session_state.Cart_dataframe = edited_cart_df_materail

# Download Excel 버튼
with open("cart_list.xlsx", 'rb') as my_file:
    st.session_state.Cart_dataframe.to_excel('cart_list.xlsx', index=False)
    st.download_button(label = 'Download Cart :white_check_mark:', data = my_file, file_name = 'cart_list.xlsx', mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# if st.button('Download Cart'):
#     st.session_state.Cart_dataframe.to_excel('cart_list.xlsx', index=False)
#     st.success('Downloaded cart_list.xlsx')

# 초기화
if 'df_materail_bulk_list' not in st.session_state:
    st.session_state.df_materail_bulk_list = pd.DataFrame()

# 벌크데이터 타이틀 추가
st.header('Bulk List :clock230: :sweat_smile:')

# bulk search 버튼
if st.button('Bulk Search :hourglass:'):
    df_materail_bulk_finded = find_codes(st.session_state.df_materail_bulk_list, df_materail_original)
    st.session_state.df_materail_bulk_list = df_materail_bulk_finded
    st.success('Ai Search Complete')

# bulk list 추가
edited_bulk_df_materail = st.data_editor(st.session_state.df_materail_bulk_list, num_rows="dynamic",key='bulk_editor', use_container_width=True) 
if edited_bulk_df_materail is not None:
    st.session_state.df_materail_bulk_list = edited_bulk_df_materail

# Bulk Download Excel 버튼
with open("bulk_list.xlsx", 'rb') as my_file:
    st.session_state.df_materail_bulk_list.to_excel('bulk_list.xlsx', index=False)
    st.download_button(label = 'Download Bulk :white_check_mark:', data = my_file, file_name = 'bulk_list.xlsx', mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
############################################
