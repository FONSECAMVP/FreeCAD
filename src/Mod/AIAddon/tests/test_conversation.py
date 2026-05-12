"""
Tests for conversation history — REQ-010, REQ-021.
"""

import pytest

pytestmark = pytest.mark.fast

SYSTEM_PROMPT = "You are a FreeCAD assistant."


@pytest.fixture()
def history():
    from freecad_ai.conversation import ConversationHistory

    return ConversationHistory(system_prompt=SYSTEM_PROMPT, max_tokens=200)


def test_initial_history_has_system_message(history):
    msgs = history.messages()
    assert msgs[0]["role"] == "system"
    assert msgs[0]["content"] == SYSTEM_PROMPT


def test_add_user_message(history):
    history.add_user("make a box")
    msgs = history.messages()
    assert msgs[-1] == {"role": "user", "content": "make a box"}


def test_add_assistant_message(history):
    history.add_assistant("Sure, creating box.", tool_calls=None)
    msgs = history.messages()
    assert msgs[-1]["role"] == "assistant"


def test_add_tool_result(history):
    history.add_tool_result(tool_call_id="tc1", content='{"label":"Box"}')
    msgs = history.messages()
    assert msgs[-1]["role"] == "tool"
    assert msgs[-1]["tool_call_id"] == "tc1"


# REQ-021: truncation keeps system message, drops oldest non-system
def test_truncation_keeps_system_message(history):
    # Fill history beyond max_tokens with user messages
    for i in range(50):
        history.add_user(f"message {i} " * 10)
    msgs = history.messages()
    assert msgs[0]["role"] == "system"


def test_truncation_respects_max_tokens(history):
    import json

    for i in range(50):
        history.add_user(f"message {i} " * 10)
    msgs = history.messages()
    token_estimate = len(json.dumps(msgs)) // 4
    assert token_estimate <= 200


def test_clear_resets_to_system_only(history):
    history.add_user("make a box")
    history.clear()
    msgs = history.messages()
    assert len(msgs) == 1
    assert msgs[0]["role"] == "system"
