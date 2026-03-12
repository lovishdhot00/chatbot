from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from dotenv import load_dotenv
import streamlit as st
import os
from streamlit_cookies_manager import EncryptedCookieManager
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage
# load_dotenv()
# api_key=os.getenv("api_token")
api_key=st.secrets["api_token"]
llm=HuggingFaceEndpoint(repo_id="Qwen/Qwen2.5-7B-Instruct",huggingfacehub_api_token=api_key,task="text-generation")
model=ChatHuggingFace(llm=llm)
def check_login():
    cookies = EncryptedCookieManager(password="secret_key")

    if not cookies.ready():
        st.stop()

    if "user_id" not in st.session_state:
        if "user_id" in cookies and cookies["user_id"]:
            st.session_state["user_id"] = bytes.fromhex(cookies["user_id"])
        else:
            st.switch_page("login_page.py")
def format_messages(messages):
    formatted_msgs=[]
    for msg in messages:
        if isinstance(msg,HumanMessage):
            formatted_msgs.append(f"Human:{msg.content}")
        elif isinstance(msg,AIMessage):
            formatted_msgs.append(f"Assistant:{msg.content}")
        elif isinstance(msg,SystemMessage):
            formatted_msgs.append(f"System:{msg.content}")
    return "\n".join(formatted_msgs) 