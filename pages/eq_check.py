import pandas as pd
from PIL import Image
import streamlit as st
import streamlit_antd_components as sac
import fitz  # PyMuPDF
import re
import os

st.set_page_config(layout="wide")

# 초기 세션 상태 설정
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0
    st.session_state.rotation = 0  # 페이지 회전 상태 초기화

# Define the root directory
file_path = 'streamlit/docs/items'

# Define a function to convert the directory structure to a tree structure
def convert_dir_to_tree(file_path):
    tree_items = []  # This will store the converted tree items.
    for level_1 in os.listdir(file_path):
        # Check if the item is a directory
        if os.path.isdir(os.path.join(file_path, level_1)):
            # Create a new TreeItem for the first level
            item_1 = sac.TreeItem(level_1, disabled=True, tag=[sac.Tag('Plant', color='red')],children=[]) # 공장명
            for level_2 in os.listdir(os.path.join(file_path, level_1)):
                # Check if the item is a directory
                if os.path.isdir(os.path.join(file_path, level_1, level_2)):
                    # Create a new TreeItem for the second level
                    item_2 = sac.TreeItem(level_2,icon='table', children=[]) # 설비명
                    for level_3 in os.listdir(os.path.join(file_path, level_1, level_2)):
                        # Check if the item is a directory
                        if os.path.isdir(os.path.join(file_path, level_1, level_2, level_3)):
                            # Create a new TreeItem for the third level
                            item_3 = sac.TreeItem(level_3, icon='table',children=[]) # 추가 폴더
                            item_2.children.append(item_3)
                    item_1.children.append(item_2)
            tree_items.append(item_1)
    return tree_items

# Convert the directory structure to a tree structure
tree_items = convert_dir_to_tree(file_path)

with st.sidebar:
    # Use the tree_items in your sac.tree
    sac.divider(label='Tag Trees', align='center', color='gray')
    
    Item_ = sac.tree(
        items=tree_items,
        label='Tag No.',
        size='sm',
        color='#4682b4',
        open_all=True,
        checkbox=False,
        return_index=True
        )
    
    # 공장 폴더별로 csv 파일 생성 및 경로 추적
    Item_path = []
    for level1 in os.listdir(file_path): # 공장명
        folder_path_1 = os.path.join(file_path + "/" + level1) # 공장 경로
        Item_path.append(folder_path_1) # 경로 추적
        
        for level2 in os.listdir(folder_path_1): # 설비명
            folder_path_2 = os.path.join(folder_path_1 + "/" + level2) # 설비 경로
            if os.path.isdir(folder_path_1): # 폴더 추가 여부 확인
                Item_path.append(folder_path_2) # 경로 추적
                boom_path = os.path.join(folder_path_2 + "/" + f'{level2}.csv') # csv 파일 만들기
                if not os.path.exists(boom_path):
                    with open(boom_path, 'w') as f:
                        f.write('Material Code, tag_no, dwg_no ,item_no, part_no/n')

            for level3 in os.listdir(folder_path_2): # sub 폴더
                folder_path_3 = os.path.join(folder_path_2 + "/" + level3) # 설비 경로
                if os.path.isdir(folder_path_3): # 폴더 추가 여부 확인
                    Item_path.append(folder_path_3) # 경로 추적
                    boom_path_ = os.path.join(folder_path_3 + "/" + f'{level3}.csv') # csv 파일 만들기
                    if not os.path.exists(boom_path_):
                        with open(boom_path_, 'w') as f:
                            f.write('something\n')
                
                    
    st.write(Item_)
    st.write(Item_path)
    sac.divider(label='Code Match', align='center', color='gray')

if Item_ is None:
    st.image("streamlit/docs/items/OXO/OX-GB-101/회전설비.png")
else: 
    file_name = Item_path[Item_].split("/")[-1]
    df_boom_list_path = Item_path[Item_] + "/" + f"{file_name}.csv"
    st.sidebar.write(df_boom_list_path)
    df_boom_list = pd.read_csv(df_boom_list_path)
    st.data_editor(df_boom_list, num_rows="dynamic", use_container_width=True)


