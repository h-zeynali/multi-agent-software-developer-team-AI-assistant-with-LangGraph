from __future__ import annotations

import os

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from src.config.llm import LLMConfig


class RouteDecision(BaseModel):
    next: str = Field(description="One of: researcher, coder, reviewer, finalize")


SUPERVISOR_PROMPT = """You are a Supervisor in a software development team.
Your job is to route tasks to the right specialist agent.

Routing rules:
- If the task needs information gathering, research, or learning → route to `researcher`
- If the task needs coding, implementation, debugging, or fixing → route to `coder`
- If the task needs code review, quality assessment, or testing → route to `reviewer`
- If the work is complete and ready for final output → route to `finalize`

Respond with ONLY the agent name."""


def supervisor_node(state) -> dict:
    fast_llm = LLMConfig.get_fast_llm()
    schema_llm = fast_llm.with_structured_output(RouteDecision)

    guidance = (
        "Decide the next specialist. "
        "If the task needs research or information → researcher. "
        "If the task needs code or implementation → coder. "
        "If the task needs review or quality check → reviewer. "
        "If all work is finished → finalize."
    )

    decision = schema_llm.invoke([
        SystemMessage(content=guidance),
        *state["messages"],
    ])

    return {"messages": [HumanMessage(content=f"[Supervisor] Routing to: {decision.next}")]}


def supervisor_router(state) -> str:
    """Rule-based fallback router if LLM output can't be parsed."""
    if not state.get("messages"):
        return "researcher"
    last = state["messages"][-1]
    text = (getattr(last, "content", "") or "").lower()

    if any(k in text for k in ["finalize", "final", "done", "complete"]):
        return "finalize"
    if any(k in text for k in ["code", "implement", "write", "fix", "debug", "function"]):
        return "coder"
    if any(k in text for k in ["review", "check", "test", "quality"]):
        return "reviewer"
    if any(k in text for k in ["search", "find", "research", "learn", "what is"]):
        return "researcher"

    return "researcher"
