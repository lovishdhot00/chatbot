import streamlit as st
from chat_store import get_connection, fetch_user,create_user
from streamlit_cookies_manager import EncryptedCookieManager
cookies = EncryptedCookieManager(password="secret_key")

if not cookies.ready():
    st.stop()
if "user_id" in cookies :
    st.session_state["user_id"] = bytes.fromhex(cookies["user_id"])
    st.switch_page("pages/frontend.py")
st.title("Login Page")
username = st.text_input("Username")
password = st.text_input("Password", type="password")

login_btn = st.button("Login")

if login_btn:
    get_connection()
    user_id = fetch_user(username=username, password=password)

    if user_id is not None:
        st.success("Login successful ✅")
        cookies["user_id"] = user_id[0].hex()
        cookies.save()

        # store login session
        st.session_state["user_id"] = user_id[0]

        # switch to chat page
        st.switch_page("pages/frontend.py")

    else:
        create_user(username=username,password=password)
        st.session_state["user_id"] = fetch_user(username,password)[0]
        cookies["user_id"] = st.session_state["user_id"].hex()
        cookies.save()
        st.success("Login successful ✅")
        st.switch_page("pages/frontend.py")

        