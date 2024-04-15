import streamlit as st  # all streamlit commands will be available through the "st" alias
from folium import folium
from streamlit_folium import st_folium

from utils import chatlib

st.set_page_config(
    page_title="안붐빌지도?",
    page_icon="👀",
)  # HTML title
st.title(":orange[?] 안붐빌지도 👀")  # page title

map = folium.Map(location=[37.572504, 126.999001], zoom_start=13, control_scale=True)

st_data = st_folium(map, width=800)

if "chat_history" not in st.session_state:  # see if the chat history hasn't been created yet
    st.session_state.chat_history = []  # initialize the chat history
st.sidebar.header("편하게 물어보세요 👀")  # page title

# Re-render the chat history (Streamlit re-runs this script, so need this to preserve previous chat messages)
for message in st.session_state.chat_history:  # loop through the chat history
    with st.sidebar.chat_message(
        message["role"]
    ):  # renders a chat line for the given role, containing everything in the with block
        st.sidebar.markdown(message["text"])  # display the chat content

input_text = st.sidebar.chat_input("언제 어디를 가고 싶은지 물어봐요 ")  # display a chat input box

if input_text:  # run the code in this if block after the user submits a chat message
    with st.sidebar.chat_message("user"):  # display a user chat message
        st.sidebar.markdown(input_text)  # renders the user's latest message

    with st.sidebar.chat_message("assistant"):  # display a bot chat message
        result = st.sidebar.write_stream(
            chatlib.get_chat_streaming_response(
                input_text=input_text,
                chat_history=st.session_state.chat_history
            )
        )  # display bot's latest response

    st.session_state.chat_history.append(
        {"role": "user", "text": input_text}
    )  # append the user's latest message to the chat history

    st.session_state.chat_history.append(
        {"role": "assistant", "text": result}
    )  # append the bot's latest message to the chat history
