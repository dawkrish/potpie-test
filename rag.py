import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langchain.agents import Tool

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

model = ChatAnthropic(model="claude-3-5-sonnet-20240620")
parser = StrOutputParser()
system_template = "Translate the following into {language}:"
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)

chain = model | parser

dummy_tool = Tool(
    name="dummy_tool",
    func=lambda x: "This is a dummy response to: " + x,
    description="A simple dummy tool that returns a static response"
)

agent = create_react_agent(chain, tools=[])


def respond_to_hi():
    # Invoke the agent with the message "Hi, how are you?"
    response = agent.invoke(HumanMessage("HIHIHIHI"))
    # Return the response messages
    return response["messages"]

# # Example use of the function
# if __name__ == "__main__":
#     response = respond_to_hi()
#     print(response)
