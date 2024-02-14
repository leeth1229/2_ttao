import streamlit as st
import fitz  # PyMuPDF

# PDF 파일 경로
pdf_path = "streamlit/doc/test.pdf"

# PDF 문서 열기
doc = fitz.open(pdf_path)

# 아웃라인(목차) 추출
outlines = doc.get_toc(simple=False)

# # 아웃라인에서 제목과 페이지 매핑 및 레벨 정보 포함
# titles_to_pages = {}
# outline_options = ["Continuous..."]
# for item in outlines:
#     if len(item) >= 3:
#         level, title, page = item
#         indent_title = " " * (level - 1) * 4 + title  # 레벨에 따른 들여쓰기 적용
#         titles_to_pages[indent_title] = page - 1  # 페이지 번호를 0 기반으로 조정
#         outline_options.append(indent_title)

# 아웃라인에서 제목과 페이지 매핑
titles_to_pages = {}
outline_options = ["Continuous..."]
for item in outlines:
    level, title, page = item[:3]  # 변경된 부분: 첫 3개의 요소만 추출
    indent_title = " " * (level - 1) * 4 + title  # 레벨에 따른 들여쓰기 적용
    titles_to_pages[indent_title] = page - 1  # 페이지 번호를 0 기반으로 조정
    outline_options.append(indent_title)

# 초기 세션 상태 설정
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0
    st.session_state.selected_title = "Continuous..."

# 사이드바에 아웃라인 선택을 위한 Selectbox
selected_title = st.sidebar.selectbox(
    "Select Outline", 
    options=outline_options,
    index=outline_options.index(st.session_state.selected_title)
)

# 아웃라인을 통한 페이지 이동 (선택한 경우에만)
if selected_title in titles_to_pages and selected_title != "Continuous...":
    st.session_state.page_number = titles_to_pages[selected_title]
    st.session_state.selected_title = selected_title  # 선택된 제목 업데이트

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
if current_page_number < len(doc) - 1:  # 다음 페이지가 존재하는 경우 추가
    pages_to_show.append(current_page_number + 1)

# 이미지 변환에 사용할 스케일링 매트릭스 정의 (너비 확장)
scaling_matrix = fitz.Matrix(2.0, 2.0)  # 너비와 높이를 2배로 확장

# 페이지 이미지를 수평으로 나란히 표시
cols = st.columns(len(pages_to_show))
for idx, page_num in enumerate(pages_to_show):
    page = doc.load_page(page_num)
    pix = page.get_pixmap(matrix=scaling_matrix)  # 이미지 크기 조정 적용
    image_bytes = pix.tobytes("png")
    cols[idx].image(image_bytes, caption=f"Page {page_num + 1}", use_column_width=True)

doc.close()
