# AI Multi-Agent System

A LangGraph-based multi-agent software development team with shared state, tool use, and multi-provider LLM support.

## Architecture

```
START → Supervisor → {Researcher | Coder | Reviewer}
                           ↓
                 (if tool call) → Tools → Supervisor
                           ↓
                        END (finalize)
```

## Agents

| Agent | Role |
|---|---|
| **Supervisor** | Routes tasks to the right specialist |
| **Researcher** | Gathers info, searches web, analyzes codebases |
| **Coder** | Writes code, fixes bugs, implements features |
| **Reviewer** | Reviews code quality, scores 1-10, gives feedback |

## Tools

- `web_search` — Search the web for information
- `run_python_code` — Execute Python code in a sandboxed subprocess
- `read_file` / `write_file` / `list_directory` — File operations

## Setup

```bash
cd ai-agent
cp .env.example .env
# Edit .env with your API keys
pip install -r requirements.txt
```

## Usage

```bash
python -m src.main "Write a Python function to merge two sorted lists"
```

With a specific thread ID (for state persistence/resume):

```bash
python -m src.main --thread my-task "Research Python async patterns"
```

## LLM Providers

Set `LLM_PROVIDER` to one of: `openai`, `anthropic`, `ollama`.

The supervisor uses a fast/cheap model (`FAST_MODEL`), while specialist agents use the main model.

## Project Structure

```
ai-agent/
├── src/
│   ├── main.py              # Entry point, graph wiring, CLI
│   ├── state.py             # Shared state (TypedDict)
│   ├── agents/
│   │   ├── supervisor.py    # Task router
│   │   ├── researcher.py    # Research agent
│   │   ├── coder.py         # Coding agent
│   │   └── reviewer.py      # Review agent
│   ├── tools/
│   │   ├── web_search.py    # Web search tool
│   │   ├── code_executor.py # Python sandbox tool
│   │   └── file_ops.py      # File read/write tools
│   └── config/
│       └── llm.py           # Multi-provider LLM config
├── requirements.txt
├── .env.example
└── README.md
```
