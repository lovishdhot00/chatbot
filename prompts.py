from langchain_core.prompts import ChatPromptTemplate
title_template=ChatPromptTemplate(messages=[("system", "You generate short, precise titles for conversations."),
    ("human", """
Generate a title for this conversation.

Rules:
- Max 8 words
- Clear and descriptive
- No quotes
- No explanation

Conversation:
{conversation}
""")])



update_summary_template = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a long-term memory compression assistant.

Your job is to maintain a single concise but information-dense summary 
of an ongoing conversation.

You will receive:
1. An existing long-term summary (if any)
2. Newly removed old messages from short-term memory

Your task:
- Merge the existing summary with the new information
- Preserve important user goals, preferences, technical context, decisions
- Remove redundancy
- Keep the summary concise but complete
- Do NOT repeat information
- Do NOT include small talk
- Keep structured bullet points

The output should be a clean, updated long-term memory summary.
"""
    ),
    (
        "human",
        """
Existing Summary:
{existing_summary}

Newly Removed Messages:
{old_messages}

Update the long-term memory summary.
"""
    )
])

from langchain_core.prompts import ChatPromptTemplate

stm_template = stm_template = ChatPromptTemplate.from_messages([
    
    ("system",
     """You are a helpful AI assistant continuing an ongoing conversation.

You will receive four types of context:

1. Conversation Summary:
A condensed summary of older messages removed from the context window.
Use it to recall important past information.

2. Recent Conversation:
The most recent messages between the user and assistant.
This is the primary conversational context.

3. Retrieved Context (Optional):
Relevant chunks retrieved from uploaded documents (e.g., PDFs).
Use this only when it is relevant to the user's query.

4. Current User Message:
The latest user query you must respond to.

Instructions:
- Prioritize the Recent Conversation for continuity.
- Use the Conversation Summary to recall past details.
- Use Retrieved Context ONLY if it is relevant to the user's question.
- If Retrieved Context is used, base your answer primarily on it.
- If Retrieved Context conflicts with conversation, prefer Retrieved Context for factual answers.
- If no relevant Retrieved Context is available, answer normally.
- Do NOT fabricate information from Retrieved Context.
- Respond naturally and helpfully.
"""),

    ("system", "Conversation Summary:\n{summary}"),

    ("system", "Recent Conversation:\n{trimmed_messages}"),

    ("system", "Retrieved Context:\n{retrieved_context}"),

    ("human", "{prompt}")

])