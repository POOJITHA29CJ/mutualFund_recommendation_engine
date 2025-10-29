import streamlit as st
from langchain.callbacks.streamlit import StreamlitCallbackHandler
from main import agent_executor, memory

st.set_page_config(
    page_title="FinSight Assistant",
    layout="centered",
    initial_sidebar_state="auto",
)

st.markdown(
    """
    <style>
    /* CSS Variables for easy color management */
    :root {
        --primary-bg: #FFFFFF;
        --secondary-bg: #F0F2F6;
        --sidebar-bg: #0A2540;
        --text-color: #333333;
        --sidebar-text-color: #FFFFFF;
        --accent-color: #00A388;
        --accent-color-hover: #007A63; 
    }

    /* General body and chat input styling */
    body {
        color: var(--text-color);
    }
    
    .stTextInput > div > div > input {
        background-color: var(--secondary-bg);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p {
        color: var(--sidebar-text-color);
    }

    /* Sidebar Button Styling */
    [data-testid="stSidebar"] div.stButton > button {
        background-color: transparent;
        color: var(--sidebar-text-color);
        border: 1px solid var(--sidebar-text-color);
        width: 100%;
        font-weight: bold;
        border-radius: 5px;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        background-color: transparent;
        color: black;
        border-color: var(--accent-color);
    }

    /* Prompt Starter Button Styling */
    div[data-testid="stHorizontalBlock"] div.stButton > button {
        background-color: #0A2540;
        color: white;
        border: black;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
    }
    div[data-testid="stHorizontalBlock"] div.stButton > button:hover {
        background-color: transparent;
        color: var(--primary-bg);
        border-color: var(--accent-color);
    }

    /* Chat bubble styling */
    [data-testid="stChatMessage"]:has(span[data-testid="chat-avatar-user"]) {
        background-color: var(--secondary-bg);
    }
    
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.title("FinSight Assistant")
    st.markdown("---")  
    st.markdown(
        "Welcome! I'm your AI-powered assistant for mutual fund inquiries. "
        "I can help you with information about fund managers, categories, sectors, "
        "and analytical insights."
    )
    st.markdown("---")

    if st.button("Clear Chat History"):
        st.session_state["messages"] = []
        memory.clear()
        st.rerun()
    if st.button("Print Memory to Terminal"):
        print("==== Agent Memory ====")
        for msg in memory.buffer:
            role = "User" if msg.type == "human" else "Assistant"
            print(f"{role}: {msg.content}")
        print("=====================")


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
    st.markdown("Hi there 👋! How can I help you today?")
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
