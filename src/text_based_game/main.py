"""A fun little text-based game."""


# ruff: noqa: PLW0603

import functools
import logging
import os
import sys
from typing import Literal, NoReturn

import numpy as np
import readchar
import trio
from rich import traceback
from rich.live import Live
from rich.logging import RichHandler
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import track
from rich.prompt import Confirm, IntPrompt
from trio import Event, Lock, Path

DEBUG = False  # Speed up animations for debugging
if DEBUG:
    import trio.testing


def clear() -> None:
    """Clear the terminal."""
    print("\033c\033[3J")


def heartcount(hearts: int) -> str:
    """Return a string of hearts."""
    return "".join([heartcolor for _ in range(hearts)])


async def tprint(text: str, sleep_time: float = 0.08) -> None:
    """Print a string, typewriter style!"""
    for character in text:
        sys.stdout.write(character)
        sys.stdout.flush()
        await trio.sleep(sleep_time)


x: int
y: int
playerchar: Literal["▲", "◀", "▼", "▶", "◣", "◥", "◤", "◢"] = "▶"
ox: int
oy: int
px: int = 0
py: int = 0
nx: int = 0
ny: int = 0
screen: str
grid: np.ndarray[str, np.dtype]
smgrid: np.ndarray[str, np.dtype]
toggletrap: Literal[0]
num_rows: int
num_cols: int
heartcolor: str
watercolor: str
keycolor: str
keystring: str
heartstring: str
arr: np.ndarray
items: list[int] = [3, 0]
bgcolor = "\033[92m"
killthread: Event = Event()
game: Event = Event()
game.set()
width = 12
level: int


p = Path(os.path.realpath(__file__)).parent


log = logging.getLogger("game")


async def open_level(level_path: Path) -> None:
    """Open a level file."""
    global x
    global y
    global playerchar
    global ox
    global oy
    global screen
    global grid
    global toggletrap
    global num_rows
    global num_cols
    global heartcolor
    global watercolor
    global keycolor
    global keystring
    global heartstring
    global arr
    async with await level_path.open("r") as f:
        lines = await f.readlines()

    num_rows = len(lines)
    num_cols = max([len(line.strip()) for line in lines])
    lines = [line.strip().ljust(num_cols) for line in lines]
    arr = np.full((num_rows, num_cols), ".")
    for row in range(num_rows):
        for col in range(num_cols):
            arr[row][col] = lines[row][col]

    arr = np.char.replace(arr, ".", " ")

    heartcolor = "\033[91m♥\033[0m" + bgcolor
    arr = np.char.replace(arr, "♥", heartcolor)
    keycolor = "\033[93m╼\033[0m" + bgcolor
    arr = np.char.replace(arr, "╼", keycolor)
    watercolor = "\033[94m~\033[0m" + bgcolor
    arr = np.char.replace(arr, "~", watercolor)

    heartstring = ""
    keystring = ""

    x = 1
    y = 1

    playerchar = "▶"
    ox = 0
    oy = 0
    screen = ""
    grid = np.array(arr, dtype=str)
    toggletrap = 0


def keycount(keys: int) -> str:
    """Return a string of keys."""
    return "".join([keycolor for _ in range(keys)])


def scrprt(width: int) -> str:
    """Create the items bar."""
    return heartstring + " " * (((width) + 2) - (items[0] + items[1])) + keystring


async def cave_explore(lock: Lock) -> None:  # noqa: C901, PLR0912, PLR0915
    """Explore the cave."""
    global x
    global y
    global ox
    global oy
    global smgrid
    global keystring
    global heartstring
    global px
    global py
    global nx
    global ny
    global game
    global screen

    async with lock:
        heartstring = heartcount(items[0])
        keystring = keycount(items[1])
        screen = scrprt(px - abs(nx))

    while not killthread:
        if items[0] == 0:
            await tprint("You died!")
            sys.exit()
        if grid[y][x] == heartcolor:
            arr[y][x] = " "
            items[0] += 1
            heartstring = heartcount(items[0])
            screen = scrprt(px - abs(nx))
        elif grid[y][x] == keycolor:
            arr[y][x] = " "
            items[1] += 1
            keystring = keycount(items[1])
            screen = scrprt(px - abs(nx))
        elif grid[y][x] == "☰":
            arr[y][x] = " "
            await tprint("You found a note!\n")
            await tprint(
                """It reads:
    5/6/1926\n I found a river today near the Library. I think I will follow it tomorrow.
    """,  # noqa: E501
            )
            if await trio.to_thread.run_sync(
                Confirm.ask,
                "Do you find and follow the river?",
            ):
                clear()
                await tprint("You follow the river and find a deep cave.")
                await endroom()
        elif grid[y][x] == watercolor:
            game = Event()
            print()
            print()
            if await trio.to_thread.run_sync(
                Confirm.ask,
                "Follow the underground river?",
            ):
                clear()
                await tprint("You follow the river and find a deep cave.")
                await endroom()
            else:
                game.set()
        elif grid[y][x] == "∆":
            items[0] -= 1
            heartstring = heartcount(items[0])
            screen = scrprt(px - abs(nx))
        elif grid[y][x] == "⊡":
            if items[1] > 0:
                items[1] -= 1
                screen = scrprt(px - abs(nx))
                if level == 1:
                    await key(lock=lock)
                    game.set()
            if level == 2:  # noqa: PLR2004
                await end()

        screen = scrprt(px - abs(nx))
        if grid[y][x] not in {" ", heartcolor, keycolor, "∆"}:
            x = ox
            y = oy
            oy = 0
            ox = 0
        else:
            grid[y][x] = "\033[96m" + playerchar + "\033[0m" + bgcolor
            grid[oy][ox] = arr[oy][ox]
            screenstr = [bgcolor]
            nx = max(x - width, 0)
            ny = max(y - width, 0)
            px = min(x + width, num_cols)
            py = min(y + width, num_cols)
            screenstr.append("╔")
            screenstr.extend(["═" for _ in range(px - abs(nx))])
            screenstr.append("╗\n")
            smgrid = grid[ny:py, nx:px]
            for i in smgrid:
                screenstr.append("║")
                screenstr.extend(i)
                screenstr.append("║\n")
            screenstr.append("╚")
            screenstr.extend(["═" for _ in range(px - abs(nx))])
            screenstr.extend(("╝\n", screen, "\n"))
            clear()
            print("".join(screenstr))
        ox = x
        oy = y
        await trio.sleep(0.05)
    clear()
    killthread.set()


async def key(lock: Lock) -> None:
    """Use the key."""
    global game
    async with lock:
        game = Event()
        killthread.set()
    await print_live_panel(
        """Door Opened!

You find treasure behind the door.
What do you do?

1. Take the treasure.
2. Leave the treasure and continue looking for the city.""",
    )
    match await trio.to_thread.run_sync(
        functools.partial(IntPrompt.ask, "What do you do?", choices=["1", "2"]),
    ):
        case 1:
            clear()
            await tprint("It was a trap! You died!")
            sys.exit()
        case 2:
            await print_live_panel(
                """You are tired, do you continue looking for the city or leave?
1. Continue looking for the city.
2. Leave.""",
            )

            match await trio.to_thread.run_sync(
                functools.partial(IntPrompt.ask, "What do you do?", choices=["1", "2"]),
            ):
                case 1:
                    await endroom()

                case 2:
                    clear()
                    await tprint("You leave the cave and go home.")
                    await tprint("You Loose!")
                    sys.exit()


async def endroom() -> None:
    """Go to end room."""
    global killthread
    global level
    global x
    global y

    await open_level(p / "endcave.txt")

    game.set()
    killthread = Event()
    x = 1
    y = 1
    level = 2


async def control(lock: Lock) -> NoReturn:
    """Control the player."""
    global x
    global y
    global playerchar

    while True:
        log.debug("Control")
        while game:
            log.debug("on")
            rc = await trio.to_thread.run_sync(readchar.readchar)
            match rc:
                case "w":
                    async with lock:
                        y -= 1
                        playerchar = "▲"
                case "a":
                    async with lock:
                        x -= 1
                        playerchar = "◀"
                case "s":
                    async with lock:
                        y += 1
                        playerchar = "▼"
                case "d":
                    async with lock:
                        x += 1
                        playerchar = "▶"
                case "z":
                    async with lock:
                        x -= 1
                        y += 1
                        playerchar = "◣"
                case "e":
                    async with lock:
                        x += 1
                        y -= 1
                        playerchar = "◥"
                case "q":
                    async with lock:
                        x -= 1
                        y -= 1
                        playerchar = "◤"
                case "c":
                    async with lock:
                        x += 1
                        y += 1
                        playerchar = "◢"
                case _:
                    pass
            await trio.sleep(0.05)
        game.wait()


async def end() -> NoReturn:
    """End the game as a winner."""
    global killthread

    game.set()
    killthread = Event()
    await print_live_panel(
        """Cue cutscene!

You Win!
(To exit, press any key)""",
    )
    sys.exit()


async def run_game() -> None:
    """Run the game!"""
    global level

    log.info("Starting game!")

    for _ in track(range(11), description="Starting..."):
        await trio.sleep(0.1)
    await trio.sleep(1)
    clear()

    level = 1

    start: Event = Event()
    while not start.is_set():
        await print_live_panel(
            """Welcome to the game!
Things to note:

- Use `w` `a` `s` `d` to move cardinally.
- Use `q` `e` `z` `c` to move diagonally.
- Answer questions with number keys
  (If the answer has no number, the last option will be the default).
- To quit the game, press `Ctrl` + `C` followed by any other key
  (This will not save your progress).
""",
            title="Instructions",
        )

        if await trio.to_thread.run_sync(Confirm.ask, "Do you understand?"):
            start.set()
        clear()

    await print_live_panel(
        """You just found a map to an ancient city in your grandfather's attic.
What do you do?

1. Follow the map.
2. Stay home and go to sleep.
3. Research about the city.""",
        title="Introduction",
    )

    match await trio.to_thread.run_sync(
        functools.partial(IntPrompt.ask, "What do you do?", choices=["1", "2", "3"]),
    ):
        case 1:
            clear()
            await tprint(
                "You follow the map and find a cave entrance. You enter the cave.",
            )
            log.info("Waiting")
            await trio.sleep(2)
            log.info("Loading")
            await run_level(p / "level1.txt")
        case 2:
            clear()
            await tprint("You go to sleep. You are The Real Winner!")
            log.info("Waiting")
            await trio.sleep(2)
            log.info("Loading")
            sys.exit()
        case 3:
            clear()
            await tprint("You decide to research about the city.")
            log.info("Waiting")
            await trio.sleep(2)
            log.info("Loading")
            await run_level(p / "city.txt")


async def print_live_panel(
    lines: str,
    title: str | None = None,
    interval: float = 0.8,
) -> None:
    """Print a rich live panel."""
    lines_list = lines.splitlines()
    text = lines_list[0]
    with Live(
        Panel(text, title=title),
    ) as pan:
        for line in lines.splitlines()[1:]:
            await trio.sleep(interval)
            pan.update(
                Panel(
                    Markdown(text := text + "\n" + line),
                    title=title,
                ),
            )
    await trio.sleep(interval)


async def run_level(file: Path) -> None:
    """Run a level."""
    log.info("Getting lock")
    lock = Lock()

    log.info("Opening level!")
    await open_level(file)

    log.info("Starting level!")
    async with trio.open_nursery() as nursery:
        nursery.start_soon(cave_explore, lock)
        nursery.start_soon(control, lock)


def main() -> None:
    """Run the game, asynchronously."""
    clear()

    clock = trio.testing.MockClock(100000) if DEBUG else None

    trio.run(run_game, clock=clock, strict_exception_groups=True)


if __name__ == "__main__":
    if DEBUG:
        traceback.install(suppress=[trio, readchar])
        logging.basicConfig(
            level="INFO",
            format="%(message)s",
            datefmt="[%X]",
            handlers=[
                RichHandler(),
            ],
        )
    main()
