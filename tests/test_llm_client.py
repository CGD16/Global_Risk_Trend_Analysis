from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.llm import client


@pytest.mark.parametrize(
    "choices",
    [
        [],
        [
            SimpleNamespace(
                finish_reason="length", message=SimpleNamespace(content="partial")
            )
        ],
        [SimpleNamespace(finish_reason="stop", message=SimpleNamespace(content=""))],
    ],
)
def test_rejects_missing_empty_or_truncated_response(monkeypatch, choices):
    fake = Mock()
    fake.chat.completions.create.return_value = SimpleNamespace(choices=choices)
    monkeypatch.setattr(client, "get_client", lambda: fake)
    with pytest.raises(client.InvalidModelOutput):
        client.complete("system", "prompt")


def test_completion_preserves_model_configuration(monkeypatch):
    fake = Mock()
    fake.chat.completions.create.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(
                finish_reason="stop", message=SimpleNamespace(content="Hello")
            )
        ],
        usage=SimpleNamespace(total_tokens=15),
    )
    monkeypatch.setattr(client, "get_client", lambda: fake)
    assert client.complete("system", "prompt") == ("Hello", 15)
    kwargs = fake.chat.completions.create.call_args.kwargs
    assert kwargs["model"] == client.MODEL
    assert kwargs["max_tokens"] == 512
    assert kwargs["extra_body"]["chat_template_kwargs"]["enable_thinking"] is False
