import os
from operator import itemgetter

from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI

from squirrel import vectorstore


def get_llm(model_type="ollama", **kwargs):
    if model_type == "azure":
        load_dotenv()
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv("OPENAI_API_VERSION")
        deployment_name = os.getenv("DEPLOYMENT_NAME")
        return AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version,
            deployment_name=deployment_name,
            temperature=0,
            **kwargs,
        )
    else:
        return ChatOllama(model="mistral", temperature=0, **kwargs)


def get_example(input_example):
    return """
        "user request": "고객 정보 10건 쿼리 해줘"
        "result": ```sql
        SELECT * FROM Customers LIMIT 10;
        ```
    """ + "\n ".join(
        input_example
    )


def get_chat_streaming_response(input_text, input_ddl, input_example, chat_history, database_type="mysql"):
    prompt = get_prompt()

    chain = (
        {
            "grounding": itemgetter("request")
            | vectorstore.as_retriever(
                search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.55, "k": 12}
            )
            | get_page_from_doc,
            "request": itemgetter("request"),
            "examples": itemgetter("examples"),
            "chat_history": itemgetter("chat_history"),
        }
        | prompt
        | capture_and_return
        | get_llm(model_type="azure")
        | StrOutputParser()
    )

    examples = get_example(input_example)

    input_prompt = {
        "request": input_text,
        "examples": examples,
        "chat_history": chat_history,
    }

    for chunks in chain.stream(input_prompt):
        yield chunks


def capture_and_return(data):
    print(data)
    return data


def get_page_from_doc(data):
    print(f"len data {data}")
    pages = map(lambda doc: doc.page_content, data)
    rags = "\n".join(pages)
    print(f"rag {rags}")

    return rags


def get_prompt():
    return ChatPromptTemplate.from_template(
        """
        You are a chatbot that predicts and informs you of congestion in a specific area on a specific date. 
        Please predict future congestion based on the data provided. Answer in Korean.

    ## grounding ddl:
        {grounding}

    ## examples:
        {examples}

    ## chat histories:
        {chat_history}

    ## chat:
        "user request": "{request}"
        "result":
"""
    )
