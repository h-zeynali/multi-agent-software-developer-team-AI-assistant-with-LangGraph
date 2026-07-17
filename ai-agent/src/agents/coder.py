from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from src.config.llm import LLMConfig
from src.tools import TOOLS


CODER_PROMPT = """You are a Coder in a software development team.

Your responsibilities:
- Write clean, correct, well-structured code
- Fix bugs and debug issues
- Implement features based on requirements
- Use run_python_code to validate your code
- Read existing files to understand the codebase before making changes
- Write files to apply your changes

Always validate your code with run_python_code before considering it done."""


def coder_node(state) -> dict:
    llm = LLMConfig.get_llm()
    bound = llm.bind_tools(TOOLS)
    msgs = [SystemMessage(content=CODER_PROMPT), *state["messages"]]
    ai_msg = bound.invoke(msgs)

    result = {"messages": [ai_msg]}

    if hasattr(ai_msg, "content") and ai_msg.content:
        result["code"] = ai_msg.content

    return result
