# AI Multi-Agent System 🤖

A production-ready multi-agent system built with **LangGraph** that collaborates as a software development team. Agents share a typed state, use tools, and support multiple LLM providers.

## Architecture

```
START → Supervisor → {Researcher | Coder | Reviewer}
                           ↕ (if tool calls)
                         Tools
                           ↓
                        Finalize → END
```

The graph runs in a loop: the **Supervisor** routes tasks to specialists, specialists call tools when needed, and the cycle repeats until the task is complete.

## Agent Roles

| Agent | Role |
|---|---|
| **Supervisor** | Routes tasks to the right specialist via structured LLM output |
| **Researcher** | Gathers info via web search, analyzes codebases |
| **Coder** | Writes code, fixes bugs, validates with Python execution |
| **Reviewer** | Reviews code quality, scores 1-10, provides feedback |

## Tools

| Tool | Description |
|---|---|
| `web_search` | Search the web via DuckDuckGo API |
| `run_python_code` | Execute Python in a sandboxed subprocess |
| `read_file` | Read file contents |
| `write_file` | Write content to file |
| `list_directory` | List directory contents |

## Quick Start

### Prerequisites

- Python 3.10+
- An API key from one of the supported providers

### Installation

```bash
# Clone the repo
git clone <your-repo-url>
cd ai-agent

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API key
```

### Usage

```bash
# Run with a task
python -m src.main "Write a Python function to merge two sorted lists"

# Run with a specific thread (for state persistence)
python -m src.main --thread my-task "Research Python async patterns"
```

## Configuration

### LLM Providers

Set `LLM_PROVIDER` in `.env` to switch providers:

| Provider | Env Var | Example Model | URL |
|---|---|---|---|
| **GapGPT** (default) | `GAPGPT_API_KEY` | `gpt-4o`, `gemini-2.5-pro` | `https://api.gapgpt.app/v1` |
| AgentRouter | `AGENTROUTER_API_KEY` | `gpt-5.5`, `glm-5.2` | `https://agentrouter.org/v1` |
| OpenAI | `OPENAI_API_KEY` | `gpt-4o` | — |
| Anthropic | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514` | — |
| Ollama (local) | — | `llama3.2` | `http://localhost:11434` |

### Fast vs Main Model

- **Fast model** (`FAST_MODEL`): Used by the Supervisor for cheap routing decisions
- **Main model**: Used by specialist agents for research, coding, and review

This split saves cost and latency.

## Project Structure

```
ai-agent/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point, graph wiring, CLI
│   ├── state.py             # TypedDict shared state with reducers
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── supervisor.py    # LLM router + rule-based fallback
│   │   ├── researcher.py    # Research specialist agent
│   │   ├── coder.py         # Coding specialist agent
│   │   └── reviewer.py      # Code review specialist agent
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── web_search.py    # Web search tool
│   │   ├── code_executor.py # Python sandbox tool
│   │   └── file_ops.py      # File read/write/list tools
│   └── config/
│       └── llm.py           # Multi-provider LLM configuration
├── .env.example             # Environment template
├── .gitignore
├── requirements.txt
└── README.md
```

## How It Works

### Shared State

All agents communicate through a single `TeamState` dictionary. Each field uses a **reducer** to control merging:

```python
class TeamState(TypedDict):
    messages: Annotated[list, add_messages]   # Append-only history
    research_notes: Annotated[str, replace_value]  # Latest wins
    code: Annotated[str, replace_value]
    review_feedback: Annotated[str, replace_value]
    review_score: Annotated[int, replace_value]
    final_output: Annotated[str, replace_value]
    iteration_count: Annotated[int, increment]  # Accumulates
    max_iterations: int
```

### Graph Execution

1. **Supervisor** receives all messages and decides the next specialist
2. **Specialist** (researcher/coder/reviewer) processes the task, optionally calling tools
3. **Tool node** executes any tool calls the agent made
4. Back to **Supervisor** for re-routing
5. Loop continues until the supervisor picks `finalize` or iteration limit is hit
6. **Finalize** compiles all work into a cohesive output

## Adding a New Provider

Edit `src/config/llm.py` and add an entry to `_providers`:

```python
PROVIDER_MYPROVIDER = "myprovider"
_providers = {
    ...
    PROVIDER_MYPROVIDER: {
        "model": os.getenv("MYPROVIDER_MODEL", "default-model"),
        "model_provider": "openai",  # or "anthropic"
        "api_key": os.getenv("MYPROVIDER_API_KEY"),
        "base_url": os.getenv("MYPROVIDER_BASE_URL", "https://api.example.com/v1"),
        "temperature": 0.7,
    },
}
```

Then set `LLM_PROVIDER=myprovider` in `.env`.

## License

MIT
