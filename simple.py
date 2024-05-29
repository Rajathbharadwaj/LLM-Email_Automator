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
from duckduckgo_search import DDGS
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from langchain_core.prompts import ChatPromptTemplate
import pandas as pd
from langchain_openai import AzureOpenAI
import streamlit as st
import os

os.environ["OPENAI_API_VERSION"] = "2024-05-01-preview"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://spenseazureopenai.openai.azure.com/"
os.environ["AZURE_OPENAI_API_KEY"] = "08e642c7a2314ddeb1380ccdf1ed3904"


# Read the CSV
df = pd.read_csv("Fintech BB Reachout list.csv")
company_name = tuple(df['Company name']) + tuple("A")

# openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

base_company =  st.selectbox("Select the product you want to pitch", ("BrokeBrothers", "PPI", "More"))
target_company = st.selectbox("Which company you want to pitch to? Select ALL for all or select any from the dropbox", company_name)
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant who will help me pitch a company's product to another company. You have access to the internet and all the revelant information. You have to fintune in your pitch and identify how the company's product will help the other company."),
    ("user", "Here's the company product {base_company} and here's the company you should pitch to {target_company}")
])
llm = AzureOpenAI(
    deployment_name="gpt-4o Email Automation", model="gpt-4o", streaming=True
)




prompt = ChatPromptTemplate.from_messages([
    ("system", "you are a helpful agent, who Help in writing emails to pitch to other companies I will give you information about the company you are pitching and also the company you will pitch to. \
     your job is to Write an email that matches the requirements of the company that you're pitching given the latest information about the company try to Fine tune the email. Make sure not to include things that are not there and only the things that are there. Don't not make up things on your own."),
    ("user", " Here is the company you're pitching\n\n {base_company} and here's the compnay you're pitching to {target_company}")
])

base_company_info = """
Create a personalized pitch email for Broke Brothers, a company specializing in engaging Vox pop content, aimed at enhancing brand visibility and engagement. The recipient is [Company Name], a leader in the [Industry]. The email should address [Contact Name], highlight the alignment between Broke Brothers' content style and the recipient's brand values, and suggest a collaborative content series that resonates with [Company Name]'s target audience. Include key metrics from Broke Brothers’ previous successful campaigns to showcase their reach and impact. 
Conclude with a call to action for a meeting to discuss the collaboration further. Note broke brothers does not engage in any financial advice broke brothers strictly a content creation channel that could potentially increase the Reach the reach of the Company that we will be pitching.

"""

email_example = """

I hope this message finds you well.

I'm Ritesh from Broke Brothers. We specialize in creating dynamic and engaging Vox pop content that resonates deeply with our audience. Our content style connects with Gen Z and Millennials, who are avid travelers and always on the lookout for reliable and stylish travel gear like American Tourister.

We see a fantastic opportunity to collaborate with American Tourister to create content that not only showcases your products but also highlights the importance of quality and style in travel gear. Our target group is perfect for your brand, and we believe our content can drive significant engagement and sales for American Tourister.

*Key Highlights:*

- Broke Brothers has over 650K followers on Instagram and 300K subscribers on YouTube, ensuring a wide reach.
- Our audience primarily consists of Gen Z and Millennials who love to travel and value high-quality travel gear.
- We have a proven track record of driving high engagement and conversions with our audience.

We propose creating a series of engaging videos that feature American Tourister products, discuss travel tips, and include fun and relatable content that resonates with our viewers. This initiative would not only enhance American Tourister's brand visibility but also connect emotionally with potential customers.

*Links to Our Platforms:*
- [Broke Brothers Instagram](https://www.instagram.com/officialbrokebrothers/)
- [Broke Brothers YouTube](https://www.youtube.com/@officialbrokebrothers)

We'd love to discuss this opportunity further and explore how we can work together to create impactful content that boosts American Tourister’s brand and drives sales.

Looking forward to the opportunity to collaborate.

Best regards,

Ritesh Prakash  
Broke Brothers  
+91 8073700288

"""


run_code = st.button("Run the output")
if run_code:
    results_target = DDGS().text(f"latest news on {target_company}",)
    results_base = DDGS().text(f"OfficialBrokeBrothers Instagram",)
    print(results_target[0]['body'])
    print(results_base[0]['body'])

    output_parser = StrOutputParser()
    chain = llm | output_parser
    skills = chain.invoke(f"Write an email to pitch officialbrokebrothers channel to {target_company} to increase their reach and visibility.\
                           Here's some info on OfficialBrokerBrothers Channel\n {results_base}\n To help you write a better email. Also here's a reference email you can use to maintain the same semantics and not change too much from this.\n {email_example}")
    # skills = chain.invoke({"base_company": base_company+results_base[0]['body'], "target_company": results_target[0]['body']})
    st.write(skills)