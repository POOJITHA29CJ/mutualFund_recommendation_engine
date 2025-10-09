import streamlit as st
from langchain.callbacks.streamlit import StreamlitCallbackHandler
from main import agent_executor

st.set_page_config(
    page_title="Mutual Fund Assistant",
    layout="centered",
    initial_sidebar_state="auto",
)


st.markdown(
    """
    <style>
    div.stButton > button:first-child {
        background-color:black; 
        color: white;              
        border-radius:5px;       
        font-weight: bold;
        border: black;
        font:Sans-serif
    }
    div.stButton > button:first-child:hover {
        background-color: black;
        color: orange;              
    }
    div[data-testid="stHorizontalBlock"] div.stButton:nth-child(1) button {
        background-color:#F8B88B;
        color: black;
        font-weight: bold;
        border-radius: 8px;
    }
    div[data-testid="stHorizontalBlock"] div.stButton:nth-child(1) button:hover {
        background-color:black;
        color:white;
    }

   
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.title("Mutual Fund Assistant")
    st.title("Hellooo Poojitha !")
    st.markdown(
        "Welcome! I'm your AI-powered assistant for mutual fund inquiries. "
        "I can help you with information about fund managers, categories, sectors, "
        "and analytical insights."
    )
    st.markdown("---")

    if st.button("Clear Chat History"):
        st.session_state["messages"] = []
        st.rerun()


if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    st.chat_message(msg["role"], avatar=avatar).write(msg["content"])


def send_prompt_starter(prompt: str):
    """Helper to send a starter prompt as if user typed it."""
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.session_state["starter_clicked"] = prompt
    st.rerun()


if len(st.session_state["messages"]) == 0:
    st.markdown("Hi there 👋! How can i help you...")
    st.markdown("---")
    st.markdown("##### Or try one of these starters:")
    cols = st.columns(2)
    with cols[0]:
        st.button(
            "What are the funds managed by Ashish Aggarwal?",
            on_click=send_prompt_starter,
            args=("What are the funds managed by Ashish Aggarwal?",),
        )
    with cols[1]:
        st.button(
            "Show me funds with low volatility",
            on_click=send_prompt_starter,
            args=("Show me all funds with low volatility",),
        )


if user_input := st.chat_input("Ask me about mutual funds...") or st.session_state.get(
    "starter_clicked"
):
    if user_input is None:
        user_input = st.session_state.pop("starter_clicked")

    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user", avatar="👤").write(user_input)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                st_callback_container = st.container()
                st_callback = StreamlitCallbackHandler(st_callback_container)

                response = agent_executor.invoke(
                    {"input": user_input},
                    {"callbacks": [st_callback]},
                )
                output = response["output"]

                st.write(output)

                st.session_state["messages"].append(
                    {"role": "assistant", "content": output}
                )

            except Exception as e:
                error_message = f"Sorry, an error occurred: {e}"
                st.error(error_message)
                st.session_state["messages"].append(
                    {"role": "assistant", "content": error_message}
                )
