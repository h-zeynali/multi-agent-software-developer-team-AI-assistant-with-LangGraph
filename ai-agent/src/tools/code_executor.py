import subprocess
import tempfile
from pathlib import Path

from langchain_core.tools import tool


@tool
def run_python_code(code: str) -> str:
    """Execute Python code in a sandboxed subprocess and return stdout/stderr."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        fpath = f.name
    try:
        result = subprocess.run(
            ["python", fpath],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = ""
        if result.stdout:
            output += f"stdout:\n{result.stdout}\n"
        if result.stderr:
            output += f"stderr:\n{result.stderr}\n"
        if not output:
            output = "(no output)"
        return output
    except subprocess.TimeoutExpired:
        return "Execution timed out after 30 seconds"
    except Exception as e:
        return f"Execution error: {e}"
    finally:
        Path(fpath).unlink(missing_ok=True)
