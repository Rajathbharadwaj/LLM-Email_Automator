from langchain.agents import ConversationalChatAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from langchain_core.prompts import ChatPromptTemplate
import pandas as pd

import streamlit as st

# Read the CSV
df = pd.read_csv("Fintech BB Reachout list.csv")
company_name = tuple(df['Company name']) + tuple("A")

# Email configuration
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_user = 'your_email@gmail.com'
smtp_password = 'your_password'

# Function to send an email
def send_email(to_address, subject, body):
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_address
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)

st.set_page_config(page_title="Email Automator", page_icon="🦜")
st.title("Automate Email")

openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
)
if len(msgs.messages) == 0 or st.sidebar.button("Reset chat history"):
    msgs.clear()
    msgs.add_ai_message("How can I help you?")
    st.session_state.steps = {}

avatars = {"human": "user", "ai": "assistant"}
for idx, msg in enumerate(msgs.messages):
    with st.chat_message(avatars[msg.type]):
        # Render intermediate steps if any were saved
        for step in st.session_state.steps.get(str(idx), []):
            if step[0].tool == "_Exception":
                continue
            with st.status(f"**{step[0].tool}**: {step[0].tool_input}", state="complete"):
                st.write(step[0].log)
                st.write(step[1])
        st.write(msg.content)
base_company =  st.selectbox("Select the product you want to pitch", ("BrokeBrothers", "PPI", "More"))
target_company = st.selectbox("Which company you want to pitch to? Select ALL for all or select any from the dropbox", company_name)
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant who will help me pitch a company's product to another company. You have access to the internet and all the revelant information. You have to fintune in your pitch and identify how the company's product will help the other company."),
    ("user", "Here's the company product {base_company} and here's the company you should pitch to {target_company}")
])

if prompt_template:
    st.chat_message("user").write(prompt_template)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    llm =    ChatOpenAI(model_name="gpt-4o", openai_api_key=openai_api_key, streaming=True)
    # chain: Runnable = prompt | llm 
    tools = [DuckDuckGoSearchRun(name="Search")]
    chat_agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=tools)
    executor = AgentExecutor.from_agent_and_tools(
        agent=chat_agent,
        tools=tools,
        memory=memory,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
    )
    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        cfg = RunnableConfig()
        cfg["callbacks"] = [st_cb]
        response = executor.invoke({"base_company": base_company, "target_company": target_company}, cfg)
        st.write(response["output"])
        st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]
        if response["output"]:
            send_email = st.button("Send Email?")
            # if send_email:
            #     subject = executor.invoke("Give me a subject for this email", cfg)["output"].capitalize()

