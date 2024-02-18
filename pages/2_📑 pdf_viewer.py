import streamlit as st
import fitz  # PyMuPDF

st.set_page_config(
    layout="wide",
    page_title="PDF_Viewer",
    page_icon="📑",
)

# PDF 파일 경로
pdf_path = "streamlit/doc/test.pdf"

# PDF 문서 열기
doc = fitz.open(pdf_path)

# 아웃라인(목차) 추출
outlines = doc.get_toc(simple=False)

# 초기 세션 상태 설정 (회전 상태 포함)
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0
if 'rotation' not in st.session_state:  # 회전 상태 초기화 추가
    st.session_state.rotation = 0

# Streamlit 앱 타이틀
st.title("PDF Viewer Navigation")

# 사이드바 UI
with st.sidebar:
    st.write("## Go to Page")
    page_input = st.text_input("Enter page number:", "")
    if page_input:
        try:
            page_number = int(page_input) - 1
            if 0 <= page_number < len(doc):
                st.session_state.page_number = page_number
            else:
                st.error("Page number out of range.")
        except ValueError:
            st.error("Please enter a valid page number.")
    
    st.write("## Page Rotation")
    if st.button("Rotate 90°"):
        st.session_state.rotation = (st.session_state.rotation + 90) % 360
    if st.button("Rotate -90°"):
        st.session_state.rotation = (st.session_state.rotation - 90) % 360

    st.write("## Navigation")
    for outline in outlines:
        level, title, page = outline[:3]
        # if level == 1:
        #     st.write(title)
        if level == 1:  # 여기서 1레벨 아웃라인만 처리
            unique_key = f"{title}_{page}"  # 고유한 key 생성
            if st.button(title, key=unique_key):
                st.session_state.page_number = page - 1

# 페이지 이동 버튼
col1, col2 = st.columns(2)
with col1:
    if st.button('Previous Page'):
        st.session_state.page_number = max(0, st.session_state.page_number - 1)
with col2:
    if st.button('Next Page'):
        st.session_state.page_number = min(len(doc) - 1, st.session_state.page_number + 1)

# 현재 및 다음 페이지 로드 및 표시
current_page_number = st.session_state.page_number
pages_to_show = [current_page_number]
if current_page_number < len(doc) - 1:
    pages_to_show.append(current_page_number + 1)

# 이미지 변환에 사용할 스케일링 매트릭스 정의 및 회전 적용
scaling_matrix = fitz.Matrix(2.0, 2.0)  # 스케일링
rotation_matrix = scaling_matrix.prerotate(st.session_state.rotation)  # 회전 적용 수정

# 페이지 이미지를 수평으로 나란히 표시
cols = st.columns(len(pages_to_show))
for idx, page_num in enumerate(pages_to_show):
    page = doc.load_page(page_num)
    pix = page.get_pixmap(matrix=rotation_matrix)  # 회전 적용
    image_bytes = pix.tobytes("png")
    cols[idx].image(image_bytes, caption=f"Page {page_num + 1}", use_column_width=True)

doc.close()
