from __future__ import annotations

import argparse
import json
import os
import sys

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from src.agents import (
    coder_node,
    researcher_node,
    reviewer_node,
    supervisor_node,
    supervisor_router,
)
from src.state import TeamState
from src.tools import TOOLS

MAX_ITERATIONS = 10


def has_tool_calls(state: TeamState) -> str:
    """Return 'tools' if the last message has tool calls, else 'supervisor'."""
    msgs = state.get("messages", [])
    if msgs:
        last = msgs[-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
    return "supervisor"


def finalize_node(state: TeamState) -> dict:
    from langchain_core.messages import HumanMessage, SystemMessage

    from src.config.llm import LLMConfig

    llm = LLMConfig.get_llm()
    parts = []
    if state.get("research_notes"):
        parts.append(f"## Research\n{state['research_notes']}")
    if state.get("code"):
        parts.append(f"## Code\n{state['code']}")
    if state.get("review_feedback"):
        parts.append(f"## Review\nScore: {state['review_score']}/10\n{state['review_feedback']}")

    content = "\n\n".join(parts) if parts else "No work was completed."
    prompt = [
        SystemMessage(
            content=(
                "You are the Team Lead. Compile the team's work into a clear, "
                "comprehensive final output. Include code, research findings, "
                "and review results."
            )
        ),
        HumanMessage(content=content),
    ]
    ai_msg = llm.invoke(prompt)
    return {"messages": [ai_msg], "final_output": ai_msg.content}


def iteration_router(state: TeamState) -> str:
    """Route based on iteration count to prevent infinite loops."""
    count = state.get("iteration_count", 0)
    max_iter = state.get("max_iterations", MAX_ITERATIONS)
    if count >= max_iter:
        return "finalize"
    return "continue"


def build_graph():
    graph = StateGraph(TeamState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("coder", coder_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "supervisor")

    def supervisor_next(state: TeamState) -> str:
        n = supervisor_router(state)
        # Cap iterations
        count = state.get("iteration_count", 0)
        max_iter = state.get("max_iterations", MAX_ITERATIONS)
        if n != "finalize" and count >= max_iter:
            return "finalize"
        return n

    graph.add_conditional_edges(
        "supervisor",
        supervisor_next,
        {
            "researcher": "researcher",
            "coder": "coder",
            "reviewer": "reviewer",
            "finalize": "finalize",
        },
    )

    for agent in ("researcher", "coder", "reviewer"):
        graph.add_conditional_edges(
            agent,
            has_tool_calls,
            {"tools": "tools", "supervisor": "supervisor"},
        )

    graph.add_edge("tools", "supervisor")
    graph.add_edge("finalize", END)

    checkpointer = MemorySaver()
    compiled = graph.compile(checkpointer=checkpointer)
    return compiled


def run_task(task: str, thread_id: str = "default"):
    app = build_graph()
    config = {"configurable": {"thread_id": thread_id}}

    initial = {
        "messages": [{"role": "user", "content": task}],
        "task": task,
        "research_notes": "",
        "code": "",
        "review_feedback": "",
        "review_score": 0,
        "final_output": "",
        "iteration_count": 0,
        "max_iterations": MAX_ITERATIONS,
    }

    for event in app.stream(initial, config=config, stream_mode="values"):
        msgs = event.get("messages", [])
        if msgs:
            last = msgs[-1]
            role = getattr(last, "type", "unknown")
            content = getattr(last, "content", "")
            if content:
                from langchain_core.messages import AIMessage

                if isinstance(last, AIMessage) and not last.tool_calls:
                    print(f"\n[{role.upper()}]\n{content[:500]}")

    final = list(app.get_state_history(config))
    if final:
        return final[0].values.get("final_output", "")
    return ""


def main():
    parser = argparse.ArgumentParser(description="AI Multi-Agent System")
    parser.add_argument("task", nargs="?", help="The task for the agents to complete")
    parser.add_argument("--thread", default="main", help="Thread ID for state persistence")
    args = parser.parse_args()

    task = args.task
    if not task:
        task = input("Enter task: ").strip()
    if not task:
        print("No task provided.")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Task: {task}")
    print(f"{'='*60}\n")

    result = run_task(task, thread_id=args.thread)

    if result:
        print(f"\n{'='*60}")
        print("FINAL OUTPUT")
        print(f"{'='*60}")
        print(result)


if __name__ == "__main__":
    main()
