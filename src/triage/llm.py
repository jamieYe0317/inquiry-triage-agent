"""One thin wrapper around the Anthropic SDK: structured output, token and cost log.

The key comes from the ANTHROPIC_API_KEY environment variable (or Streamlit secrets, which the
app copies into the environment). This module never stores or prints the key.
"""

from __future__ import annotations

import os
import time
from typing import TypeVar

from pydantic import BaseModel

DEFAULT_MODEL = os.environ.get("TRIAGE_MODEL", "claude-haiku-5-5")

# USD per million tokens (input, output), prompts up to 100K tokens.
# Source: Anthropic model table cached 2026-10-06. Check the live pricing page before you rely on it.
PRICES: dict[str, tuple[float, float]] = {
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-opus-5-5": (4.00, 20.00),
}

T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    pass


def has_api_key() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    pin, pout = PRICES.get(model, (0.0, 0.0))
    return (input_tokens * pin + output_tokens * pout) / 1_000_000


class LLM:
    def __init__(self, model: str = DEFAULT_MODEL, effort: str = "low", max_tokens: int = 4000):
        import anthropic  # imported here so offline tests never need the SDK configured

        if not has_api_key():
            raise LLMError("ANTHROPIC_API_KEY is not set. Live LLM mode needs a key.")
        self._anthropic = anthropic
        self.client = anthropic.Anthropic(max_retries=2, timeout=60.0)
        self.model = model
        self.effort = effort
        self.max_tokens = max_tokens

    def parse(self, system: str, user: str, schema: type[T]) -> tuple[T, dict]:
        a = self._anthropic
        t0 = time.perf_counter()
        kwargs = dict(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_format=schema,
        )
        try:
            try:
                resp = self.client.messages.parse(**kwargs, output_config={"effort": self.effort})
            except TypeError:
                # Older SDKs may not accept output_config next to output_format.
                resp = self.client.messages.parse(**kwargs)
        except a.RateLimitError as e:
            raise LLMError(f"rate limited: {e}") from e
        except a.APIStatusError as e:
            raise LLMError(f"API error {e.status_code}: {e.message}") from e
        except a.APIConnectionError as e:
            raise LLMError(f"connection error: {e}") from e
        if resp.stop_reason == "refusal":
            raise LLMError("the model declined this request")
        if resp.stop_reason == "max_tokens":
            raise LLMError("the response hit max_tokens before it finished")
        parsed = resp.parsed_output
        if parsed is None:
            raise LLMError("the response did not match the schema")
        u = resp.usage
        usage = {
            "model": self.model,
            "input_tokens": u.input_tokens,
            "output_tokens": u.output_tokens,
            "cost_usd": cost_usd(self.model, u.input_tokens, u.output_tokens),
            "seconds": round(time.perf_counter() - t0, 3),
        }
        return parsed, usage
