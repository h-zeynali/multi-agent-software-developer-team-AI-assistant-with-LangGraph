from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


def replace_value(left, right):
    return right


def increment(left, right):
    return (left or 0) + (right or 0)


class TeamState(TypedDict):
    messages: Annotated[list, add_messages]
    task: str
    research_notes: Annotated[str, replace_value]
    code: Annotated[str, replace_value]
    review_feedback: Annotated[str, replace_value]
    review_score: Annotated[int, replace_value]
    final_output: Annotated[str, replace_value]
    iteration_count: Annotated[int, increment]
    max_iterations: int
