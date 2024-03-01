import pandas as pd
import streamlit as st
import streamlit_antd_components as sac
from PIL import Image
import openpyxl
import fitz  # PyMuPDF
import re
import os
import tempfile
import dataiku
import io
import math

from function_search import add_to_cart

st.set_page_config(layout="wide")

def get_folder_paths(file_paths):
    folder_paths = []
    for file_path in file_paths:
        folder_path = os.path.dirname(file_path)
        folder_paths.append(folder_path)
    return folder_paths

# Define a function to convert the directory structure to a tree structure
def convert_dir_to_tree(folder_paths):
    tree_items = []  # This will store the converted tree items.
    group_items = {}  # This will store the group items.

    for file_path in folder_paths:
        # Split the path into parts
        parts = file_path.strip("/").split("/")
        group_name = parts[0]  # The first part is always the group name

        # Ensure group item exists
        group_item = group_items.get(group_name)
        if group_item is None:
            group_item = sac.TreeItem(group_name, disabled=True, children=[], tag=[sac.Tag('Plant', color='red'), sac.Tag('lv1', color='cyan')])
            tree_items.append(group_item)
            group_items[group_name] = group_item

        # Iterate through the rest of the parts to build the tree structure
        current_item = group_item
        for folder_name in parts[1:]:
            # Check if the folder item already exists under the current item
            folder_item = None
            for child_item in current_item.children:
                if child_item.label == folder_name:
                    folder_item = child_item
                    break

            # If the folder item doesn't exist, create and append it
            if folder_item is None:
                folder_item = sac.TreeItem(folder_name, icon='table', tag=[sac.Tag('lv2', color='blue')], children=[])
                current_item.children.append(folder_item)
            
            # Move the current item pointer to the new or found folder item
            current_item = folder_item

    return tree_items

FOLDER = dataiku.Folder("ezuSeiHz")

list_files = FOLDER.list_paths_in_partition()

folder_paths = get_folder_paths(list_files)

tree_items = convert_dir_to_tree(folder_paths)

with st.sidebar:
    
    Item_ = sac.tree(
        items=tree_items,
        label='Tag No.',
        size='sm',
        color='#4682b4',
        index=1,
        open_all=True,
        checkbox=False,
        return_index=False,
        checkbox_strict = True
        )


    if not isinstance(Item_, list):
        Item_ = Item_.split(".")[0]
    else:
        Item_ = Item_[0].split(".")[0]
    
    for index,path in enumerate(folder_paths):
        if Item_ in path:
            tag_index = index
            break

    # st.write(tag_index)
    df_boom_list_path = f"{list_files[tag_index]}"

    default_data = {
        '자재코드': ["20240001"],
        'tag_no': ["GA-000"], # 설비 아이디 고유 번호
        'maker': ["LG.C"], # 설비 아이디 고유 번호
        'model_no': ["LGC24MODELS1"], # 모델 번호
        'dwg_no': ["DWG 2024 001"], # 도면 고유 번호
        'item_no': ["1"], # 파트 아이템 넘버
        'part_no': ["LG-Chem-1"], # 파트 고유 번호
        # '재고1': [], # VMI 재고
        # '재고2': [], # 구매 재고
        # '자재단가': [], # 구매 재고
        # '공장': [], # 중복 입력 가능토록
        'Description': ["Description"] # 비고
    }

    default_data_df = pd.DataFrame(default_data)

    # 선택된 액션에 따라 로직 처리


with FOLDER.get_download_stream(df_boom_list_path) as f:
    df_boom_list = pd.read_excel(f.read(), engine='openpyxl')

# 탭 생성
tab1, tab2 = st.tabs(["Special Code", "Help"])

with tab1:
    st.subheader("Code list")
    if Item_ is not None:
        if df_boom_list is not None:
            # Determine the correct Excel file path based on user selection
            if len(df_boom_list.index) == 0:
                df_boom_list = default_data_df
            df_boom_list["bool"] = False
            edited_df_boom_list = st.data_editor(data = df_boom_list,
                                                key='edited_key1',
                                                num_rows="dynamic", 
                                                use_container_width=True,
                                                column_config={
                                                    "자재코드": st.column_config.NumberColumn(
                                                        format  = "%u",
                                                        required = True
                                                        ),
                                                    "tag_no" : st.column_config.TextColumn(
                                                        default = df_boom_list["tag_no"].iloc[-1]
                                                        ),
                                                    "maker" : st.column_config.TextColumn(
                                                        default = df_boom_list["maker"].iloc[-1]
                                                        ),
                                                    "model_no" : st.column_config.TextColumn(
                                                        default = df_boom_list["model_no"].iloc[-1]
                                                        ),
                                                    "dwg_no" : st.column_config.TextColumn(
                                                        default = df_boom_list["dwg_no"].iloc[-1]
                                                        ),
                                                    "item_no" : st.column_config.NumberColumn(
                                                        format  = "%f",
                                                        # help = st.image("/home/dataiku/workspace/code_studio-versioned/streamlit/docs/exp/file_generator_exp.png")
                                                        ),
                                                    "part_no" : st.column_config.TextColumn(
                                                        ),
                                                    "비고" : st.column_config.Column(
                                                        ),
                                                    }
                                                )
        else:
            st.sidebar.write("No Excel file found for this folder.")

    if edited_df_boom_list is not None:
        df_boom_list = edited_df_boom_list


st.subheader("Drawing Viewing")
item_folder = df_boom_list_path.rsplit('/', 1)[0]

with tempfile.TemporaryDirectory() as temp_dir:
    for path in list_files:
        if path.startswith(item_folder) and path.endswith(".pdf"):
            with FOLDER.get_download_stream(path) as f:
                full_path = os.path.join(temp_dir, os.path.basename(path))
                data = f.read()
                with open(full_path, 'wb') as f:
                    f.write(data)
    pdf_list = os.listdir(temp_dir)

def show_pdf_page(pdf_path, current_page, rotation_angle):
    
    if not os.path.exists(pdf_path):
        # pdf_path가 존재하지 않는 경우, pdf_list에서 첫 번째 PDF 파일을 다운로드
        with FOLDER.get_download_stream(pdf_list[0]) as f:
            data = f.read()
            with open(pdf_path, 'wb') as f:
                f.write(data)

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

    if pdf_list:
        st.write(list_files)
        st.write(df_boom_list_path)
        st.write(item_folder)
        pdf_name = st.sidebar.selectbox("PDF 선택", pdf_list)
        
        pdf_path = os.path.join(item_folder,pdf_name)

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
    else: 
        st.markdown("필요 도면을 업데이트해주세요")
