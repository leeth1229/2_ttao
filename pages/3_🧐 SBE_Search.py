import streamlit as st
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, util
# 모델 로드
model = SentenceTransformer("streamlit/doc/my_model")

# 화면 설정
st.set_page_config(
    layout="wide",
    page_title="SBE_Search",
    page_icon="🧐",
)

# 탭 생성
tab1, tab2, tab3, tab4, tab5 = st.tabs(["탭 1", "탭 2", "탭 3", "탭 4", "탭 5"])

with tab1:
    st.header("원본 SBE 리스트 [리플렉션 완료]")
    # 원본 데이터 뷰어, 랜덤하게 작성 양식을 약 5개 정도 디스플레이
    # 원본 데이터에 추가 기능 -> 탭 4까지 가면 전체 완료, 4이후 원본 추가 버튼 구현


with tab2:
    st.header("SBE 신규 작성 시트")
    #T2 위험성 리스크 & LG,강도, 빈도, 위험도1~25 // 신규 양식 생성
    #T2 M,강도, 빈도, 위험도1~25 자동 평가 버튼 반영
    st.title('질문과 답변 관리 시스템')

    # 파일 경로 설정 및 데이터 로드
    file_path = "streamlit/doc/sbe/SBE_data.xlsx"

    # 메인 화면에 대한 내용을 여기에 추가합니다.
    if 'df' not in st.session_state or st.button('Reset'):
        st.session_state.df = pd.read_excel(file_path)

    # 데이터 표시
    df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
    if 'df' not in st.session_state:
        df = st.session_state.df

    # 입력란 생성
    risk_ = st.text_input('위험성을 입력하세요', '')
    strength_ = st.text_input('강도을 입력하세요', '')
    frequency_ = st.text_input('빈도을 입력하세요', '')
    risk_level_ = st.text_input('위험도을 입력하세요', '')
    # risk_answer = st.text_input('대책사항을을 입력하세요', '')

    # 입력 데이터 처리
    if st.button('데이터 추가'):
        if risk_ and strength_ and frequency_ and risk_level_:
            # 질문과 답변을 DataFrame에 추가
            new_data = pd.DataFrame({'위험성': [risk_], '강도':[strength_],'빈도':[frequency_],'위험도':[risk_level_]})
            st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
            st.success('데이터가 추가되었습니다.')
            # 입력란 초기화 (선택적)
            st.experimental_rerun()
        else:
            st.error('질문과 답변을 모두 입력해주세요.')

    # 데이터를 엑셀 파일로 저장
    if st.button('데이터 저장'):
        df.to_excel(file_path, index=False)
        st.success('데이터가 SBE_data.xlsx 파일로 저장되었습니다.')
    # 탭 2에 대한 내용을 여기에 추가합니다.

with tab3:
    st.header("SBE 대책 평가 및 점수화 탭")
    # 탭 3에 대한 내용을 여기에 추가합니다.
    #T3 업체 대책 & LG,하인리 점수도1~5 기존 작성 데이터 불러와서 입력
    #T3 M,하인리 점수도1~5 자동 평가 데이터
    # 업체 대첵 입력 후 계산 시, 점수화 실시
    # 여기까지가 완료

with tab4:
    st.header("SBE 리플랙션 평가 탭")
    # 탭 4에 대한 내용을 여기에 추가합니다.
    #T4 리플렉션 이미지 & LG,Good or bad

with tab5:
    st.header("탭 5")
    # 탭 5에 대한 내용을 여기에 추가합니다.


    
    
#T6 M,Good or bad