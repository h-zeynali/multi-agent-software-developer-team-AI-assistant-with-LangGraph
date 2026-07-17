from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """Search the web for information on the given query. Returns relevant snippets and URLs."""
    import json
    import re
    import urllib.parse

    import requests

    try:
        encoded = urllib.parse.quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        data = response.json()

        parts = []
        abstract = data.get("AbstractText", "")
        if abstract:
            parts.append(f"Summary: {abstract[:500]}")

        source = data.get("AbstractSource", "")
        src_url = data.get("AbstractURL", "")
        if src_url:
            parts.append(f"Source: {source} - {src_url}")

        related = data.get("RelatedTopics", [])
        if related:
            if not parts:
                parts.append(f"Results for: {query}")
            for item in related[:8]:
                if isinstance(item, dict):
                    text = item.get("Text", "")
                    first_url = item.get("FirstURL", "")
                    if text:
                        parts.append(f"  - {text[:200]}")
                        if first_url:
                            parts.append(f"    {first_url}")

        if parts:
            return "\n".join(parts)[:4000]

        # Fallback: scrape using textise dot iitty
        fallback_url = f"https://textise.iitty.com/show?url={encoded}"
        try:
            fb = requests.get(fallback_url, timeout=5)
            text = fb.text
            snippets = re.findall(r"(?:https?://[^\s<>'\"\[\]]+)", text)
            unique = list(dict.fromkeys(snippets))
            if unique:
                result = f"Results for '{query}':\n"
                for u in unique[:10]:
                    result += f"\n- {u}"
                return result[:4000]
        except Exception:
            pass

        return f"No results found for '{query}'."

    except Exception as e:
        return f"Search failed: {e}"
