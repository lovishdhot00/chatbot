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

stm_template = ChatPromptTemplate.from_messages([
    
    ("system",
     """You are a helpful AI assistant continuing an ongoing conversation.

You will receive three types of context:

1. Conversation Summary:
This is a condensed summary of older messages that were removed from the context window.
Use it to remember important facts, preferences, and topics from earlier in the conversation.

2. Recent Conversation:
These are the most recent messages between the user and the assistant.
Treat these as the primary context.

3. Current User Message:
This is the latest message from the user that you must respond to.

Instructions:
- Use the recent conversation as the main context.
- Use the summary to recall older information.
- If the summary conflicts with the recent conversation, prioritize the recent conversation.
- Respond naturally and continue the conversation.
"""),

    ("system", "Conversation Summary:\n{summary}"),

    ("system", "Recent Conversation:\n{trimmed_messages}"),

    ("human", "{prompt}")

])