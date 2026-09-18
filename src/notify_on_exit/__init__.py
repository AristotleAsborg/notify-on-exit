"""notify-on-exit: run a long command, get a phone push when it exits."""

from .cli import (
    FAILURE_TITLE_PREFIX,
    SUCCESS_TITLE_PREFIX,
    build_message,
    main,
)
from .notifier import DingTalkNotifier

__all__ = [
    "DingTalkNotifier",
    "FAILURE_TITLE_PREFIX",
    "SUCCESS_TITLE_PREFIX",
    "build_message",
    "main",
]

__version__ = "0.1.0"
