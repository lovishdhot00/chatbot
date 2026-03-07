from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from dotenv import load_dotenv
import streamlit as st
import os
load_dotenv()
api_key=st.secrets["api_token"]
llm=HuggingFaceEndpoint(repo_id="deepseek-ai/DeepSeek-R1",huggingfacehub_api_token=api_key,task="text-generation")
model=ChatHuggingFace(llm=llm)

