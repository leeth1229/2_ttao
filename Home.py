import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="Hello",
    page_icon="👋",
)

# 로그인 성공 여부를 저장할 세션 상태 초기화
if 'login_success' not in st.session_state:
    st.session_state['login_success'] = False


st.sidebar.success("Select a Tab above.")

st.write("# Welcome👋")

if st.session_state['login_success']:
    st.sidebar.markdown("## Pages")

# Create an empty container
placeholder = st.empty()

actual_email = "email"
actual_password = "password"

# Insert a form in the container
with placeholder.form("login"):
    st.markdown("#### Enter your credentials")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login")

if submit and email == actual_email and password == actual_password:
    # If the form is submitted and the email and password are correct,
    # clear the form/container and display a success message
    placeholder.empty()
    st.success("Login successful")
    st.session_state['login_success'] = True
    st.experimental_rerun()  # 페이지 새로고침
elif submit and email != actual_email and password != actual_password:
    st.error("Login failed")
else:
    pass

st.markdown(
    """
    Streamlit is an open-source app framework built specifically for
    Machine Learning and Data Science projects.

    **👈 Select a demo from the sidebar** to see some examples
    of what Streamlit can do!

    ### Want to learn more?
    - Check out [streamlit.io](https://streamlit.io)
    - Jump into our [documentation](https://docs.streamlit.io)
    - Ask a question in our [community
        forums](https://discuss.streamlit.io)

    ### See more complex demos
    - Use a neural net to [analyze the Udacity Self-driving Car Image
        Dataset](https://github.com/streamlit/demo-self-driving)
    - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
"""
)