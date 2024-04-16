import streamlit as st  # all streamlit commands will be available through the "st" alias
from streamlit_folium import st_folium

import folium

from utils import chatlib
import json

st.set_page_config(
    page_title="안붐빌지도?",
    page_icon="👀",
)  # HTML title
st.title(":orange[?] 안붐빌지도 👀")  # page title
m = folium.Map(location=[37.572504, 126.999001], zoom_start=16, control_scale=True)
folium.Marker(
    [37.572504, 126.999001], popup="Liberty Bell", tooltip="Liberty Bell"
).add_to(m)

st_data = st_folium(m, width=725)

if "chat_history" not in st.session_state:  # see if the chat history hasn't been created yet
    st.session_state.chat_history = []  # initialize the chat history

st.sidebar.header("혼잡 수치")  # page title
side_container0 = st.sidebar.container(border=True)

side_container0.image('https://github.com/ju-ong/test-repo/assets/126046181/7b2e9c0c-1591-4279-984b-e6575983c022')
st.sidebar.header("편하게 물어보는 공간! 👀")  # page title

side_container1 = st.sidebar.container(border=True, height=500)

side_container2 = st.sidebar.container()
input_text = side_container2.chat_input("언제 어디를 가고 싶은지 물어봐요 ")  # display a chat input box


# Re-render the chat history (Streamlit re-runs this script, so need this to preserve previous chat messages)
for message in st.session_state.chat_history:  # loop through the chat history
    with side_container1.chat_message(
        message["role"]
    ):  # renders a chat line for the given role, containing everything in the with block
        if message["role"] == "assistant":
            side_container1.markdown(message["text"]["explain"])  # display the chat content
        else:
            side_container1.markdown(message["text"])



if input_text:  # run the code in this if block after the user submits a chat message
    with side_container1.chat_message("user"):  # display a user chat message
        side_container1.markdown(input_text)  # renders the user's latest message

    chat_response = chatlib.get_chat_streaming_response(
        request=input_text,
        chat_history=st.session_state.chat_history
    )

    json_response = json.loads(chat_response)

    with side_container1.chat_message("assistant"):  # display a bot chat message
        side_container1.markdown(json_response["explain"])  # display bot's latest response

    st.session_state.chat_history.append(
        {"role": "user", "text": input_text}
    )  # append the user's latest message to the chat history

    st.session_state.chat_history.append(
        {"role": "assistant", "text": chat_response}
    )  # append the bot's latest message to the chat history
