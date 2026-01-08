from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import AzureChatOpenAI

from gxmd.config import PARSE_MANGA_INFO_TEMPLATE, PARSE_CHAPTER_IMAGES_TEMPLATE


def get_template(purpose: str) -> str:
    return PARSE_MANGA_INFO_TEMPLATE if purpose == 'manga_info' else PARSE_CHAPTER_IMAGES_TEMPLATE


class CodeGeneratorService:
    def __init__(self):
        llm = AzureChatOpenAI(deployment_name="gpt-5.2-chat")
        self.system_message = SystemMessage(
            "You're an expert Python developer specializing in high-performance web scraping using the `selectolax` library, Produce correct, ready-to-run code in Python directly without further info, if you cannot provide a solution for any reason, respond with 'No'.")
        self.chain = llm | StrOutputParser()

    async def generate_manga_code(self, purpose: str, html: str, url: str):
        template = get_template(purpose)
        with open(template, 'r') as f:
            template_content = f.read()
            populated_template = template_content.replace("{link}", url).replace("{html}", html)
            return await self._invoke(populated_template)

    async def _invoke(self, message: str) -> str:
        messages = [self.system_message,
                    HumanMessage(message)]
        code: str = await self.chain.ainvoke(messages)

        return code.strip().lstrip('```python').rstrip('```').strip()


# Global instance
code_generator = CodeGeneratorService()
