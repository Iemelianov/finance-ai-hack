
from typing import Dict, Any
import json
import sys
import logging
from pathlib import Path

# Try to import the Cognee completion helper from cognee-minihack/solution_q_and_a.py
_cognee_completion = None
_root = Path(__file__).resolve().parent.parent
_mini = _root / "cognee-minihack"
if _mini.exists():
    sys.path.append(str(_mini))
    try:
        from solution_q_and_a import completion as _cognee_completion  # type: ignore
    except Exception as exc:  # log import issues explicitly
        logging.getLogger(__name__).warning(
            "Failed to import completion from solution_q_and_a: %s", exc
        )
        _cognee_completion = None
else:
    logging.getLogger(__name__).warning("cognee-minihack folder not found at %s", _mini)

logger = logging.getLogger(__name__)


def _truncate(text: str, max_len: int = 400) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + "...[truncated]"


def ask_cognee_raw(prompt: str) -> str:
    """Send a natural-language prompt to Cognee and get back a string.

    This MUST call the local Cognee + distil SLM backend (no online LLMs).
    Replace the body once you know the correct function name/signature from solution_q_and_a.py.
    """
    logger.debug("ask_cognee_raw prompt len=%d preview=%s", len(prompt or ""), _truncate(prompt or ""))
    if _cognee_completion is None:
        # Safe fallback so the app can still import before wiring Cognee.
        return json.dumps(
            {
                "error": "Cognee completion function not wired. "
                         "Update core.cognee_client.ask_cognee_raw to call solution_q_and_a."
            }
        )
    return _cognee_completion(prompt)  # type: ignore[call-arg]


def ask_cognee_json(prompt: str) -> Dict[str, Any]:
    """Ask Cognee and parse the result as JSON.

    - Calls ask_cognee_raw(prompt)
    - Tries to parse JSON
    - Strips simple Markdown fences if present
    """
    raw = ask_cognee_raw(prompt)
    if isinstance(raw, dict):
        return raw

    text = str(raw).strip()
    logger.debug("ask_cognee_json raw type=%s len=%d preview=%s", type(raw).__name__, len(text), _truncate(text))

    if text.startswith("```"):
        # Strip code fences and optional 'json'
        text = text.strip("`").strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()

    try:
        return json.loads(text)
    except Exception:
        logger.debug("ask_cognee_json primary parse failed; attempting substring parse")
        # Best-effort: try to extract the first JSON array/object substring
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except Exception as exc:
                logger.debug("ask_cognee_json array parse failed: %s", exc)
                pass
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except Exception as exc:
                logger.debug("ask_cognee_json object parse failed: %s", exc)
                pass

        return {
            "error": "Failed to parse Cognee response as JSON.",
            "raw_response": text,
        }
