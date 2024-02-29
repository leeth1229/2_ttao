import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="Hello",
    page_icon="👋",
)

st.session_state.name = "billy"
st.session_state.email = "none_nono_@lgchem.com"

st.write("# Welcome👋")

# if st.session_state['Save_success']:
#     st.sidebar.markdown("your keys")

# Create an empty container
placeholder = st.empty()

# 로그인 성공 여부를 저장할 세션 상태 초기화

# Insert a form in the container
with placeholder.form("login"):
    st.markdown("#### Enter your information")
    name = st.text_input("name")
    email = st.text_input("email")
    submit = st.form_submit_button("Save")

if submit: # and name == actual_name and idNo == actual_idNo and email == actual_email
    # If the form is submitted and the name and idNo are correct,
    # clear the form/container and display a success message
    placeholder.empty()
    st.success("Save successful")
    st.session_state['Save_success'] = True
    # st.experimental_rerun()  # 페이지 새로고침
    st.session_state.name =name
    st.session_state.email =email
    
else:
    pass

st.sidebar.write("Name :",st.session_state.name)
st.sidebar.write("Email :",st.session_state.email)


st.markdown(
    """
    메일 주소 및 이름을 입력 시, 자재코드 다운로드 양식에 자동 반영 됩니다.(반영예정)
    
    👈 미 입력 시, 해당 Name & Email 로 자동 입력됩니다.
    """
)


    # ### Want to learn more?
    # - Check out [streamlit.io](https://streamlit.io)
    # - Jump into our [documentation](https://docs.streamlit.io)
    # - Ask a question in our [community
    #     forums](https://discuss.streamlit.io)

    # ### See more complex demos
    # - Use a neural net to [analyze the Udacity Self-driving Car Image
    #     Dataset](https://github.com/streamlit/demo-self-driving)
    # - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
