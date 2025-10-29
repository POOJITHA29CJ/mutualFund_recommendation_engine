# import langchain
from dotenv import load_dotenv
from services.neo4j_tool import neo4j_query
from services.mongodb_tool import mongodb_analytical_query
from services.recommendation_tool import find_similar_funds
from langchain.agents import AgentExecutor, create_tool_calling_agent
from constants.prompts.system_prompt import system_prompt
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationTokenBufferMemory

# langchain.debug = True
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
load_dotenv()
memory = ConversationTokenBufferMemory(
    llm=llm,
    max_token_limit=2048,
    return_messages=True,
    memory_key="chat_history",
)

tools = [neo4j_query, mongodb_analytical_query, find_similar_funds]
agent = create_tool_calling_agent(llm, tools, system_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, memory=memory)
if __name__ == "__main__":
    print("Agent is ready. Type your queries below (type 'exit' or 'quit' to stop).")
    print("-" * 50)
    while True:
        user_question = input("\nWRITE YOUR USER QUERY ? ").strip()

        if user_question.lower() in ["exit", "quit"]:
            print("Exiting... Goodbye")
            break
        response = agent_executor.invoke({"input": user_question})
        print("-" * 50)
        print("Agent execution finished.")
        print("\nFinal Answer:")
        print(response["output"])
