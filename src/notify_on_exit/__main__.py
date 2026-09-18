"""Allow ``python -m notify_on_exit -- <command>``."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
