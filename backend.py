from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from dotenv import load_dotenv
from langgraph.graph import StateGraph,START,add_messages,END
import os
from typing import TypedDict,Annotated,List
from langchain_core.messages import BaseMessage,HumanMessage,AIMessage,SystemMessage
from langchain_core.prompts import ChatPromptTemplate
import uuid
from typing import List
from langchain_core.messages.utils import trim_messages,count_tokens_approximately
load_dotenv()
api_key=os.getenv("api_token")
llm=HuggingFaceEndpoint(repo_id="deepseek-ai/DeepSeek-R1",huggingfacehub_api_token=api_key,task="text-generation")
model=ChatHuggingFace(llm=llm)
print(model.invoke("hi how are you").content)
# short term memory 
def short_term_memory(messages:List[BaseMessage]):
    if count_tokens_approximately(messages)>1000:
        trimmed_meesages=trim_messages(messages=messages,
                      max_tokens=600,
                      token_counter=count_tokens_approximately,
                      strategy="last")
        lenght=len(messages)-len(trimmed_meesages)
        removed_messages=messages[:lenght]
        return trimmed_meesages,removed_messages
def format_messages(messages):
    formatted = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            formatted.append(f"Assistant: {msg.content}")
        elif isinstance(msg, SystemMessage):
            formatted.append(f"System: {msg.content}")
    return "\n".join(formatted)    

