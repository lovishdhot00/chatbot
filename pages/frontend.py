import streamlit as st
from backend import model,check_login,format_messages
from prompts import title_template,update_summary_template,stm_template
from chat_store import get_connection,save_messages,save_conversation_id,fetch_messages,fetch_title,fetch_summary,update_summary,fetch_trimmed_messages,set_false_is_active,set_true_is_summarized,fetch_To_Summarize
import uuid
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage
from langchain_core.messages.utils import trim_messages,count_tokens_approximately
from snowflake import SnowflakeGenerator

check_login()
prompt=st.chat_input()
get_connection()
                      
if "conversation_id" not in st.session_state:
    conversation_id=uuid.uuid4()    
    st.session_state["conversation_id"]=conversation_id.bytes

if "messages" not in st.session_state:
    st.session_state["messages"]=fetch_trimmed_messages(conversation_id=st.session_state["conversation_id"])
if "summary" not in st.session_state or st.session_state["summary"] is None :
    st.session_state["summary"]=fetch_summary(conversation_id=st.session_state["conversation_id"])
if "current_messages" not in st.session_state:
    st.session_state["current_messages"]=[]    
generator=SnowflakeGenerator(1)
if prompt is not None:
    if st.session_state["current_messages"] != []:
        for message in st.session_state["current_messages"]:
            if isinstance(message,HumanMessage):
                with st.chat_message("user"):
                    st.write(message.content)
            if isinstance(message,AIMessage):
                with st.chat_message("ai"):
                    st.write(message.content)
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state["current_messages"].append(HumanMessage(content=prompt))
    formatted_trimmed_messages=format_messages(st.session_state["messages"])
    stm_prompt=stm_template.invoke({"summary":st.session_state["summary"],"trimmed_messages":formatted_trimmed_messages,"prompt":prompt})
    output=model.stream(stm_prompt)
    with st.chat_message("ai"):
        response=st.write_stream(output)           
    if "title" not in st.session_state:
        title_prompt=title_template.invoke({"conversation":f"User:{prompt}\nAssistant:{response}"})
        title=model.invoke(title_prompt).content
        st.session_state["title"]=title
        save_conversation_id(user_id=st.session_state["user_id"],conversation_id=st.session_state["conversation_id"],title=st.session_state["title"])
    
    st.session_state["message_id1"]=next(generator)
    save_messages(message_id=st.session_state["message_id1"] ,user_id= st.session_state["user_id"],conversation_id=st.session_state["conversation_id"],role="user",message=prompt)
    if response is not None:
        st.session_state["current_messages"].append(AIMessage(content=response))
        st.session_state["message_id2"]=next(generator)
        save_messages(message_id=st.session_state["message_id2"] ,user_id= st.session_state["user_id"],conversation_id=st.session_state["conversation_id"],role="ai",message=response)
        

    # short term memory 
    st.session_state["messages"].append(HumanMessage(content=prompt,id=st.session_state["message_id1"]))
    st.session_state["messages"].append(AIMessage(content=response, id=st.session_state["message_id2"]))
    if count_tokens_approximately(st.session_state["messages"])>=7000:
        trimmed_msgs=trim_messages(messages=st.session_state["messages"],
                                                    max_tokens=5000,
                                                    strategy="last",
                                                    token_counter=count_tokens_approximately)
        st.session_state["remaining_old_msgs"]=st.session_state["messages"][:len(st.session_state["messages"])-len(trimmed_msgs)]
        st.session_state["messages"]=trimmed_msgs
        for message in st.session_state["remaining_old_msgs"]:
            set_false_is_active(message_id=message.id)
        del st.session_state["remaining_old_msgs"]
    To_Summarize=fetch_To_Summarize(conversation_id=st.session_state["conversation_id"])
    if To_Summarize:    
        if count_tokens_approximately(To_Summarize)>=1500:
            formatted_old=format_messages(To_Summarize)
            summary=fetch_summary(conversation_id=st.session_state["conversation_id"])
            summary_prompt=update_summary_template.invoke({"existing_summary":f"System:{summary}" if summary else "no previous summary",
                                                    "old_messages":formatted_old})
            summary=model.invoke(summary_prompt).content
            update_summary(summary=summary,user_id=st.session_state["user_id"],conversation_id=st.session_state["conversation_id"])
            for message in To_Summarize:    
                set_true_is_summarized(message_id=message.id)
            

with st.sidebar:
    st.write("fucking chatbot")
    if st.button("new chat"):
        conversation_id=uuid.uuid4()    
        st.session_state["conversation_id"]=conversation_id.bytes
        if "current_messages" in st.session_state:
            del st.session_state["current_messages"]
        if "title" in st.session_state:
            del st.session_state["title"]
        for key in ["messages","trimmed_msgs","remaining_old_msgs","to_show_messages","summary"]:
            if key in st.session_state:
                del st.session_state[key]  


for i, id_title in enumerate(fetch_title(user_id=st.session_state["user_id"])):
    if st.sidebar.button(id_title[1],key=f"title_{i}"):
        st.session_state["conversation_id"]=id_title[0]
        st.session_state["title"]=id_title[1]
        for message in fetch_messages(user_id=st.session_state["user_id"],conversation_id=id_title[0]):
            if isinstance(message,HumanMessage):
                with st.chat_message("user"):
                    st.write(message.content)
            if isinstance(message,AIMessage):
                with st.chat_message("ai"):
                    st.write(message.content)         
