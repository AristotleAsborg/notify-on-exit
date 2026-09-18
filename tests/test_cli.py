from __future__ import annotations

import sys

from notify_on_exit import cli

WEBHOOK_ENV = {"DINGTALK_WEBHOOK": "https://example.invalid/robot/send?access_token=test-token"}
SUCCESS_TITLE_PREFIX = cli.SUCCESS_TITLE_PREFIX
FAILURE_TITLE_PREFIX = cli.FAILURE_TITLE_PREFIX


class _Collector:
    """Stub notifier: records sends instead of touching the network."""

    def __init__(self) -> None:
        self.sent: list[tuple[str, str, str]] = []

    def send(self, webhook_url: str, title: str, text: str) -> None:
        self.sent.append((webhook_url, title, text))


def _collector() -> tuple[list, _Collector]:
    collector = _Collector()
    return collector.sent, collector


def test_module_imports_and_exposes_prefixes():
    assert SUCCESS_TITLE_PREFIX != FAILURE_TITLE_PREFIX
    assert callable(cli.main)


def test_main_notifies_success():
    sent, notifier = _collector()
    code = cli.main(
        ["--", sys.executable, "-c", "print('done')"],
        notifier=notifier,
        env=WEBHOOK_ENV,
    )
    assert code == 0
    assert len(sent) == 1
    url, title, text = sent[0]
    assert url == WEBHOOK_ENV["DINGTALK_WEBHOOK"]
    assert title.startswith(SUCCESS_TITLE_PREFIX)
    assert "done" not in text


def test_main_notifies_failure_with_stderr_tail():
    sent, notifier = _collector()
    script = "import sys; sys.stderr.write('boom-line\\n'); sys.exit(3)"
    code = cli.main(["--", sys.executable, "-c", script], notifier=notifier, env=WEBHOOK_ENV)
    assert code == 3
    assert len(sent) == 1
    _, title, text = sent[0]
    assert title.startswith(FAILURE_TITLE_PREFIX)
    assert not title.startswith(SUCCESS_TITLE_PREFIX)
    assert "boom-line" in text


def test_main_missing_webhook_does_not_notify():
    sent, notifier = _collector()
    code = cli.main(["--", sys.executable, "-c", "pass"], notifier=notifier, env={})
    assert code == 2
    assert sent == []


def test_main_without_command_returns_usage_error():
    sent, notifier = _collector()
    code = cli.main([], notifier=notifier, env=WEBHOOK_ENV)
    assert code == 2
    assert sent == []


def test_main_survives_notifier_failure():
    class _Boom:
        def send(self, webhook_url, title, text):
            raise RuntimeError("network down")

    code = cli.main(["--", sys.executable, "-c", "pass"], notifier=_Boom(), env=WEBHOOK_ENV)
    assert code == 0


def test_build_message_success_omits_stderr():
    title, text = cli.build_message(0, "secret-stderr", 1.25)
    assert title.startswith(SUCCESS_TITLE_PREFIX)
    assert "secret-stderr" not in text


def test_build_message_failure_appends_stderr_tail():
    title, text = cli.build_message(1, "line-a\nline-b\n", 2.5)
    assert title.startswith(FAILURE_TITLE_PREFIX)
    assert "line-a" in text
    assert "line-b" in text


def test_tail_lines_boundaries():
    assert cli.tail_lines("a\n\nb\nc\nd\n", 2) == ["c", "d"]
    assert cli.tail_lines("", 5) == []
    assert cli.tail_lines("only", 0) == []
