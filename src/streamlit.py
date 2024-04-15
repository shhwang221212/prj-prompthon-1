import streamlit as st  # all streamlit commands will be available through the "st" alias

from utils import chatlib

st.set_page_config(
    page_title="Query 생성기",
    page_icon="🐿",
)  # HTML title
st.title("🌰 Query 생성기 🐿️")  # page title


if "ddl_history" not in st.session_state:
    st.session_state.ddl_history = []

if "example_history" not in st.session_state:
    st.session_state.example_history = []

if "chat_history" not in st.session_state:  # see if the chat history hasn't been created yet
    st.session_state.chat_history = []  # initialize the chat history

st.sidebar.markdown("## 🌰 Database 종류")
database_type = st.sidebar.text_input(":orange[Database Type:  ]", "mysql")

st.sidebar.markdown("## 🌰 테이블 DDL 추가")
ddl_input = st.sidebar.text_area(":orange[Enter DDL:  ]")

if st.sidebar.button("DDL Sumit 🥜", use_container_width=True):
    st.session_state.ddl_history.append(ddl_input)
    chatlib.vectorstore.aadd_texts(ddl_input)

for ddl in st.session_state.ddl_history:
    st.sidebar.markdown(f"```{ddl}```")

st.sidebar.markdown("## 🌰 답변 예시 추가")

request = st.sidebar.text_input(":orange[User Request:  ]")
result = st.sidebar.text_area(":orange[Result:  ]")

if st.sidebar.button("Example Sumit 🥜", use_container_width=True):
    added_example = f""" \nuser request: {request}
                        \nresult: ```{result}```"""

    st.session_state.example_history.append(added_example)

for example in st.session_state.example_history:
    st.sidebar.markdown(example)

# Re-render the chat history (Streamlit re-runs this script, so need this to preserve previous chat messages)
for message in st.session_state.chat_history:  # loop through the chat history
    with st.chat_message(
        message["role"]
    ):  # renders a chat line for the given role, containing everything in the with block
        st.markdown(message["text"])  # display the chat content

input_text = st.chat_input("다람쥐와 함께 쿼리를 만들어 보아요🐿️ ")  # display a chat input box

if input_text:  # run the code in this if block after the user submits a chat message
    with st.chat_message("user"):  # display a user chat message
        st.markdown(input_text)  # renders the user's latest message

    with st.chat_message("assistant"):  # display a bot chat message
        result = st.write_stream(
            chatlib.get_chat_streaming_response(
                input_text=input_text,
                input_ddl=st.session_state.ddl_history,
                input_example=st.session_state.example_history,
                chat_history=st.session_state.chat_history,
                database_type=database_type,
            )
        )  # display bot's latest response

    st.session_state.chat_history.append(
        {"role": "user", "text": input_text}
    )  # append the user's latest message to the chat history

    st.session_state.chat_history.append(
        {"role": "assistant", "text": result}
    )  # append the bot's latest message to the chat history
