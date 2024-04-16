import os
from operator import itemgetter

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents._generated.models import VectorizedQuery
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from openai.lib.azure import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "").strip(),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION")
)


def get_llm(**kwargs):
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


def get_example():
    return """
        "user request": 이번주 토요일 오후 3시 압구정 로데오거리 사람 많아?
        "result":  {"congestion level" : "혼잡", "place_name" : "압구정 로데오거리", "latitude" : "37.527660935102", "longitude" : "127.04070357316", "explain": "약속날인 이번주 토요일 오후 3시의 압구정 로데오거리의 혼잡도를 체크했더니
`압구정 로데오거리`의 오후 3시의 혼잡도는 혼잡 단계로, 숨이 턱 막힐지도? 사람 조심하세요!"
"}
    """


def get_json_format():
    return """
      {"congestion level" : "약간붐빔", "place_name" : "서울역", "latitude" : "37.123", "longitude" : "127.234", "explain": "내일 오후 3시 서울역은 혼잡할 것으로 예상돼요! 혼잡도는 "약간 붐빔" 수준이며, 약 18,000명에서 20,000명이 이 지역을 이용할 것으로 예상돼요."}
    """


def search_data_from_rag(request):
    endpoint = os.getenv('AZURE_AI_SEARCH_ENDPOINT')
    credential = AzureKeyCredential(os.getenv('AZURE_AI_SEARCH_API_KEY'))
    index_name = os.getenv('AZURE_AI_SEARCH_INDEX')
    api_version = os.getenv('AZURE_AI_SEARCH_API_VERSION')
    embedding_model_name = "text-embedding-ada-002"

    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential,
                                 api_version=api_version)

    embedding = client.embeddings.create(input=request, model=embedding_model_name).data[0].embedding
    vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=20, fields="pl_tm_wkd_vector", exhaustive=True)

    results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
        select=["place_name", "time", "cong_lvl", "minpp", "maxpp"],
    )

    return results


def get_chat_streaming_response(request, chat_history):
    prompt = get_prompt()

    chain = (
            {
                "grounding": itemgetter("grounding"),
                "request": itemgetter("request"),
                "examples": itemgetter("examples"),
                "chat_history": itemgetter("chat_history"),
                "json_format": itemgetter("json_format")
            }
            | prompt
            | capture_and_return
            | get_llm()
            | StrOutputParser()
    )

    input_prompt = {
        "request": request,
        "grounding": json_to_string(search_data_from_rag(request)),
        "examples": get_example(),
        "chat_history": chat_history,
        "json_format": get_json_format()
    }
    result = chain.invoke(input_prompt)
    print(result)
    return result


def capture_and_return(data):
    print(f"total prompt: {data}")
    return data


def json_to_string(results):
    grounding = ""
    for result in results:
        grounding = grounding + f"""
        장소: {result['place_name']}
        시간: {result['time']} 
        최대 인원수: {result['maxpp']}
        최소 인원수: {result['minpp']}
        혼잡도: {result['cong_lvl']}
        """
    return grounding


def get_prompt():
    return ChatPromptTemplate.from_template(
        """
        You are a chatbot that predicts and informs you of congestion in a specific area on a specific date. 
        Please predict future congestion based on the data provided. Answer in Korean.

        - 

        - Generate output as the following json format. 
            {json_format}

        - There are four levels of congestion ["여유", "보통", "약간 붐빔", "혼잡"]

        ## grounding:
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


if __name__ == '__main__':
    get_chat_streaming_response("내일 서울역 혼잡도 알려줘", "")