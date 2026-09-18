# notify-on-exit

Wrap a long-running command and get a DingTalk robot push on your phone the
moment the child process exits, so you can walk away from the screen.

## What it does

- Runs the wrapped command as a child process.
- Sends exactly one message through a DingTalk robot webhook when it exits.
- Success and failure use different title prefixes (`[成功]` / `[失败]`).
- On failure, the tail of the child's stderr is appended to the message body.

The push is triggered by the child process exiting, not by watching log files.
The numeric exit code is deliberately not part of the message body.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Configure

```bash
export DINGTALK_WEBHOOK="https://oapi.dingtalk.com/robot/send?access_token=..."
```

The webhook is read from the environment at run time; it is never hard-coded.

## Usage

```bash
notify-on-exit -- pytest -q
# or
python -m notify_on_exit -- make build
```

The wrapper exits with the child's exit code.

## Non-goals

- No self-built mobile app (no push certificates, no background keep-alive).
- No side-channel log-file monitoring.
- The raw exit code is not required in the message body.

## Development

```bash
python -m pytest -q
python -m ruff check .
python scripts/check_blacklist.py
```
