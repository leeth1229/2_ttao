import streamlit as st
import fitz  # PyMuPDF

# PDF 파일 경로
pdf_path = "streamlit/doc/test.pdf"

# PDF 문서 열기
doc = fitz.open(pdf_path)

# 아웃라인(목차) 추출
outlines = doc.get_toc(simple=False)

# 초기 세션 상태 설정
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0
    st.session_state.selected_title = "First Page..."

# Streamlit 앱 타이틀
st.title("PDF Viewer Navigation")

# 사이드바에 아웃라인 선택 UI 개선 및 페이지 직접 이동
with st.sidebar:
    st.write("## Navigation")
    # "First Page..." 버튼 추가
    if st.button("First Page..."):
        st.session_state.page_number = 0
        st.session_state.selected_title = "First Page..."

    # 아웃라인 항목 표시 (1레벨만)
    for outline in outlines:
        if len(outline) >= 3:
            level, title, page = outline[:3]
            if level == 1:  # 1레벨 아웃라인만 처리
                unique_key = f"{title}_{page}"  # 고유한 key 생성
                if st.button(title, key=unique_key):
                    st.session_state.page_number = page - 1
                    st.session_state.selected_title = title

    # 지정 페이지로 이동하는 텍스트 입력
    st.write("## Go to Page")
    page_input = st.text_input("Enter page number:", "")
    if page_input:
        try:
            page_number = int(page_input) - 1  # 사용자 입력을 페이지 번호로 변환 (0 기반 인덱싱)
            if 0 <= page_number < len(doc):
                st.session_state.page_number = page_number
            else:
                st.error("Page number out of range.")
        except ValueError:
            st.error("Please enter a valid page number.")

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
