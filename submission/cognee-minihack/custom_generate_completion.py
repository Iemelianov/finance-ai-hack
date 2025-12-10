from typing import Optional, Type, Any
import os
from openai import AsyncOpenAI
import logging
from cognee.infrastructure.llm.prompts import read_query_prompt


async def generate_structured_completion_with_user_prompt(
    user_prompt: str,
    system_prompt_path: str,
    system_prompt: Optional[str] = None,
    conversation_history: Optional[str] = None,
    response_model: Type = str,
) -> Any:
    """Generates a structured completion using LLM with given context and prompts."""
    system_prompt = system_prompt if system_prompt else read_query_prompt(system_prompt_path)

    if conversation_history:
        #:TODO: I would separate the history and put it into the system prompt but we have to test what works best with longer convos
        system_prompt = conversation_history + "\nTASK:" + system_prompt

    # Bypass structured-output enforcement and call Ollama/OpenAI-compatible endpoint directly.
    client = AsyncOpenAI(
        base_url=os.environ.get("LLM_ENDPOINT", "http://localhost:11434/v1"),
        api_key=os.environ.get("LLM_API_KEY", "ollama"),
    )
    model_name = os.environ.get("LLM_MODEL", "cognee-distillabs-model-gguf-quantized")

    logging.getLogger(__name__).debug(
        "generate_structured_completion_with_user_prompt model=%s endpoint=%s user_prompt_len=%d system_prompt_len=%d",
        model_name,
        client.base_url,
        len(user_prompt or ""),
        len(system_prompt or ""),
    )

    resp = await client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return resp.choices[0].message.content if resp.choices else ""


async def generate_completion_with_user_prompt(
    user_prompt: str,
    system_prompt_path: str,
    system_prompt: Optional[str] = None,
    conversation_history: Optional[str] = None,
) -> str:
    """Generates a completion using LLM with given context and prompts."""
    return await generate_structured_completion_with_user_prompt(
        user_prompt=user_prompt,
        system_prompt_path=system_prompt_path,
        system_prompt=system_prompt,
        conversation_history=conversation_history,
        response_model=str,
    )
