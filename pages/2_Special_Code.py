import pandas as pd
import streamlit as st
import streamlit_antd_components as sac
from streamlit_image_coordinates import streamlit_image_coordinates
from streamlit_image_annotation import classification

import openpyxl
import re

import fitz  # PyMuPDF
from PIL import Image
from glob import glob
import io
import os
import matplotlib as plt

from function_search import add_to_cart

st.set_page_config(layout="wide")

# Define the root directory
file_path = 'streamlit/docs/items'

# Define a function to convert the directory structure to a tree structure
def convert_dir_to_tree(file_path):
    tree_items = []  # This will store the converted tree items.
    for level_1 in os.listdir(file_path):
        level_1_path = os.path.join(file_path, level_1)
        if level_1.startswith('.'):  # 숨겨진 파일이나 폴더 건너뛰기
            continue
        if os.path.isdir(level_1_path):
            item_1 = sac.TreeItem(level_1, disabled=True, tag=[sac.Tag('Plant', color='red'), sac.Tag('lv1', color='cyan')], children=[])
            for level_2 in os.listdir(level_1_path):
                level_2_path = os.path.join(level_1_path, level_2)
                if level_2.startswith('.'):
                    continue
                if os.path.isdir(level_2_path):
                    item_2 = sac.TreeItem(level_2, icon='table', tag=[sac.Tag('lv2', color='blue')], children=[])
                    for level_3 in os.listdir(level_2_path):
                        level_3_path = os.path.join(level_2_path, level_3)
                        if level_3.startswith('.'):
                            continue
                        if os.path.isdir(level_3_path):
                            item_3 = sac.TreeItem(level_3, icon='table', tag=[sac.Tag('lv3', color='green')], children=[])
                            item_2.children.append(item_3)
                    item_1.children.append(item_2)
            tree_items.append(item_1)
    return tree_items


def Item_path_find(file_path):
    Item_path = []
    # 기본 데이터 프레임 생성
    default_data = {
        '자재코드': [],
        'tag_no': [], # 설비 아이디 고유 번호
        'model_no': [], # 모델 번호
        'dwg_no': [], # 도면 고유 번호
        'item_no': [], # 파트 아이템 넘버
        'part_no': [], # 파트 고유 번호
        'VMI재고': [], # VMI 재고
        '구매재고': [], # 구매 재고
        '자재단가': [], # 구매 재고
        'special': [] # 비고
    }
    default_df = pd.DataFrame(default_data)
    
    for level1 in os.listdir(file_path):
        if level1.startswith('.'):  # 숨겨진 파일이나 폴더 건너뛰기
            continue
        folder_path_1 = os.path.join(file_path, level1)
        if os.path.isdir(folder_path_1):
            Item_path.append(folder_path_1)
            for level2 in os.listdir(folder_path_1):
                if level2.startswith('.'):
                    continue
                folder_path_2 = os.path.join(folder_path_1, level2)
                if os.path.isdir(folder_path_2):
                    Item_path.append(folder_path_2)
                    xlsx_path = os.path.join(folder_path_2, f'{level2}.xlsx')
                    # xlsx 파일이 존재하는 경우 컬럼 확인 및 업데이트
                    if os.path.exists(xlsx_path):
                        df = pd.read_excel(xlsx_path)
                        # 필요한 컬럼이 모두 있는지 확인하고 없으면 추가
                        for column in default_data.keys():
                            if column not in df.columns:
                                df[column] = None  # 새 컬럼 추가
                        df.to_excel(xlsx_path, index=False)  # 변경된 데이터프레임 저장
                    else:
                        default_df.to_excel(xlsx_path, index=False)  # 새 파일 생성

                    for level3 in os.listdir(folder_path_2):
                        if level3.startswith('.'):
                            continue
                        folder_path_3 = os.path.join(folder_path_2, level3)
                        if os.path.isdir(folder_path_3):
                            Item_path.append(folder_path_3)
                            xlsx_path_ = os.path.join(folder_path_3, f'{level3}.xlsx')
                            # xlsx 파일이 존재하는 경우 컬럼 확인 및 업데이트
                            if os.path.exists(xlsx_path_):
                                df = pd.read_excel(xlsx_path_)
                                for column in default_data.keys():
                                    if column not in df.columns:
                                        df[column] = None  # 새 컬럼 추가
                                df.to_excel(xlsx_path_, index=False)
                            else:
                                default_df.to_excel(xlsx_path_, index=False)  # 새 파일 생성
    return Item_path


# 검색 기능을 위한 Streamlit 입력 필드 추가
search_query = st.sidebar.text_input("Search Tag No.", "")

# 검색 로직을 포함하는 함수 정의
def search_tree_items(tree_items, query):
    if query == "":  # 검색어가 없으면 모든 항목을 반환
        return tree_items
    else:
        # 검색어가 포함된 항목만 필터링
        filtered_items = []
        for item in tree_items:
            if query.lower() in item.label.lower():  # 대소문자 구분 없이 검색
                filtered_items.append(item)
            else:
                # 자식 항목 중에서 검색
                child_matches = search_tree_items(item.children, query)
                if child_matches:
                    new_item = sac.TreeItem(item.label, disabled=True, children=child_matches)
                    filtered_items.append(new_item)
        return filtered_items

# Convert the directory structure to a tree structure
tree_items = convert_dir_to_tree(file_path)

# 검색 결과에 따라 트리 항목 업데이트
tree_items = search_tree_items(tree_items, search_query)

with st.sidebar:
    # Use the tree_items in your sac.tree
    sac.divider(label='Tag Trees', align='center', color='gray')
    
    if search_query != "": # 검색 시
        Item_ = sac.tree(
            items=tree_items,
            label='Tag No.',
            size='sm',
            color='#4682b4',
            index=1,
            open_all=True,
            checkbox=False,
            checkbox_strict=True
            )
        
        sac.divider(label='file path', align='center', color='gray')
        Item_path = Item_path_find(file_path)
        for path_ in Item_path:
            if os.path.basename(path_) == Item_:  # Matching the directory name
                df_boom_list_path = os.path.join(path_, f"{Item_}.xlsx")
                break
        st.write(df_boom_list_path)

    else: # 일반 
        Item_ = sac.tree(
            items=tree_items,
            label='Tag No.',
            size='sm',
            color='#4682b4',
            index=1,
            open_all=True,
            checkbox=False,
            return_index=True
            )

        sac.divider(label='file path', align='center', color='gray')
        Item_path = Item_path_find(file_path)
        st.write(Item_path)

        st.write(Item_)
        df_boom_list_path = os.path.join(Item_path[Item_], f"{os.path.basename(Item_path[Item_])}.xlsx")
        st.write(df_boom_list_path)

    sac.divider(label='file generator', align='center', color='gray')
    # 파일 및 폴더 관리 액션 선택
    action = st.sidebar.selectbox("Select action", ["None", "Create", "Rename", "Delete"])
                
    # 선택된 액션에 따라 로직 처리
    if action == "Create":
        new_file_folder = st.sidebar.text_input("Enter new file/folder name")
        if st.sidebar.button("Create"):
            os.makedirs(os.path.join(file_path, new_file_folder), exist_ok=True)
            st.sidebar.success(f"Created {new_file_folder}")

    elif action == "Rename":
        target = st.sidebar.text_input("Enter file/folder name to rename")
        new_name = st.sidebar.text_input("Enter new name")
        if st.sidebar.button("Rename"):
            os.rename(os.path.join(file_path, target), os.path.join(file_path, new_name))
            st.sidebar.success(f"Renamed {target} to {new_name}")

    elif action == "Delete":
        target = st.sidebar.text_input("Enter file/folder name to delete")
        if st.sidebar.button("Delete"):
            if os.path.isdir(os.path.join(file_path, target)):
                os.rmdir(os.path.join(file_path, target))  # 폴더 삭제
            else:
                os.remove(os.path.join(file_path, target))  # 파일 삭제
            st.sidebar.success(f"Deleted {target}")
                    
st.title("설비 전용자재 코드 list")


st.subheader("Code list")

if Item_ is not None:
    # Determine the cor rect Excel file path based on user selection
    if os.path.exists(df_boom_list_path):
        df_boom_list = pd.read_excel(df_boom_list_path)
        df_boom_list["bool"] = False
        edited_df_boom_list = st.data_editor(key='df_boom_list_editor',
                                             num_rows="dynamic", 
                                             use_container_width=False, 
                                             data=df_boom_list,
                                             )
    else:
        st.sidebar.write("No Excel file found for this folder.")

# 데이터를 엑셀 파일로 저장
if st.button('데이터 저장'):
    edited_df_boom_list.to_excel(df_boom_list_path, index=False)

st.subheader("설비도면")

def show_pdf_page(pdf_path, current_page, rotation_angle):
    doc = fitz.open(pdf_path)
    if current_page < 0:
        current_page = 0
    elif current_page >= len(doc):
        current_page = len(doc) - 1
    page = doc.load_page(current_page)
    
    # 페이지 회전 적용
    mat = fitz.Matrix(2, 2).prerotate(rotation_angle)
    
    pix = page.get_pixmap(matrix=mat)  # 수정된 매트릭스를 사용하여 이미지 생성
    img = Image.open(io.BytesIO(pix.tobytes()))
    doc.close()
    return img, current_page


# 선택된 항목에서 PDF 파일 찾기 및 초기 페이지 설정
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0  # 세션 상태에 현재 페이지 번호를 저장

if 'Item_' in locals() and Item_ is not None:
    item_folder = df_boom_list_path.rsplit('/', 1)[0]
    pdf_files = [file for file in os.listdir(item_folder) if file.endswith('.pdf')]
    if pdf_files:
        selected_pdf = st.selectbox('Select a PDF file:', pdf_files, key='pdf_select')
        pdf_path = os.path.join(item_folder, selected_pdf)

        # 페이지 넘김 및 회전 버튼
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if st.button('Previous Page'):
                st.session_state.current_page -= 1
            if st.button("Rotate -90°"):
                st.session_state.rotation -= 90

        with col3:
            if st.button('Next Page'):
                st.session_state.current_page += 1
            if st.button("Rotate 90°"):
                st.session_state.rotation += 90

        # 현재 페이지의 PDF 이미지 보여주기
        img, current_page = show_pdf_page(pdf_path, st.session_state.current_page, st.session_state.rotation)
        st.image(img, caption=f'Page {current_page + 1}', use_column_width=True)
