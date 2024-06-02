from langchain_google_genai import ChatGoogleGenerativeAI
from pdf_manager import download_pdf
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
import streamlit as st

from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema.messages import HumanMessage,AIMessage
import os

st.set_page_config(page_title="Chat On Law", page_icon="💬")
st.title("Chat On Law 💬")

def main():
    prompt = ChatPromptTemplate(
        messages=[
SystemMessagePromptTemplate.from_template(
"""You are a helpful assistant.Your task is to answer user questions based on this Pakistan Punjab Law, delimited with ````. If a user asks about this law any question, please assist them courteously and always give your best effort.Please do your best because it is very important to my career.

> ```{law}```"""),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{question}")])

    prompt = prompt.partial(law=st.session_state["content"])

    msgs = StreamlitChatMessageHistory(key="langchain_messages")
    if len(msgs.messages) == 0:
        msgs.add_ai_message("Hello! How can I assist you today?")

    llm_chain = prompt | ChatGoogleGenerativeAI(model="gemini-1.5-flash",google_api_key=os.getenv("google_api_key"))

    USER_AVATAR = "👤"
    BOT_AVATAR = "🤖"
    
    chat = st.session_state["langchain_messages"]
    chat_messages = ""
    for mess in chat:
        if isinstance(mess,HumanMessage):
            chat_messages += f"User: {mess.content}\n\n"
        elif isinstance(mess,AIMessage):
            chat_messages += f"Assistant: {mess.content}\n\n"

    download_pdf(chat_messages,"Chat")

    for msg in msgs.messages:
        avatar = USER_AVATAR if msg.type == "human" else BOT_AVATAR
        st.chat_message(msg.type,avatar=avatar).write(msg.content)
    
    if prompt := st.chat_input():
        st.chat_message("human",avatar=USER_AVATAR).write(prompt)

        with st.chat_message("assistant",avatar=BOT_AVATAR):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                response = llm_chain.stream({"question":prompt,"chat_history":st.session_state.
                                        langchain_messages[0:40]})

                for res in response:
                    full_response += res.content or "" 
                    message_placeholder.markdown(full_response + "|")
                    message_placeholder.markdown(full_response)

                msgs.add_user_message(prompt)
                msgs.add_ai_message(full_response)

            except Exception as e:
                st.error(f"An error occured. {e}")

if "content" in st.session_state:
    main()

else:
    st.info("Please search for a law first, then you can chat about it.")