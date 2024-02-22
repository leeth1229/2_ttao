import pandas as pd
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import fitz  # PyMuPDF
import io

st.set_page_config(layout="wide")

# PDF 파일 경로
pdf_path = "streamlit/doc/pdf/test.pdf"  # PDF 파일 경로
# PDF 문서 열기
doc = fitz.open(pdf_path)



# 초기 세션 상태 설정
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0
    st.session_state.rotation = 0  # 페이지 회전 상태 초기화
    st.session_state.canvas_data = {}  # 페이지별 캔버스 데이터 저장

with st.sidebar:
    st.write("## Page Rotation")
    if st.button("Rotate 90°"):
        st.session_state.rotation = (st.session_state.rotation + 90) % 360
    if st.button("Rotate -90°"):
        st.session_state.rotation = (st.session_state.rotation - 90) % 360

# 페이지 이동 버튼
col1, col2 = st.columns(2)
with col1:
    if st.button('Previous Page'):
        st.session_state.page_number = max(0, st.session_state.page_number - 1)
with col2:
    if st.button('Next Page'):
        st.session_state.page_number = min(len(doc) - 1, st.session_state.page_number + 1)

# 현재 페이지 로드 및 표시
current_page_number = st.session_state.page_number
scaling_matrix = fitz.Matrix(2.0, 2.0)  # 너비와 높이를 2배로 확장
rotation_matrix = scaling_matrix.prerotate(st.session_state.rotation)

# 현재 페이지의 PDF를 이미지로 변환
current_page = doc[current_page_number]  # 현재 페이지 선택
pix = current_page.get_pixmap(matrix=rotation_matrix)  # 회전 적용
img = Image.open(io.BytesIO(pix.tobytes("png")))  # PDF 페이지를 이미지로 변환

st.write(f"Page {current_page_number + 1}")  # 페이지 번호를 보여주기

# 초기 세션 상태 설정
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0
    st.session_state.rotation = 0  # 페이지 회전 상태 초기화

# 여기에 canvas_data 초기화 코드 추가
if 'canvas_data' not in st.session_state:
    st.session_state.canvas_data = {}  # 페이지별 캔버스 데이터 저장 초기화


# Specify canvas parameters in application
drawing_mode = st.sidebar.selectbox("Drawing tool:", ["rect"])
stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
stroke_color = st.sidebar.color_picker("Stroke color hex: ")
bg_color = st.sidebar.color_picker("Background color hex: ", "#ffffff")
realtime_update = st.sidebar.checkbox("Update in realtime", True)

# Load existing drawing for the current page or use a new canvas
initial_data = st.session_state.canvas_data.get(current_page_number)

# Create a canvas component with background image from current PDF page
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    background_image=img,
    update_streamlit=True,
    width=pix.width,
    height=pix.height,
    drawing_mode=drawing_mode,
    initial_drawing=initial_data,
    key=f"canvas_{current_page_number}",
)

# Save the current drawing to session state
st.session_state.canvas_data[current_page_number] = canvas_result.json_data

# Display drawing data if available
if canvas_result.json_data is not None:
    objects = pd.json_normalize(canvas_result.json_data["objects"])
    for col in objects.select_dtypes(include=['object']).columns:
        objects[col] = objects[col].astype("str")
    st.dataframe(objects)  # 데이터 프레임으로 변경
