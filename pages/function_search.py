import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import dataiku
import re
import os
import tempfile

from sentence_transformers import SentenceTransformer, util

################ 모델 Load ########################

my_model = dataiku.Folder("IXPPMAD5")

with tempfile.TemporaryDirectory() as temp_dir:
    for path in my_model.list_paths_in_partition():
        if len(path.split("/")) == 2:
            with my_model.get_download_stream(path) as stream:
                data = stream.read()
                full_path = os.path.join(temp_dir, os.path.basename(path))
                with open(full_path, 'wb') as f:
                    f.write(data)
        elif len(path.split("/")) == 3:
            folder_path = os.path.join(temp_dir, path.split("/")[1])
            os.makedirs(folder_path, exist_ok=True)
            with my_model.get_download_stream(path) as stream:
                data = stream.read()
                full_path = os.path.join(folder_path, os.path.basename(path))
                with open(full_path, 'wb') as f:
                    f.write(data)
    model = SentenceTransformer(temp_dir)

################ 모델 Load ########################

def load_data():
    # df = dataiku.Dataset("vmi_r6")
    # df = df.get_dataframe()
    df_path = "/home/dataiku/workspace/code_studio-versioned/streamlit/doc/VMI_Data/vmi_r6.xlsx"
    df = pd.read_excel(df_path)
    df = vmi_processing(df)
    df = df.astype(str)
    return df

def sentence_processing_ai(sentence):
    sentence_ = re.sub(" ",",",sentence.upper())
    sentence_ = sentence_.split(",")

    df_item=pd.DataFrame()

    questions_item = [
        "is it Pipe?, please Reference to ASTM",
        "is it valve?",
        "is it reducer-c?",
        "is it reducer-e?",
        "is it Flange?",
        "is it flange-Blind?",
        "is it cap?",
        "is it coupling-full?",
        "is it elbow-90degree?",
        "is it elbow-90degree and Long Radius?",
        "is it elbow-45degree?",
        "is it boss-90degree?",
        "is it boss-45degree?",
        "is it elbow-45degree and Long Radius?",
        "is it elobw-90degree and Shot Radius?",
        "is it Nipple?",
        "is it plug?",
        "is it Swage-c?",
        "is it Swage-e?",
        "is it Tee-E?",
        "is it Tee-R?",
        "is it union?",
        "is it Blank?",
        "is it spacer?",
        "is it gasket?",
        "is it weldolet?"
    ]

    df_item["questions"] = pd.DataFrame(questions_item)
    df_item["Item"] = ["Pipe",
                "valve",
                "reducer-c",
                "reducer-e",
                "Flange",
                "Flange-bl",
                "cap",
                "coupling-f",
                "elbow-90d",
                "elbow-90d/lr",
                "elbow-45d",
                "boss-90d",
                "boss-45d",
                "elbow-45d/lr",
                "elbow-90d/sr",
                "Nipple",
                "plug",
                "Swage-c",
                "Swage-e",
                "Tee-E",
                "Tee-R",
                "union",
                "Blank",
                "spacer",
                "gasket",
                "weldolet"
                ]
    df_item["Item"] = df_item["Item"].str.upper()
    passage_embedding = model.encode(sentence) # 문장 임베딩
    query_embedding = model.encode(df_item["questions"])
    df_item["cos"] = util.cos_sim(query_embedding,passage_embedding)
    df_item = df_item.sort_values(by='cos', ascending=False).reset_index(drop=True)
    item = df_item["Item"][0] # 아이템은 무엇인가?

    df_size = pd.DataFrame()
    questions_size = "What is the size?"
    df_size["sentence_"] = pd.DataFrame(sentence_)
    passage_embedding = model.encode(sentence_) # 문장 임베딩
    query_embedding = model.encode(questions_size) # 질문 임베딩
    df_size["euc"] = util.cos_sim(passage_embedding,query_embedding)

    df_size = df_size.sort_values(by='euc', ascending=False)
    df_size = df_size.reset_index(drop=True)
    size = df_size["sentence_"][0] # 사이즈는 무엇인가?

    sentence_ = [w for w in sentence_ if w not in [item, size]]
    sentence_ = [item] + [size] + sentence_
    sentence_ = ",".join(sentence_)
    return sentence_

def sentence_processing(sentence):
    """
    문장으로 검색 할 시, SIZE 관련 문장을 처리하여 분할된 단어 리스트 를 반환합니다.
    - 따옴표(")를 B로 변경합니다.
    - 쉼표(,)를 기준으로 문장을 분할합니다.
    - 각 부분을 공백으로 다시 분할하여 최종 단어 리스트를 생성합니다.
    """
    sentence = re.sub(" \" ", "B", sentence)  # 따옴표(")를 B로 변경
    sentence = re.sub("INCH", "B", sentence.upper())  # 따옴표(INCH)를 B로 변경
    processed = sentence.split(",")  # 쉼표로 분할
    processed = [value.strip() for value in processed]  # 각 부분의 공백 제거
    processed = [value.split(" ") for value in processed]  # 공백으로 다시 분할
    processed = [item for sublist in processed for item in sublist]  # 중첩 리스트 평탄화
    
    return processed


def vmi_processing(df):

    df_original = df
    df = df_original.copy() # 오리지날 카피
  
    #SIZE 변경 숫자로 된 형태를 변경
    size_dict = {0.25: "1/4", 0.375: "3/8", 0.5: "1/2", 0.75: "3/4", 1.25: "1-1/4", 1.5: "1-1/2", 2.5: "2-1/2"}
    df["SIZE"] = df["SIZE"].apply(lambda x: size_dict[x] if x in size_dict else f"{int(x)}" ) #SIZE 변경 숫자로 된 형태를 변경
    df["SUB_SIZE"] = df["SUB_SIZE"].apply(lambda x: size_dict[x] if x in size_dict else f"{int(x)}" ) #SUB SIZE 변경
    
    #ITEM 컬럼 생성
    df["ITEM"] = df["자재내역"].apply(lambda x: x.split(",")[0])
    df = df[["자재코드","PLANT","SPEC_CLASS","ITEM","SIZE","SUB_SIZE","BASIC_MATERIAL","RATING","FLANGE_FACE","STRESS_RELIEF","자재내역","NOTE"]] # 순서 정열
    #df.drop_duplicates(subset="자재코드", keep="first", inplace=True) # 중복코드 제거 여부
    df.reset_index(drop=True, inplace=True) # 인덱스 리셋

    return df

def vmi_list_find(df,sentence_processing):
    for k in [0,1]: # item 과 size 
        querys = df[["ITEM","SIZE", "SUB_SIZE", "자재내역"]]
        sentence_ = sentence_processing[k] # sentence_processing 
        
        querys_find = []
        for item, size, sub_size, sentence in querys.values:
            if k == 0: # item 찾기
                match = re.search(re.escape(sentence_), item, flags=re.IGNORECASE)
                if match:
                    querys_find.append(1) # 해당되면 1
                else:
                    querys_find.append(0) # 해당 안되면 0
                    
            elif k == 1: # 두번쨰에서 size 찾기
                sentence_ = re.sub("\"", "", sentence_)  # 따옴표(")를 변경
                sentence_ = re.sub("INCH", "", sentence_.upper(), flags=re.IGNORECASE)  # INCH를 변경
                sentence_ = re.sub("B", "", sentence_)  # B를 변경
                
                if re.search("\*", sentence_) is not None: # 이중 싸이즈 일 경우 # 1*2
                    sentence_split = sentence_.split("*")
                    if re.search(r"(?<![0-9/-])" + re.escape(sentence_split[0]) + r"(?![0-9/-])", size) is not None and re.search(r"(?<![0-9/-])" + re.escape(sentence_split[1]) + r"(?![0-9/-])", sub_size) is not None:
                        querys_find.append(1) # 해당되면 1
                    elif re.search(r"(?<![0-9/-])" + re.escape(sentence_split[1]) + r"(?![0-9/-])", size) is not None and re.search(r"(?<![0-9/-])" + re.escape(sentence_split[0]) + r"(?![0-9/-])", sub_size) is not None:
                        querys_find.append(1) # 해당되면 1
                    else:
                        querys_find.append(0) # 해당 안되면 0 
  
                else: # 단순 사이즈 일 경우
                    match = re.search(r"(?<![0-9/-])" + re.escape(sentence_) + r"(?![0-9/-])", size) # 사이즈 값 일단 변경      
                    if match:
                        querys_find.append(1) # 해당되면 1
                    else:
                        querys_find.append(0) # 해당 안되면 0
        
        querys_finds = pd.DataFrame({"find": querys_find}) # 데이터 프레임 생성
        querys_index = querys_finds[querys_finds["find"] == 1].index # 1에 해당하는 인덱스행만 추출
        # querys = querys.iloc[querys_index].reset_index(drop=True) # querys 추출 후 인덱스 리셋        
        df_filtered = df.copy() # 앞전 데이터 프레임 복사
        df_filtered['temp_find'] = querys_finds["find"] # 파인드 데이터 프레임을 시도 파인드로 대체
        df_filtered = df_filtered[df_filtered['temp_find'] != 0].dropna() # 0이 아닌 행을 제외한 나머지 눌값 제외
        df_filtered.drop('temp_find', axis=1, inplace=True) # 시도 컬럼 삭제
        df_filtered.reset_index(drop=True, inplace=True) # 인덱스 리셋   
        df = df_filtered   
            
    return df

def embedding_rank(df, sentence):
    """
    임베딩 모델을 사용하여 주어진 문장과 쿼리 리스트 사이의 유사도를 계산하고, 가장 유사한 상위 항목을 반환합니다.
    - 쿼리 리스트와 주어진 문장의 임베딩을 생성합니다.
    - 생성된 임베딩 간의 코사인 유사도를 계산합니다.
    - 유사도에 기반하여 상위 10개 항목을 반환합니다.
    """

    split_string = sentence.split(",")
    sentence = [split_string[0]] + split_string[2:]
    sentence = ", ".join(sentence)

    if df.empty:
        return pd.DataFrame()

    df_queries_embedding = model.encode(df["자재내역"])
    query_embedding = model.encode(sentence.upper())  # 문장을 대문자로 변환
    cosine_scores = util.cos_sim(df_queries_embedding, query_embedding)

    df["유사도"] = cosine_scores
    doc_top_rank = df.sort_values(by='유사도', ascending=False)
    doc_top_rank = doc_top_rank.drop_duplicates(subset=['자재내역'], keep='last')
    # doc_top_rank = doc_top_rank.head(5)
    doc_top_rank['유사도'] = doc_top_rank['유사도'].apply(lambda x: f"{x:.1%}")

    return doc_top_rank[df.columns.tolist()]

###################################################

def auto_size_columns(sheet):
    for column in sheet.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)  # Get column letter

        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass

        adjusted_width = (max_length + 2)  # Adjust as needed
        sheet.column_dimensions[column_letter].width = adjusted_width

def modify_item_column(df_dataset_pd):
    # "ITEM" 열 수정
    for i in range(len(df_dataset_pd["ITEM"])):
        item = df_dataset_pd["ITEM"][i]

        if re.search('ELBOW', item, re.IGNORECASE): # 엘보
            if re.search('45', item, re.IGNORECASE):
                df_dataset_pd.at[i, "ITEM"] = 'elbow-45d'
            elif re.search('90', item, re.IGNORECASE):
                df_dataset_pd.at[i, "ITEM"] = 'elbow-90d'

        if re.search('RED', item, re.IGNORECASE): # 레듀샤
            if re.search('con', item, re.IGNORECASE):
                df_dataset_pd.at[i, "ITEM"] = 'reducer-c'
            elif re.search('ecc', item, re.IGNORECASE):
                df_dataset_pd.at[i, "ITEM"] = 'reducer-e'

        if re.search('V/V', item, re.IGNORECASE): # 벨브
            df_dataset_pd.at[i, "ITEM"] = 'valve'

        if re.search('B/N', item, re.IGNORECASE): # 볼트너트
            df_dataset_pd.at[i, "ITEM"] = 'Bolt'

        if re.search('TEE', item, re.IGNORECASE): # 티
            if re.search('R', item, re.IGNORECASE):
                df_dataset_pd.at[i, "ITEM"] = 'tee-r'
            else:
                df_dataset_pd.at[i, "ITEM"] = 'tee'

        if re.search('blind', item, re.IGNORECASE): # 플라인드 플렌지
            df_dataset_pd.at[i, "ITEM"] = 'flange-blind'

        if re.search('cpl\'g', item, re.IGNORECASE): # 커플링
            df_dataset_pd.at[i, "ITEM"] = 'coupling'

    # Return outside the loop
    return df_dataset_pd

def modify_size_column(df_dataset_pd):
    # "SIZE" 열 수정
    for i in range(len(df_dataset_pd["SIZE"])):
        size = df_dataset_pd.at[i, "SIZE"]

        # 문자열 교체
        # size = re.sub('\"', 'B', size, flags=re.IGNORECASE)
        # size = re.sub('U', '', size, flags=re.IGNORECASE)
        # size = re.sub('x', '*', size, flags=re.IGNORECASE)

        # 첫 번째 "B"만 제거
        if str(size).count('B') > 1:
            size = str(size).replace('B', '', 1)

         # 문자열 중간에 위치한 "B" 제거
        if str(size).count('B') > 0:
            # 문자열 시작과 끝을 제외한 부분에서 "B" 제거
            middle_part = str(size)[1:-1].replace('B', '')
            size = str(size)[0] + middle_part + str(size)[-1] if len(str(size)) > 1 else str(size)

        # if re.search('11/', size, re.IGNORECASE): # 플라인드 플렌지
        #     size = '1-1/'

        # if re.search('21/', size, re.IGNORECASE): # 플라인드 플렌지
        #     size = '2-1/'

        # 수정된 값 저장
        df_dataset_pd.at[i, "SIZE"] = size

    return df_dataset_pd

def find_codes(df_bulk, df_original):
    df_dataset_pd = df_bulk[["ITEM","SIZE","자재내역"]]
    if df_dataset_pd.empty:
        return df_dataset_pd

    df_dataset_pd = modify_item_column(df_dataset_pd) # 아이템 수정
    df_dataset_pd = modify_size_column(df_dataset_pd) # 사이즈 수정
    sentence = df_dataset_pd.apply(lambda row: ','.join(row.astype(str)), axis=1) # 수정된 문장을 통으로 합치기

    # 코드 찾기
    find_coded = []
    sub_coded = []
    euc_coded = []
    for i in range(len(df_dataset_pd)):
        search_term_processing = sentence_processing(sentence[i]) # 문장 전처리
        search_df = vmi_list_find(df_original, search_term_processing)
        if search_df.empty:
            find_coded.append("null")
            sub_coded.append("null")
            euc_coded.append("null")
            continue

        search_df = embedding_rank(search_df, sentence[i]).head(5) # 탑 랭크 찾기
        search_df.reset_index(drop=True, inplace=True)
        find_coded.append(search_df["자재코드"][0]) # 탑 랭크의 첫번째 자재코드
        sub_coded.append("\n".join(search_df.apply(lambda row: ','.join(row.astype(str)), axis=1))) # 탑랭크 5개를 띄어 쓰기로 저장
        euc_coded.append(search_df["유사도"][0]) # 유사도 저장

    # 결과를 저장할 리스트 초기화
    check = []
    count = []
    for i in range(len(df_dataset_pd)):
        code = str(find_coded[i])
        euc = euc_coded[i]
        if euc != "null":
            euc = float(euc.replace("%", "")) / 100

        if code != "null":
            if euc >= 0.9:
                check.append("perfect")
                count.append(1)
            elif euc >= 0.7:
                check.append("good")
                count.append(1)
            elif euc >= 0.5:
                check.append("bad")
                count.append(1)          
            else:
                check.append("re_check")
                count.append(0)
        else:
            check.append("re_check")
            count.append(0)

    # 결과를 새로운 열로 DataFrame에 추가
    df_dataset_pd['find_coded'] = find_coded
    df_dataset_pd['sub_coded'] = sub_coded
    df_dataset_pd['euc_coded'] = euc_coded
    df_dataset_pd['check'] = check
    # df_dataset_pd['count'] = count

    return df_dataset_pd

###################################################
# Define search functions
def search_CODE_data(df,search_term):
    querys = df["자재코드"]
    querys_find = []
    for size in querys.values:
        if re.search(r"(?<![0-9/-])" + search_term + r"(?![0-9/-])", size) is not None:
            querys_find.append(1) # 해당되면 1
        else:
            querys_find.append(0) # 해당 안되면 0 
        
    querys_finds = pd.DataFrame({"find": querys_find}) # 데이터 프레임 생성
    querys_index = querys_finds[querys_finds["find"] == 1].index # 1에 해당하는 인덱스행만 추출
    df_filtered = df.copy() # 앞전 데이터 프레임 복사
    df_filtered['temp_find'] = querys_finds["find"] # 파인드 데이터 프레임을 시도 파인드로 대체
    df_filtered = df_filtered[df_filtered['temp_find'] != 0].dropna() # 0이 아닌 행을 제외한 나머지 눌값 제외
    df_filtered.drop('temp_find', axis=1, inplace=True) # 시도 컬럼 삭제
    df_filtered.reset_index(drop=True, inplace=True)
    return df_filtered

def search_SPEC_CLASS_data(df,search_term):
    search_df = df[df['SPEC_CLASS'].isin(search_term)]
    search_df.reset_index(drop=True, inplace=True)
    return search_df

def search_ITEM_data(df,search_term):
    search_df = df[df['ITEM'].isin(search_term)]
    # search_df = df[df['ITEM'].str.contains(search_term, case=False)]
    search_df.reset_index(drop=True, inplace=True)
    return search_df
    
def search_SIZE_data(df,search_term):
    querys = df["SIZE"]
    querys_find = []
    for size in querys.values:
        if re.search(r"(?<![0-9/-])" + search_term + r"(?![0-9/-])", size) is not None:
            querys_find.append(1) # 해당되면 1
        else:
            querys_find.append(0) # 해당 안되면 0 
        
    querys_finds = pd.DataFrame({"find": querys_find}) # 데이터 프레임 생성
    querys_index = querys_finds[querys_finds["find"] == 1].index # 1에 해당하는 인덱스행만 추출
    df_filtered = df.copy() # 앞전 데이터 프레임 복사
    df_filtered['temp_find'] = querys_finds["find"] # 파인드 데이터 프레임을 시도 파인드로 대체
    df_filtered = df_filtered[df_filtered['temp_find'] != 0].dropna() # 0이 아닌 행을 제외한 나머지 눌값 제외
    df_filtered.drop('temp_find', axis=1, inplace=True) # 시도 컬럼 삭제
    df_filtered.reset_index(drop=True, inplace=True)
    return df_filtered

def search_SUB_SIZE_data(df,search_term):
    querys = df["SUB_SIZE"]
    querys_find = []
    for size in querys.values:
        if re.search(r"(?<![0-9/-])" + search_term + r"(?![0-9/-])", size) is not None:
            querys_find.append(1) # 해당되면 1
        else:
            querys_find.append(0) # 해당 안되면 0 
        
    querys_finds = pd.DataFrame({"find": querys_find}) # 데이터 프레임 생성
    querys_index = querys_finds[querys_finds["find"] == 1].index # 1에 해당하는 인덱스행만 추출
    df_filtered = df.copy() # 앞전 데이터 프레임 복사
    df_filtered['temp_find'] = querys_finds["find"] # 파인드 데이터 프레임을 시도 파인드로 대체
    df_filtered = df_filtered[df_filtered['temp_find'] != 0].dropna() # 0이 아닌 행을 제외한 나머지 눌값 제외
    df_filtered.drop('temp_find', axis=1, inplace=True) # 시도 컬럼 삭제
    df_filtered.reset_index(drop=True, inplace=True)
    return df_filtered

def search_BASIC_MATERIAL_data(df,search_term):
    search_df = df[df['BASIC_MATERIAL'].isin(search_term)]
    search_df.reset_index(drop=True, inplace=True)
    return search_df

def search_RATING_data(df,search_term):
    querys = df["RATING"]
    querys_find = []
    for rating in querys.values:
        if re.search(r"(?<![0-9/-])" + search_term + r"(?![0-9/-])", rating) is not None:
            querys_find.append(1) # 해당되면 1
        else:
            querys_find.append(0) # 해당 안되면 0 
        
    querys_finds = pd.DataFrame({"find": querys_find}) # 데이터 프레임 생성
    querys_index = querys_finds[querys_finds["find"] == 1].index # 1에 해당하는 인덱스행만 추출
    df_filtered = df.copy() # 앞전 데이터 프레임 복사
    df_filtered['temp_find'] = querys_finds["find"] # 파인드 데이터 프레임을 시도 파인드로 대체
    df_filtered = df_filtered[df_filtered['temp_find'] != 0].dropna() # 0이 아닌 행을 제외한 나머지 눌값 제외
    df_filtered.drop('temp_find', axis=1, inplace=True) # 시도 컬럼 삭제
    df_filtered.reset_index(drop=True, inplace=True)
    return df_filtered

def search_LIST_data(df, search_term):
    search_terms = search_term.split(',')
    search_df = df
    for term in search_terms:
        search_df = search_df[search_df['자재내역'].str.contains(term.strip(), case=False)]
    search_df.reset_index(drop=True, inplace=True)
    return search_df

def Ai_search_ITEM_data(df,search_term):
    search_term_processing = sentence_processing(search_term)
    search_df = vmi_list_find(df,search_term_processing)
    search_df = embedding_rank(search_df, search_term)
    search_df.reset_index(drop=True, inplace=True)
    return search_df, search_term_processing

def Ai_search_ITEM_data_(df,search_term):
    search_term = sentence_processing_ai(search_term)
    search_term_processing = sentence_processing(search_term)
    search_df = vmi_list_find(df,search_term_processing)
    search_df = embedding_rank(search_df, search_term)
    search_df.reset_index(drop=True, inplace=True)
    return search_df, search_term_processing

# 장바구니에 상품 추가하는 함수
def add_to_cart(df):
    global df_cart
    # 체크된 상품만 장바구니에 추가
    if 'df_cart' not in locals() or 'df_cart' not in globals():
        df_cart = pd.DataFrame(columns=df.columns)  # 또는 필요한 열 구조를 지정
    df_cart = pd.concat([df_cart, df[df['bool'] == True]], ignore_index=True)

    # 중복 제거
    df_cart = df_cart.drop_duplicates(subset=['자재코드'], keep='last')
    return df_cart
