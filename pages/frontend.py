import streamlit as st
from backend import model,short_term_memory
from prompts import title_template,update_summary_template,stm_template
from chat_store import get_connection,save_messages,save_conversation_id,fetch_messages,fetch_title,fetch_summary,update_summary,fetch_trimmed_messages,set_false_is_active,set_true_is_summarized,fetch_To_Summarize
import uuid
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage
from langchain_core.messages.utils import trim_messages,count_tokens_approximately
from snowflake import SnowflakeGenerator
prompt=st.chat_input()
get_connection()

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
                         
if "conversation_id" not in st.session_state:
    conversation_id=uuid.uuid4()    
    st.session_state["conversation_id"]=conversation_id.bytes

if "messages" not in st.session_state:
    st.session_state["messages"]=fetch_trimmed_messages(conversation_id=st.session_state["conversation_id"])
if "summary" not in st.session_state or st.session_state["summary"] is None :
    st.session_state["summary"]=fetch_summary(conversation_id=st.session_state["conversation_id"])
generator=SnowflakeGenerator(1)
if prompt is not None:
    formatted_trimmed_messages=format_messages(st.session_state["messages"])
    stm_prompt=stm_template.invoke({"summary":st.session_state["summary"],"trimmed_messages":formatted_trimmed_messages,"prompt":prompt})
    response=model.invoke(stm_prompt)
    if "title" not in st.session_state:
        title_prompt=title_template.invoke({"conversation":f"User:{prompt}\nAssistant:{response}"})
        title=model.invoke(title_prompt).content
        st.session_state["title"]=title
        save_conversation_id(user_id=st.session_state["user_id"],conversation_id=st.session_state["conversation_id"],title=st.session_state["title"])
    
    st.session_state["message_id1"]=next(generator)
    save_messages(message_id=st.session_state["message_id1"] ,user_id= st.session_state["user_id"],conversation_id=st.session_state["conversation_id"],role="user",message=prompt)
    if response is not None:
        st.session_state["message_id2"]=next(generator)
        save_messages(message_id=st.session_state["message_id2"] ,user_id= st.session_state["user_id"],conversation_id=st.session_state["conversation_id"],role="ai",message=response.content)
        
    st.session_state["to_show_messages"]=fetch_messages(user_id=st.session_state["user_id"],conversation_id=st.session_state["conversation_id"])
    for message in st.session_state["to_show_messages"]:
        if isinstance(message,HumanMessage):
            with st.chat_message("user"):
                st.write(message.content)
        if isinstance(message,AIMessage):
            with st.chat_message("ai"):
                st.write(message.content)

        # short term memory 
    st.session_state["messages"].append(HumanMessage(content=prompt,id=st.session_state["message_id1"]))
    st.session_state["messages"].append(AIMessage(content=response.content, id=st.session_state["message_id2"]))
    if count_tokens_approximately(st.session_state["messages"])>=700:
        st.session_state["trimmed_msgs"]=trim_messages(messages=st.session_state["messages"],
                                                    max_tokens=500,
                                                    strategy="last",
                                                    token_counter=count_tokens_approximately)
        st.session_state["remaining_old_msgs"]=st.session_state["messages"][:len(st.session_state["messages"])-len(st.session_state["trimmed_msgs"])]
        st.session_state["messages"]=st.session_state["trimmed_msgs"]
        for message in st.session_state["remaining_old_msgs"]:
            set_false_is_active(message_id=message.id)
        del st.session_state["remaining_old_msgs"]
    To_Summarize=fetch_To_Summarize(conversation_id=st.session_state["conversation_id"])
    if To_Summarize:    
        if count_tokens_approximately(To_Summarize)>=150:
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
        if "title" in st.session_state:
            del st.session_state["title"]
        for key in ["messages","trimmed_msgs","remaining_old_msgs","to_show_messages","summary"]:
            if key in st.session_state:
                del st.session_state[key]    


for id_title in fetch_title(user_id=st.session_state["user_id"]):
    if st.sidebar.button(id_title[1]):
        st.session_state["conversation_id"]=id_title[0]
        st.session_state["title"]=id_title[1]
        st.session_state["to_show_messages"]=fetch_messages(user_id=st.session_state["user_id"],conversation_id=id_title[0])
        for message in st.session_state["to_show_messages"]:
            if isinstance(message,HumanMessage):
                with st.chat_message("user"):
                    st.write(message.content)
            if isinstance(message,AIMessage):
                with st.chat_message("ai"):
                    st.write(message.content)



