from langchain.tools.retriever import create_retriever_tool
import os
import ast
from dotenv import load_dotenv
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Pinecone as Pine
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import argparse
from typing import List, Dict, Any
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain_core.runnables import RunnablePassthrough
from langgraph.graph import StateGraph, END, START
from langchain_iris import IRISVector


load_dotenv()
os.environ['OPENAI_API_KEY']=os.getenv("OPENAI_API_KEY")


model1 = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
model2 = ChatOpenAI(model="gpt-4o", temperature=0)
parser = StrOutputParser()
embeddings = OpenAIEmbeddings()
username = 'demo'
password = 'demo' 
hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
port = '1972' 
namespace = 'USER'
CONNECTION_STRING = f"iris://{username}:{password}@{hostname}:{port}/{namespace}"
COLLECTION_NAME = "main"
notes = IRISVector(
    embedding_function=embeddings,
    dimension=1536,
    # collection_name=COLLECTION_NAME,
    collection_name="notes",
    connection_string=CONNECTION_STRING)
canjson = IRISVector(
    embedding_function=embeddings,
    dimension=1536,
    # collection_name=COLLECTION_NAME,
    collection_name="canjson",
    connection_string=CONNECTION_STRING)
syllabi = IRISVector(
    embedding_function=embeddings,
    dimension=1536,
    # collection_name=COLLECTION_NAME,
    collection_name="main",
    connection_string=CONNECTION_STRING)

llm = model2
llm2=model1

context_selection_prompt="""You are an educational assistant and your job is to select the type of context that would best answer an user's question.
There are three types of context available:
1) Note and Book based context- This type of context contains information about the actual topics and concepts covered in the course. So any doubt or question that involves study material/ course content would use this
2) Syllabus based context- This type of context contains information about the syllabus of the course. So any doubt or question that involves syllabus, course structure, policies etc would use this
3) Assignment and Announcement- This type of context contains information about assignments, their due dates, announcements etc. So any doubt or question that involves assignments, announcements etc would use this

Respond with the number corresponding to the type of context you want to select for the question. For example if the question requires Note and book Based context return 1
{question}

NOTE- Only respond with the number 1, 2 or 3"""

template = """You are an educational assistant 
and your job is to answer the question asked by the user based on the context provided.

This is the question: {question} 
This is the context: {context}

"""
context_check_template="""You are a relevancy checker and you need to check if my answer is relevant to the question or not. You do not need to check about the correctness
of the answer, just the relevancy as you do not have any information regarding the correctness.

this is the question:: {question}
this is my answer:: {context}

If you think the answer is relevant return 1 and if you think the answer is irrelevant return 2

NOTE- Only respond with 1 or 2

"""
def select_context(state):
    question = state["question"]
    selection = llm.invoke(context_selection_prompt.format(question=question))
    selection=selection.content
    print(selection)
    return {"context_type": int(selection)}

def get_note_context(state):
    question = state["question"]
    search_result = notes.similarity_search(question, k=3)

    return {"context": search_result}

def get_syllabus_context(state):
    question = state["question"]
    search_result = syllabi.similarity_search(question, k=3)
    return {"context": search_result}

def get_canjson_context(state):
    question = state["question"]
    search_result= canjson.similarity_search(question, k=3)
    return {"context": search_result}

def check_answer(state):
    question = state["question"]
    context = state["context"]
    answer = llm2.invoke(context_check_template.format(context=context, question=question))
    answer=answer.content
    print(answer)
    return {"validation_type": int(answer)}
    
def generate_answer(state):
    context = state["context"]
    print(context)
    question = state["question"]
    answer = llm.invoke(template.format(context=context, question=question))
    answer=answer.content

    print(answer)
    return {"answer": answer}

def dodge_question(state):
    return {"answer": "Sorry, I cannot help you with that question at this time. If you have any other questions, feel free to ask."}

class GraphState(Dict):
    question: str
    context_type: int
    validation_type: int
    context: str
    answer: str

workflow = StateGraph(GraphState)

workflow.add_node("select_context", select_context)
workflow.add_node("get_note_context", get_note_context)
workflow.add_node("get_syllabus_context", get_syllabus_context)
workflow.add_node("get_canjson_context", get_canjson_context)
workflow.add_node("check_answer", check_answer )
workflow.add_node("generate_answer", generate_answer)
workflow.add_node("dodge_question", dodge_question)


workflow.add_edge(START, "select_context")
workflow.add_conditional_edges(
    "select_context",
    lambda x: x["context_type"],
    {
        1: "get_note_context",
        2: "get_syllabus_context",
        3: "get_canjson_context"
    }
)
workflow.add_edge("get_note_context", "generate_answer")
workflow.add_edge("get_syllabus_context", "generate_answer")
workflow.add_edge("get_canjson_context", "generate_answer")
workflow.add_edge("generate_answer", "check_answer")
workflow.add_conditional_edges("check_answer",
    lambda x: x["validation_type"],
    {
        1: END,
        2: "dodge_question",
        
    })
workflow.add_edge("dodge_question", END)

graph = workflow.compile()

def run_rag_agent(question: str) -> Dict[str, Any]:
    return graph.invoke({"question": question})

result = run_rag_agent("what are some important public speaking skills")
print(result)
