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
context_check_template="""You are a bot and your job is to verify if answer provided by me is relvant and correct in respect to the question or not.
Return yes if you think the answer is correct and no if you think the answer is incorrect.

this is the question {question}
this is the context {context}

NOTE- Only respond with yes or no.

"""
prompt = ChatPromptTemplate.from_template(template)

def execut(query):
    print("Executing query...")
    chain = prompt | model | parser
    data = search_q(query, "notes")
    print("Context retrieved:", data)
    out = chain.invoke({"question": query, "context": data})
    validity= answer_ver(query, out)
    response=out
    if not validity:
        response=bail()
    return response

def answer_ver(query, context):
    print("Verifying answer...")
    prompt2 = ChatPromptTemplate.from_template(context_check_template)
    chain =  prompt2 | model | parser
    response = chain.invoke({"question": query, "context": context})
    if response == "yes":
        return True
    return False

def bail():
    return "Sorry, I cannot help you with that question at this time. If you have any other questions, feel free to ask."

if __name__ == "__main__":
    query = "how  can you solve coin changing"
    output = execut(query)
    print("Response:", output)