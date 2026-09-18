from __future__ import annotations

import json
from unittest import mock

from notify_on_exit.notifier import DingTalkNotifier


class _FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *exc_info) -> bool:
        return False


def test_send_posts_markdown_payload():
    captured = {}

    def fake_urlopen(request, timeout=None):
        captured["url"] = request.full_url
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return _FakeResponse(b'{"errcode":0}')

    with mock.patch("urllib.request.urlopen", fake_urlopen):
        result = DingTalkNotifier(timeout=3).send(
            "https://example.invalid/hook", "[\u6210\u529f] \u547d\u4ee4\u5df2\u7ed3\u675f", "\u8017\u65f6 1.0 \u79d2"
        )

    assert captured["url"] == "https://example.invalid/hook"
    assert captured["body"]["msgtype"] == "markdown"
    markdown = captured["body"]["markdown"]
    assert markdown["title"] == "[\u6210\u529f] \u547d\u4ee4\u5df2\u7ed3\u675f"
    assert "[\u6210\u529f]" in markdown["text"]
    assert "\u8017\u65f6 1.0 \u79d2" in markdown["text"]
    assert captured["timeout"] == 3
    assert result == '{"errcode":0}'


def test_default_timeout_is_positive():
    assert DingTalkNotifier().timeout > 0
