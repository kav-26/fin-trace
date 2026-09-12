from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

response = llm.invoke("In one sentence, why might a company's profitability decline even if revenue grows?")
print(response.content)