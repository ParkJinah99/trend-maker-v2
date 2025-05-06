import os
import json
from dotenv import load_dotenv
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from backend.tools import SerpAPIAdsTool

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

llm = ChatOpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
search_tool = SerpAPIAdsTool()
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

conversation_prompt = PromptTemplate(
    input_variables=["user_input"],
    template="""
You are a helpful assistant designed to guide a user in forming a well-defined marketing ad search.
Your job is to ask clarifying questions and collect key parameters:
- advertiser_id or text (required)
- region, political_ads, platform, creative_format, start_date, end_date (optional)

Don't do any searches yourself. Once the user has provided enough details, summarize the final parameters
as: search_parameters: {{ "advertiser_id": "...", "region": "...", ... }}

User said: {user_input}
"""
)

conversation_agent_chain = LLMChain(
    llm=llm,
    prompt=conversation_prompt,
    memory=memory
)

search_agent = initialize_agent(
    tools=[Tool(name=search_tool.name, func=search_tool.run, description=search_tool.description)],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    memory=ConversationBufferMemory(memory_key="search_memory", return_messages=True),
    verbose=True
)

def run_multi_agent(user_input: str) -> str:
    response = conversation_agent_chain.run({"user_input": user_input})

    if "search_parameters:" in response:
        try:
            json_str = response.split("search_parameters:")[-1].strip()
            json_data = json.loads(json_str)
            result = search_agent.run(json.dumps(json_data))
            return f"\n📦 Search Summary:\n{result}"
        except Exception as e:
            return f"⚠️ Error running search: {str(e)}"

    return response
