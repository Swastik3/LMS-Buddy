import os
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from vdb import search_q
from langchain_openai import OpenAI

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

model = OpenAI()
parser = StrOutputParser()

template = """You are an educational assistant 
and your job is to answer the question asked by the user based on the context provided.

This is the question: {question} 
This is the context: {context}

"""

prompt = ChatPromptTemplate.from_template(template)

def execut(query):
    print("Executing query...")
    chain = prompt | model | parser
    data = search_q(query, "notes")
    print("Context retrieved:", data)
    response = chain.invoke({"question": query, "context": data})
    return response

if __name__ == "__main__":
    query = "how  can you solve coin changing"
    output = execut(query)
    print("Response:", output)