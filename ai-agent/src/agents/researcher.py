from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from src.config.llm import LLMConfig
from src.tools import TOOLS


RESEARCHER_PROMPT = """You are a Research Specialist in a software development team.

Your responsibilities:
- Gather information from the web when needed
- Analyze codebases and documentation
- Find best practices, patterns, and solutions
- Provide clear, concise research summaries with sources

Use the web_search tool when you need external information."""


def researcher_node(state) -> dict:
    llm = LLMConfig.get_llm()
    bound = llm.bind_tools(TOOLS)
    msgs = [SystemMessage(content=RESEARCHER_PROMPT), *state["messages"]]
    ai_msg = bound.invoke(msgs)

    result = {"messages": [ai_msg]}

    if hasattr(ai_msg, "content") and ai_msg.content:
        result["research_notes"] = ai_msg.content

    return result
