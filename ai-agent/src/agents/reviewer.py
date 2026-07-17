from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from src.config.llm import LLMConfig
from src.tools import TOOLS


REVIEWER_PROMPT = """You are a Code Reviewer in a software development team.

Your responsibilities:
- Review code for correctness, performance, and best practices
- Check for edge cases, bugs, and security issues
- Provide actionable, specific feedback
- Score the code 1-10

Format your output as:
SCORE: <1-10>
FEEDBACK: <your detailed feedback>

Be constructive and specific."""


def reviewer_node(state) -> dict:
    llm = LLMConfig.get_llm()
    bound = llm.bind_tools(TOOLS)
    msgs = [SystemMessage(content=REVIEWER_PROMPT), *state["messages"]]
    ai_msg = bound.invoke(msgs)

    content = getattr(ai_msg, "content", "") or ""

    score = 5
    feedback = content
    for line in content.split("\n"):
        if line.strip().upper().startswith("SCORE:"):
            try:
                score = int(line.split(":")[1].strip())
            except (ValueError, IndexError):
                pass
        if line.strip().upper().startswith("FEEDBACK:"):
            feedback = line.split(":", 1)[1].strip()

    return {
        "messages": [ai_msg],
        "review_score": score,
        "review_feedback": feedback,
    }
