import streamlit as st  # all streamlit commands will be available through the "st" alias
from folium.plugins import GroupedLayerControl
from streamlit_folium import st_folium
from streamlit_chat import message
import folium
import pandas as pd
import numpy as np

from wordcloud import WordCloud
import matplotlib.pyplot as plt

from utils.chatlib import get_information_of_place
from utils.chatmessagelib import get_cong_image, get_dummy_search_value, get_cong_small_image, get_color_by_cong
from utils import chatlib
import json


st.set_page_config(
    page_title="안붐빌지도?",
    page_icon="👀",
    layout="wide",
)  # HTML title
st.title(":orange[?] 안붐빌지도 👀")  # page title


if "chat_history" not in st.session_state:  # see if the chat history hasn't been created yet
    st.session_state.chat_history = []  # initialize the chat history

if 'user' not in st.session_state:
    st.session_state['user'] = []

if 'chatbot' not in st.session_state:
    st.session_state['chatbot'] = []

if 'location' not in st.session_state:
    st.session_state['location'] = [37.498095, 127.027610]

if 'area_info' not in st.session_state:
    st.session_state['area_info'] = {"congestion level" : "혼잡",
                                     "place_name" : "강남역",
                                     "latitude" : "37.498095",
                                     "longitude" : "127.027610",
                                     "text": "강남역핫플,클럽,쇼핑,레스토랑,카페,뷔페,술집,쇼핑몰,패션,미용실,맛집,놀거리,음식점,가게,이색카페,바,분위기좋은음식점,문화,유흥,강남,쇼핑센터,이벤트,화려한,유행,멋진장소,연예인,건물,한류,명소,엔터테인먼트"
                                     }


st.sidebar.image("https://github.com/shhwang221212/prj-prompthon-1/assets/126046181/33c10757-cceb-4331-9a3e-994471a17f6d",
                 width= 200)
side_container0 = st.sidebar.container(border=True)
col1, col2, col3, col4 = side_container0.columns(4)

bbti = "여유"

with col1:
    st.image("https://github.com/shhwang221212/prj-prompthon-1/assets/126046181/7e820597-e61e-4b60-84ef-aa85dac50a1a", width=100)
    lev1 = st.checkbox(" ")
with col2:
    st.image("https://github.com/shhwang221212/prj-prompthon-1/assets/126046181/39dc033b-dffa-45a6-b1d6-a2b82a249733", width=100)
    lev2 = st.checkbox("   ")
with col3:
    st.image("https://github.com/shhwang221212/prj-prompthon-1/assets/126046181/afb15bf1-7672-4697-90fa-954e5de99046", width=100)
    lev3 = st.checkbox("    ")
with col4:
    st.image("https://github.com/shhwang221212/prj-prompthon-1/assets/126046181/ea835854-1d32-4cfb-9745-ed4ae4db695d", width=100)
    lev4 = st.checkbox("      ")

if lev1:
    bbti = "여유"
if lev2:
    bbti = "보통"
if lev3:
    bbti = "약간붐빔"
if lev4:
    bbti = "혼잡"

st.sidebar.header("어디든 데려가줄게 👀")  # page title

side_container1 = st.sidebar.container(border=True, height=500)

side_container2 = st.sidebar.container()
input_text = side_container2.chat_input("언제 어디를 가고 싶은지 물어봐요")  # display a chat input box

# rerender
if st.session_state['chatbot']:
    for i in range(len(st.session_state['chatbot'])):
        with side_container1:
            message(st.session_state['user'][i], is_user=True, key=str(i) + '_user', avatar_style="no-avatar")
            message(st.session_state["chatbot"][i]["explain"], key=str(i), avatar_style="icons")

            if "congestion level" in st.session_state["chatbot"][i]:
                honzap_image = get_cong_image(st.session_state["chatbot"][i]["congestion level"])
                st.image(honzap_image)

if input_text:
    with side_container1:
        message(input_text, is_user=True, avatar_style="no-avatar")

    type, chat_response = chatlib.get_chat_streaming_response(
        request=input_text,
        chat_history=st.session_state.chat_history,
        bbti=bbti
    )

    if type == "place_y" or type == "place_n" :
        json_response = json.loads(chat_response)
        response = json_response["explain"]
    else:
        json_response = {}
        json_response["explain"] = chat_response



    with side_container1:
        message(json_response["explain"], avatar_style="icons")
        if "congestion level" in json_response:
            honzap_image = get_cong_image(json_response["congestion level"])
            st.image(honzap_image)

    st.session_state.user.append(input_text)
    st.session_state.chatbot.append(json_response)

    if "place_name" in json_response:
        st.session_state.chat_history.append(
            {"role": "user", "text": input_text}
        )
        st.session_state.chat_history.append(
            {"role": "assistant", "text": chat_response}
        )
        st.session_state['area_info'] = json_response
        st.session_state['location'] = [json_response["latitude"], json_response["longitude"]]
        st.session_state['area_info']['text'] = get_information_of_place(json_response['place_name'])['text']


left, right = st.columns([2,1])

with left:
    m = folium.Map(st.session_state['location'], zoom_start=16)
    color = get_color_by_cong(st.session_state['area_info']["congestion level"])
    folium.Marker(
        st.session_state['location'], popup=st.session_state['area_info']["place_name"] + " " + st.session_state['area_info']["congestion level"], tooltip="<img src='" +  get_cong_small_image(st.session_state['area_info']["congestion level"])+ "' width=100>",
        icon=folium.Icon(color=color)
    ).add_to(m)
    st_data = st_folium(m, width=800, height=800, returned_objects=["last_object_clicked"])


with (right):
    font_path = "/Users/juyounglee/Downloads/prj-prompthon-1/resource/D2.ttf"
    st.set_option('deprecation.showPyplotGlobalUse', False)

    right_mk = st.markdown(f"#### 💡 {st.session_state['area_info']['place_name']} 어때 :orange[?]")
    right_image = st.image(get_cong_image(st.session_state['area_info']['congestion level']))
    st.markdown("#### 👀 일자별 검색량")
    chart_data = pd.DataFrame(get_dummy_search_value(), columns=["time", "value"], )
    right_line_chart = st.line_chart(chart_data, height=150, x ="time", y ="value")
    st.markdown("#### 👀 :orange[Top30] 연관 키워드")

    # Create some sample text
    if "text" in st.session_state['area_info']:
        text =st.session_state['area_info']["text"]

    # Create and generate a word cloud image:
    wordcloud = WordCloud(background_color="white", font_path=font_path).generate(text)

    # Display the generated image:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    right_pyplot = st.pyplot()


