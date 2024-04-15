from dotenv import load_dotenv
from langchain_community.vectorstores.chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings

DB_PATH = f"vectorstores/db/"


def get_default_data():
   pass ### csv 데이터 읽어와주세요 ㅠ


def create_vector_db():
    texts = get_default_data().split("\n")
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment="text-embedding-ada-002",
    )
    vectorstore = Chroma.from_texts(texts=texts[:-1], embedding=embeddings, persist_directory=DB_PATH)
    vectorstore.persist()
    return vectorstore
