import os
from operator import itemgetter
import json
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


def get_place_example():
    return """
        "user request": 이번주 토요일 오후 3시 압구정 로데오거리 사람 많아?
        "result":  {"congestion level" : "붐빔", "place_name" : "압구정 로데오거리", "latitude" : "37.527660935102", "longitude" : "127.04070357316", "explain": "약속날인 이번주 토요일 오후 3시의 압구정 로데오거리의 혼잡도를 체크했더니
        `압구정 로데오거리`의 오후 3시의 혼잡도는 붐빔 단계로, 숨이 턱 막힐지도? 사람 조심하세요!"}

        "user request" : 혼잡한 곳을 좋아하는 사람이야 강남역 가고 싶어
        "result" {"congestion level" : "붐빔", "place_name" : "강남역", "latitude" : "37.498095", "longitude" : "127.027610", "explain": "내일 오후 7시 강남역은 혼잡으로 예측돼요. 내일 오후 강남역에서 신나게 놀아보는 건 어때요?"}
        
         "user request" : 여유로운 곳을 좋아하는 사람이야 홍대입구 가고 싶어
        "result" {"congestion level" : "여유", "place_name" : "홍대입구", "latitude" : "37.554371328", "longitude" : "126.926611", "explain": "내일 오전 11시 홍대입구는 여유로울 것으로 예측돼요. 내일 오전 홍대입구에서 여유로운 시간을 보내보세요."}

    """

def get_no_place_example():
    return """
        "user request": 여유로는 곳을 좋아하는 사람이야. 오늘 저녁 약속을 어디갈까? {“question_type” : “place_n”, "place": "everywhere", “weekday” : “수요일” , "date": "2024-04-17", "explain": "nothing", "bbti": "여유”}
        "result": {"congestion level" : "여유", "place_name" : "서울대공원", "latitude" : "37.426449", "longitude" : "127.121420", "explain": "오늘은 18시에는 서울대공원이 한가할 예정이므로 방문하세요!"}  
        
        "user request": 붐비는 곳을 좋아하는 사람이야. 내일 19시에 어디갈지 추천좀 해줘 {“question_type” : “place_n”, "place": "everywhere", “weekday” : “everyday” , "date": "everyday", "explain": "{19시에 어디갈지 추천좀 해줘}", "bbti": "붐빔”}
        "result": {"congestion level" : "붐빔", "place_name" : "강남", "latitude" : "37.497942", "longitude" : "127.027621", "explain": "내일 19시에는 강남, 압구정이 붐빌 예정이므로 방문을 추천드립니다.}
    """


def get_json_format():
    return """
      {"congestion level" : "약간 붐빔", "place_name" : "서울역", "latitude" : "37.123", "longitude" : "127.234", "explain": "내일 오후 3시 서울역은 혼잡할 것으로 예상돼요! 혼잡도는 "약간 붐빔" 수준이며, 약 18,000명에서 20,000명이 이 지역을 이용할 것으로 예상돼요."}
    """


def search_data_from_rag(request, question_type):
    endpoint = os.getenv('AZURE_AI_SEARCH_ENDPOINT')
    credential = AzureKeyCredential(os.getenv('AZURE_AI_SEARCH_API_KEY'))
    index_name = 'prj-prompthon-1' if question_type == "place_y" else 'prj-prompthon-1-cong-lvl'
    filed_name = 'pl_tm_wkd_vector' if question_type == "place_y" else 'cl_tm_wkd_vector'
    api_version = os.getenv('AZURE_AI_SEARCH_API_VERSION')
    embedding_model_name = "text-embedding-ada-002"

    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential,
                                 api_version=api_version)

    embedding = client.embeddings.create(input=request, model=embedding_model_name).data[0].embedding
    vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=20, fields=filed_name, exhaustive=True)

    results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
        select=["place_name", "time", "cong_lvl", "minpp", "maxpp"],
    )

    return results

def get_chat_streaming_response(request, chat_history, bbti):
    response = filter_user_request(request)
    filtered_user_request = json.loads(response)
    question_type = filtered_user_request["question_type"]
    print(filtered_user_request)

    if question_type == "place_y":
        return question_type, get_chat_streaming_response_about_place(filtered_user_request, request, chat_history, bbti, question_type)
    elif question_type == "place_n":
        return question_type, get_chat_streaming_response_about_no_place(filtered_user_request, request, chat_history, bbti, question_type)
    elif question_type == "nothing":
        return question_type, response

# place_y
def get_chat_streaming_response_about_place(filtered_user_request, request, chat_history, bbti, question_type):
    prompt = get_place_prompt()

    chain = (
            {
                "grounding": itemgetter("grounding"),
                "request": itemgetter("request"),
                "examples": itemgetter("examples"),
                "chat_history": itemgetter("chat_history"),
                "json_format": itemgetter("json_format"),
                "bbti": itemgetter("bbti"),
            }
            | prompt
            | capture_and_return
            | get_llm()
            | StrOutputParser()
    )

    index = f"{filtered_user_request['place']} {filtered_user_request['weekday']} {filtered_user_request['time']}"

    input_prompt = {
        "request": request,
        "grounding": json_to_string(search_data_from_rag(index, question_type)),
        "examples": get_place_example(),
        "chat_history": chat_history,
        "bbti": bbti,
        "json_format": get_json_format()
    }
    result = chain.invoke(input_prompt)
    print(result)
    return result

#
def get_chat_streaming_response_about_no_place(filtered_user_request, request, chat_history, bbti, question_type):
    prompt = get_no_place_prompt()

    chain = (
            {
                "grounding": itemgetter("grounding"),
                "request": itemgetter("request"),
                "examples": itemgetter("examples"),
                "chat_history": itemgetter("chat_history"),
                "json_format": itemgetter("json_format"),
                "bbti": itemgetter("bbti"),
            }
            | prompt
            | capture_and_return
            | get_llm()
            | StrOutputParser()
    )

    index = f"{filtered_user_request['cong_lvl']} {filtered_user_request['weekday']} {filtered_user_request['time']}"

    input_prompt = {
        "request": request,
        "grounding": json_to_string(search_data_from_rag(index, question_type)),
        "examples": get_no_place_example(),
        "chat_history": chat_history,
        "bbti": bbti,
        "json_format": get_json_format()
    }
    result = chain.invoke(input_prompt)
    print(result)
    return result


def get_information_of_place(place_name):
    response1 = client.chat.completions.create(
        model=os.getenv("DEPLOYMENT_NAME"),
        messages=[
            {"role": "system", "content": """너는 특정 지역과 관련된 연관 검색어를 알려주는 챗봇이야. 
                                        결과는 리스트 형태로 알려줘. 결과형식: "검색어1, 검색어2, 검색어3"
                                        """},
            {"role": "user", "content": f"{place_name} 연관 검색어 Top 30개 알려줘"},

        ],
        temperature=0,
        max_tokens=1000
    )

    response2 = client.chat.completions.create(
        model=os.getenv("DEPLOYMENT_NAME"),
        messages=[
            {"role": "system", "content": """이전 한달간의 value를 랜덤하게 만들어줘
                                                결과는 다음과 같이 json list 형식으로 알려주면 돼.
                                                다른 말은 하지 말고 아래 결과 형식대로 json list만 제공해줘.
                                                결과형식: "[{"time" : "2024-04-16", "value" : 10000},{"time" : "2024-04-17", "value" : 23410}]"
                                            """},
            {"role": "user", "content": f"10000 이상의 값으로 이전 한달간의 value를 랜덤하게 제작해줘.  오늘은 4월 17일이야."},
        ],
        temperature=0,
        max_tokens=1000
    )
    return {"text" : response1.choices[0].message.content, "search" : response2.choices[0].message.content}


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

def get_first_prompt():
    return """
    너는 사용자의 질문을 듣고 필요한 정보를 추출해내는 봇이야.
    너는 반드시 다음과 같은 json 형식으로 대답해야해
    {"question_type" : "", "place": "", "weekday" : "", "date": "", "time": "", "response" : "" }
    
    질문 유형은 다음과 같이 3개로 분류해줘
    ["place_y", "place_n", "nothing"]
    질문에 위치가 지정되어있으면 place_y로 대답해줘
    질문에 위치가 없으면 place_n로 대답해줘
    질문이 맥락이 없다면 nothing으로 대답해줘
    
    요일은 '월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일'로 한국시간으로 계산해서 대답해줘
    
    위치를 말해줬으면 place를 위치로 대답해주고, 말해주지 않았다면 everywhere로 대답해줘
    
    날짜는 오늘이나 내일만 한국 표준시간 기준으로 yyyy-mm-dd 형식으로 대답해주는데 내일이라고 하면 다음날로 계산해서줘. 만약 받은 질문에서 날짜가 오늘인지 내일인지 정확하게 모른다면 다시 물어봐줘
    
    사용자가 시간에 대해 언급했다면 time 필드에 넣어주고, 언급하지 않았다면 빈칸으로 놔둬.
    
    만약 question_type이 place_y이지만 질문에서 오늘인지 내일인지 정확하게 판단할 수 없다면 다시 물어봐줘
    
    만약 question_type이 nothing인 경우 response에 질문에 대한 답을 해줘.
    
    examples:
        내일 광화문에 사람이 많을까?
        {"question_type": "place_y", "place": "광화문", "weekday": "목요일", "date": "2024-04-18", "time" :"", "response" : ""}
        
        지금 갈만한 한산한 곳이 있을까?
        {"question_type": "place_n", "place": "everywhere", "weekday": "수요일", "date": "2024-04-17", "time" :"", "response" : ""}
        
        내일 어디가는게 좋을까?
        {"question_type": "place_n", "place": "everywhere", "weekday": "목요일", "date": "2024-04-18", "time" :"", "response" : ""}
         
        내일 오후 3시에 광화문 혼잡도는 어떨까?
        {"question_type": "place_n", "place": "everywhere", "weekday": "목요일", "date": "2024-04-18", "time" :"15시", "response" : ""}
     
        뭐하냐?
        {"question_type": "nothing", "place": "", "weekday": "", "date": "", "time" :"", "response" :"글쎄요 당신 생각 중?"}
    """

def filter_user_request(user_input):
    prompt = get_first_prompt()
    response = client.chat.completions.create(
        model=os.getenv("DEPLOYMENT_NAME"),
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input},
        ],
        temperature=0,
        max_tokens=1000
    )

    return response.choices[0].message.content


def get_place_prompt():
    return ChatPromptTemplate.from_template(
        """
        You are a chatbot that predicts and informs you of congestion in a specific area. 
        Please predict future congestion based on the data provided. Answer in Korean.
        When the user doesn't tell you the time information, recommend the time according to the user's preference
            질문자의 성향: {bbti}
        If users like to be crowded, let them know the estimated time for which the population density is high, and if they like to be relaxed, let them know the estimated time for which the population density is low
          
        - Please have a good way of speaking in the Explain section


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


def get_no_place_prompt():
    return ChatPromptTemplate.from_template(
        """
        너는 사용자가 어디에 방문해야 하는지 추천해주는 챗봇이야.

        원래 질문은 {chat_history}야.
        
        - 제공되는 데이터는 다음과 같아.
            {“question_type” : “place_n”, "place": "everywhere", “weekday” : “” , "date": "", "explain": "{원래 질문}", "bbti": ""}
        
        - bbti는 다음과 같이 4개로 나뉘어 있어.
            ['여유', '보통', '약간 붐빔', '붐빔']
        
        - 사용자가 날짜나 요일을 지정하지 않았다면 제공되는 데이터의 date, weekday는 everyday야.
        
        - 사용자의 장소의 혼잡도 성향은 {bbti}를 좋아하기 때문에 이를 고려해서 추천해줘.
        
        - 위의 맥락과 제공된 데이터를 바탕으로 어느 장소에 어느 시간에 가야 하는지 추천해줘.
        
        - date가 현재 날짜와 같으면 오늘로 표현하고, 1일 후면 내일로 표현해줘.
        
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
    response = filter_user_request("내일 오후 8시 서울역 혼잡도는 어때?")
    filtered_user_request = json.loads(response)
    question_type = filtered_user_request["question_type"]
    print(filtered_user_request)
