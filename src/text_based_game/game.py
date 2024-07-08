"""A fun little text-based game."""

from typing import NoReturn

from rich.layout import Layout
from rich.live import Live
import trio
import trio.testing

DEBUG = False


async def game() -> NoReturn:
    """Run the game!"""
    with Live(refresh_per_second=10, screen=True) as live:
        try:
            content = Layout()
            health = Layout()
            main = Layout()
            main.split_row("Hello", "there")
            content.split_column(main, health)
            live.update(content)
        finally:
            await trio.sleep(2)


def main() -> NoReturn:  # pyright:ignore [reportReturnType]
    """Run the game, asynchronously."""
    clock = trio.testing.MockClock(100000) if DEBUG else None

    try:
        trio.run(game, clock=clock)
    except* (SystemExit, KeyboardInterrupt) as excgroup:
        for exc in excgroup.exceptions:
            raise SystemExit from exc


if __name__ == "__main__":
    main()
