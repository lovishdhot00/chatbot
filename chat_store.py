import mysql.connector
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage
import uuid
def get_connection():
    return mysql.connector.connect(
    host="localhost",
    user="root",
    password="2580",
    database="chatbot"
)

def create_user(username, password):
    conn=get_connection()
    cursor=conn.cursor()
    user_id=uuid.uuid4().bytes
    query="insert into users_table (user_id,username,password) values (%s,%s,%s)"
    cursor.execute(query,(user_id,username,password))
    conn.commit()
    cursor.close()
    conn.close()  


def save_conversation_id(user_id,conversation_id,title):
    conn = get_connection()
    cursor = conn.cursor()
    query= "insert into conversations_id_table (user_id,conversation_id,title) values (%s,%s,%s)"
    cursor.execute(query,(user_id,conversation_id,title))
    conn.commit()

    cursor.close()
    conn.close()

def save_messages(message_id,user_id,conversation_id,role,message):
    conn = get_connection()
    cursor = conn.cursor()
    query="INSERT INTO chats_history_table (message_id,user_id,conversation_id,role,message) VALUES (%s,%s,%s,%s,%s)"
    cursor.execute(query,(message_id,user_id,conversation_id,role,message))
    conn.commit()

    cursor.close()
    conn.close()   

def fetch_user(username,password):
    conn = get_connection()
    cursor = conn.cursor()
    query="select user_id from users_table where username=%s AND password=%s"
    cursor.execute(query,(username,password))
    user= cursor.fetchone()
    conn.commit()

    cursor.close()
    conn.close()
    return user

def fetch_conversation_id(user):
    conn = get_connection()
    cursor = conn.cursor()
    query= "select conversation_id from conversations_id_table where user_id=%s order by created_at DESC"
    cursor.execute(query,(user,))
    conversation_id=cursor.fetchall()
    conversations=[]
    for id in conversation_id:
        conversations.append(id[0])
    conn.commit()

    cursor.close()
    conn.close()
    return conversations

def fetch_messages(user_id,conversation_id):
    conn = get_connection()
    cursor = conn.cursor()
    query="select role,message from chats_history_table where user_id=%s and conversation_id=%s order by created_at ASC"
    cursor.execute(query,(user_id,conversation_id))
    messages=cursor.fetchall()
    base_messages_list=[]
    for role,message in messages:
        if role=="user":
            base_messages_list.append(HumanMessage(content=message))
        elif role=="ai":
            base_messages_list.append(AIMessage(content=message))
    cursor.close()
    conn.close()
    return base_messages_list
def fetch_title(user_id):
    conn=get_connection()
    cursor=conn.cursor()
    query="select conversation_id,title from conversations_id_table where user_id=%s order by created_at DESC"
    cursor.execute(query,(user_id,))
    id_title=cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return id_title
def fetch_summary(conversation_id):
    conn=get_connection()
    cursor=conn.cursor()
    query="select stm_summary from conversations_id_table where conversation_id=%s"
    cursor.execute(query,(conversation_id,))
    summary=cursor.fetchone()
    cursor.close()
    conn.close()
    return summary[0] if summary else None
def update_summary(summary,user_id,conversation_id):
    conn=get_connection()
    cursor=conn.cursor()
    query="update conversations_id_table set stm_summary=%s where user_id=%s and conversation_id=%s"
    cursor.execute(query,(summary,user_id,conversation_id))
    conn.commit()
    cursor.close()
    conn.close()
def fetch_trimmed_messages(conversation_id):
    conn=get_connection()
    cursor=conn.cursor()
    query="select message_id,role,message from chats_history_table where conversation_id=%s and is_active=%s order by created_at asc"
    cursor.execute(query,(conversation_id,1))
    messages=cursor.fetchall()
    base_messages_list=[]
    for message_id,role,message in messages:
        if role=="user":
            base_messages_list.append(HumanMessage(content=message,id=message_id))
        elif role=="ai":
            base_messages_list.append(AIMessage(content=message,id=message_id))
    cursor.close()
    conn.close()
    return base_messages_list
def set_false_is_active(message_id):
    conn=get_connection()
    cursor=conn.cursor()
    query="update chats_history_table set is_active=%s where message_id=%s"
    cursor.execute(query,(False,message_id)) 
    conn.commit()
    cursor.close()
    conn.close()  
def set_true_is_summarized(message_id):
    conn=get_connection()
    cursor=conn.cursor()
    query="update chats_history_table set is_summarized=%s where message_id=%s"
    cursor.execute(query,(True,message_id)) 
    conn.commit()
    cursor.close()
    conn.close() 
def fetch_To_Summarize(conversation_id):
    conn=get_connection()
    cursor=conn.cursor()
    query="select message_id,role,message from chats_history_table where conversation_id=%s and is_active=%s and is_summarized=%s order by created_at "
    cursor.execute(query,(conversation_id,False,False))
    messages=cursor.fetchall()
    base_messages_list=[]
    for message_id,role,message in messages:
        if role=="user":
            base_messages_list.append(HumanMessage(content=message,id=message_id))
        elif role=="ai":
            base_messages_list.append(AIMessage(content=message,id=message_id))    
    cursor.close()
    conn.close()
    return base_messages_list
# get_connection()

# conversation_id = uuid.UUID("688fe473-457c-400f-9738-0f516d4c789b").bytes

# print(fetch_summary(conversation_id=conversation_id))
