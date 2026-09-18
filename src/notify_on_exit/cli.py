"""Wrap a long command and push a DingTalk message when it finishes."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from typing import Sequence

from .notifier import DingTalkNotifier

WEBHOOK_ENV_VAR = "DINGTALK_WEBHOOK"
SUCCESS_TITLE_PREFIX = "[\u6210\u529f]"
FAILURE_TITLE_PREFIX = "[\u5931\u8d25]"
STDERR_TAIL_LINES = 10

USAGE = "usage: notify-on-exit -- <command> [args...]"


def parse_argv(argv: Sequence[str]) -> list[str] | None:
    """Return the wrapped command, or ``None`` when nothing was given."""
    if not argv:
        return None
    command = list(argv[1:]) if argv[0] == "--" else list(argv)
    return command or None


def run_command(command: Sequence[str]) -> tuple[int, str, str, float]:
    """Run ``command`` as a child process and report how it ended."""
    started = time.monotonic()
    proc = subprocess.run(command, capture_output=True, text=True, errors="replace")
    elapsed = time.monotonic() - started
    return proc.returncode, proc.stdout, proc.stderr, elapsed


def tail_lines(text: str, count: int) -> list[str]:
    """Return the last ``count`` non-blank lines of ``text``."""
    if count <= 0:
        return []
    lines = [line for line in text.splitlines() if line.strip()]
    return lines[-count:]


def build_message(returncode: int, stderr: str, elapsed: float) -> tuple[str, str]:
    """Build ``(title, body)``; success and failure use different prefixes.

    The wrapped command and the child's stdout are intentionally not echoed into
    the message body: only the outcome, the duration and (on failure) the tail of
    stderr end up in the push.
    """
    if returncode == 0:
        title = f"{SUCCESS_TITLE_PREFIX} \u547d\u4ee4\u5df2\u7ed3\u675f"
        body = [f"\u8017\u65f6 {elapsed:.1f} \u79d2", "\u5b50\u8fdb\u7a0b\u6b63\u5e38\u9000\u51fa\u3002"]
        return title, "\n".join(body)

    title = f"{FAILURE_TITLE_PREFIX} \u547d\u4ee4\u5df2\u7ed3\u675f"
    body = [f"\u8017\u65f6 {elapsed:.1f} \u79d2", "\u5b50\u8fdb\u7a0b\u5f02\u5e38\u9000\u51fa\u3002"]
    tail = tail_lines(stderr, STDERR_TAIL_LINES)
    if tail:
        body.append("stderr \u672b\u5c3e\uff1a")
        body.extend(tail)
    return title, "\n".join(body)


def main(argv=None, notifier=None, env=None) -> int:
    """Run the wrapped command, then push a DingTalk notification."""
    if argv is None:
        argv = sys.argv[1:]
    if env is None:
        env = os.environ

    command = parse_argv(argv)
    if command is None:
        print(USAGE, file=sys.stderr)
        return 2

    webhook_url = env.get(WEBHOOK_ENV_VAR, "")
    if not webhook_url:
        print(f"{WEBHOOK_ENV_VAR} is not set; cannot push a notification.", file=sys.stderr)
        return 2

    if notifier is None:
        notifier = DingTalkNotifier()

    returncode, stdout, stderr, elapsed = run_command(command)
    if stdout:
        sys.stdout.write(stdout)
    if stderr:
        sys.stderr.write(stderr)

    title, body = build_message(returncode, stderr, elapsed)
    try:
        notifier.send(webhook_url, title, body)
    except Exception as exc:  # pragma: no cover - depends on the network
        print(f"warning: notification failed: {exc}", file=sys.stderr)

    return returncode
