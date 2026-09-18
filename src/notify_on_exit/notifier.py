"""Send a message to a DingTalk robot webhook."""

from __future__ import annotations

import json
import urllib.request

TIMEOUT_SECONDS = 10.0
WEBHOOK_CONTENT_TYPE = "application/json"


class DingTalkNotifier:
    """Minimal DingTalk robot client: one webhook, one markdown message."""

    def __init__(self, timeout: float = TIMEOUT_SECONDS) -> None:
        self.timeout = timeout

    def send(self, webhook_url: str, title: str, text: str) -> str:
        """POST a markdown message to ``webhook_url`` and return the raw reply."""
        payload = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": f"### {title}\n\n{text}"},
        }
        request = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": WEBHOOK_CONTENT_TYPE},
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            return response.read().decode("utf-8")
