"""Conversation history — DES-003, REQ-010, REQ-021."""

from __future__ import annotations

import json
from typing import Any


class ConversationHistory:
    def __init__(self, system_prompt: str, max_tokens: int = 8000) -> None:
        self._system = {"role": "system", "content": system_prompt}
        self._history: list[dict[str, Any]] = []
        self._max_tokens = max_tokens

    def add_user(self, content: str) -> None:
        self._history.append({"role": "user", "content": content})
        self._truncate()

    def add_assistant(self, content: str | None, tool_calls: list | None = None) -> None:
        msg: dict[str, Any] = {"role": "assistant", "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        self._history.append(msg)
        self._truncate()

    def add_tool_result(self, tool_call_id: str, content: str) -> None:
        self._history.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": content,
            }
        )
        self._truncate()

    def messages(self) -> list[dict[str, Any]]:
        return [self._system, *self._history]

    def clear(self) -> None:
        self._history.clear()

    def _truncate(self) -> None:
        while self._history and self._token_estimate() > self._max_tokens:
            self._history.pop(0)

    def _token_estimate(self) -> int:
        return len(json.dumps(self.messages())) // 4
