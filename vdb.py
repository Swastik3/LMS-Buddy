import getpass
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

from langchain.docstore.document import Document
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_iris import IRISVector


loader =PyPDFLoader("coinchanging.pdf")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=400, chunk_overlap=20)
docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()
# embeddings = FastEmbedEmbeddings()

username = 'demo'
password = 'demo' 
hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
port = '1972' 
namespace = 'USER'
CONNECTION_STRING = f"iris://{username}:{password}@{hostname}:{port}/{namespace}"

print(CONNECTION_STRING)
COLLECTION_NAME = "state_of_the_union_test"

db = IRISVector.from_documents(
    embedding=embeddings,
    documents=docs,
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING,
)

print(f"Number of docs in vector store: {len(db.get()['ids'])}")
query = "dyanmic programming"
docs_with_score = db.similarity_search(query)

print(docs_with_score)