import streamlit as st
from chat_store import get_connection, fetch_user,create_user
import uuid
st.title("Login Page")
username = st.text_input("Username")
password = st.text_input("Password", type="password")

login_btn = st.button("Login")

if login_btn:
    get_connection()
    user_id = fetch_user(username=username, password=password)

    if user_id is not None:
        st.success("Login successful ✅")

        # store login session
        st.session_state["user_id"] = user_id[0]

        # switch to chat page
        st.switch_page("pages/frontend.py")

    else:
        st.success("Login successful ✅")
        user_id=create_user(username=username,password=password)
        st.session_state["user_id"] = fetch_user(username,password)[0]
        st.switch_page("pages/frontend.py")

        