# Global llm instance
from langchain_core.messages import SystemMessage
from langchain_openai import AzureChatOpenAI

DEFAULT_SYSTEM_MESSAGE = SystemMessage(
    "You're a helpful proficient Python programming assistant, Produce correct, ready-to-run code in Python directly without further info, if you cannot provide a solution for any reason, respond with 'No'.")

llm = AzureChatOpenAI(deployment_name="gpt-5.2-chat")
