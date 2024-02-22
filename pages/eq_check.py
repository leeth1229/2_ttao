import pandas as pd
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import fitz  # PyMuPDF

st.set_page_config(layout="wide")

# PDF 파일 경로
pdf_path = "streamlit/docs/설비/회전설비.png"
# PDF 문서 열기
doc = fitz.open(pdf_path)

# 초기 세션 상태 설정
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0
    st.session_state.rotation = 0  # 페이지 회전 상태 초기화

# with st.sidebar:
#     st.write("## Page Rotation")
#     if st.button("Rotate 90° :leftwards_arrow_with_hook:"):
#         st.session_state.rotation = (st.session_state.rotation + 90) % 360
#     if st.button("Rotate -90° :arrow_right_hook:"):
#         st.session_state.rotation = (st.session_state.rotation - 90) % 360

# # 페이지 이동 버튼
# col1, col2 = st.columns(2)
# with col1:
#     if st.button('Previous Page'):
#         st.session_state.page_number = max(0, st.session_state.page_number - 1)
# with col2:
#     if st.button('Next Page'):
#         st.session_state.page_number = min(len(doc) - 1, st.session_state.page_number + 1)

# # 현재 페이지 로드 및 표시
# # 현재 및 다음 페이지 로드 및 표시
# current_page_number = st.session_state.page_number
# pages_to_show = [current_page_number]
# if current_page_number < len(doc) - 1:  # 다음 페이지가 존재하는 경우 추가
#     pages_to_show.append(current_page_number + 1)

# # 이미지 변환에 사용할 스케일링 매트릭스 정의 (너비 확장)
# scaling_matrix = fitz.Matrix(2.0, 2.0)  # 너비와 높이를 2배로 확장
# rotation_matrix = scaling_matrix.prerotate(st.session_state.rotation)

# page_num = pages_to_show[0]
# st.write(page_num)
# page = doc.load_page(page_num)
# pix = page.get_pixmap(matrix=rotation_matrix)  # 이미지 크기 조정 적용
# pix.set_dpi(pix.width, pix.height)
# image_bytes = pix.tobytes("png")


# Specify canvas parameters in application
drawing_mode = st.sidebar.selectbox(
    "Drawing tool:", (["rect"])
)

bg_image = pdf_path
stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 1)
stroke_color = st.sidebar.color_picker("Stroke color hex: ")
bg_color = st.sidebar.color_picker("Background color hex: ", "#eee")
realtime_update = st.sidebar.checkbox("Update in realtime", True)

# Create a canvas component
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    background_image=Image.open(bg_image) if bg_image else None,
    update_streamlit=True,
    width = 1800,
    height=1000,
    drawing_mode=drawing_mode,
    # point_display_radius=point_display_radius if drawing_mode == 'point' else 0,
    key="canvas",
)

# Do something interesting with the image data and paths
if canvas_result.json_data is not None:
    objects = pd.json_normalize(canvas_result.json_data["objects"]) # need to convert obj to str because PyArrow
    for col in objects.select_dtypes(include=['object']).columns:
        objects[col] = objects[col].astype("str")
    st.data_editor(objects,num_rows="dynamic",use_container_width=True)
    
