"""A fun little text-based game."""


# ruff: noqa: PLW0603


import logging
import os
import sys
from pathlib import Path
from typing import Literal, NoReturn

import numpy as np
import readchar as rchar
import trio
from readchar import readchar
from rich import live, markdown, panel, progress, prompt, traceback
from rich.logging import RichHandler


def clear() -> None:
    """Clear the terminal."""
    print("\033c", end="", flush=True)


def heartcount(hearts: int) -> str:
    """Return a string of hearts."""
    return "".join(["♥" for _ in range(hearts)])


async def tprint(text: str, sleep_time: float = 0.08) -> None:
    """Print a string, typewriter style!"""
    for character in text:
        sys.stdout.write(character)
        sys.stdout.flush()
        await trio.sleep(sleep_time)


x: int
y: int
playerchar: Literal[" ", "▲", "◀", "▼", "▶", "◣", "◥", "◤", "◢"]
ox: int
oy: int
px: int = 0
py: int = 0
nx: int = 0
ny: int = 0
screen: str
grid: np.ndarray
smgrid: np.ndarray
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
killthread = False
game = True
width = 12
level: int


p = Path(os.path.realpath(__file__)).parent


log = logging.getLogger("game")


def open_level(level_path: Path) -> None:
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
    with level_path.open("r") as f:
        lines = f.readlines()

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

    playerchar = " "
    ox = 0
    oy = 0
    screen = ""
    grid = np.array(arr, dtype=object)
    toggletrap = 0


def keycount(keys: int) -> str:
    """Return a string of keys."""
    return "".join([keycolor for _ in range(keys)])


def scrprt(width: int) -> str:
    """Create the items bar."""
    return heartstring + " " * (((width) + 2) - (items[0] + items[1])) + keystring


async def cave_explore() -> None:
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
    global killthread
    global game
    global screen

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
""",
            )
            if prompt.Confirm.ask("Do you find and follow the river?"):
                clear()
                await tprint("You follow the river and find a deep cave.")
                await endroom()
        elif grid[y][x] == watercolor:
            game = False
            await tprint("")
            await tprint("")
            if prompt.Confirm.ask("Follow the underground river?"):
                clear()
                await tprint("You follow the river and find a deep cave.")
                await endroom()
            else:
                game = True
        elif grid[y][x] == "∆":
            items[0] -= 1
            heartstring = heartcount(items[0])
            screen = scrprt(px - abs(nx))
        elif grid[y][x] == "⊡":
            if items[1] > 0:
                items[1] -= 1
                screen = scrprt(px - abs(nx))
                if level == 1:
                    await key()
                    game = True
            if level == 2:
                await end()

        screen = scrprt(px - abs(nx))
        if grid[y][x] not in {" ", heartcolor, keycolor, "∆"}:
            x = ox
            y = oy
            oy = 0
            ox = 0
        else:
            clear()
            grid[y][x] = "\033[96m" + playerchar + "\033[0m" + bgcolor
            grid[oy][ox] = arr[oy][ox]
            screenstr = bgcolor
            nx = max(x - width, 0)
            ny = max(y - width, 0)
            px = min(x + width, num_cols)
            py = min(y + width, num_cols)
            screenstr += "╔" + ("═" * (px - abs(nx))) + "╗" + "\n"
            smgrid = grid[ny:py, nx:px]
            for i in smgrid:
                screenstr += "║"
                screenstr += "".join(i)
                screenstr += "║"
                screenstr += "\n"
            screenstr += "╚" + ("═" * (px - abs(nx))) + "╝"
            screenstr += "\n"
            screenstr += screen
            screenstr += "\n"
            print(screenstr)
        ox = x
        oy = y
        await trio.sleep(0.05)
    clear()
    killthread = True


async def key() -> None:
    """Use the key."""
    global game
    global killthread
    game = False
    killthread = True
    await print_live_panel(
        """Door Opened!

You find treasure behind the door.
What do you do?

1. Take the treasure.
2. Leave the treasure and continue looking for the city.""",
    )
    match prompt.IntPrompt.ask("What do you do?", choices=["1", "2"]):
        case 1:
            await tprint("It was a trap! You died!")
            sys.exit()
        case 2:
            await print_live_panel(
                """You are tired, do you continue looking for the city or leave?
1. Continue looking for the city.
2. Leave.""",
            )

            match prompt.IntPrompt.ask("What do you do?", choices=["1", "2"]):
                case 1:
                    await endroom()

                case 2:
                    await tprint("You leave the cave and go home.")
                    await tprint("You Loose!")
                    sys.exit()


async def endroom() -> None:
    """Go to end room."""
    global game
    global killthread
    global level
    global x
    global y

    end_cave_file = p / "endcave.txt"
    open_level(end_cave_file)

    game = True
    killthread = False
    x = 1
    y = 1
    level = 2


async def control() -> NoReturn:
    """Control the player."""
    global x
    global y
    global playerchar

    while True:
        log.debug("Control")
        while game:
            log.debug("on")
            rc = await trio.to_thread.run_sync(readchar)
            match rc:
                case "w":
                    y -= 1
                    playerchar = "▲"
                case "a":
                    x -= 1
                    playerchar = "◀"
                case "s":
                    y += 1
                    playerchar = "▼"
                case "d":
                    x += 1
                    playerchar = "▶"
                case "z":
                    x -= 1
                    y += 1
                    playerchar = "◣"
                case "e":
                    x += 1
                    y -= 1
                    playerchar = "◥"
                case "q":
                    x -= 1
                    y -= 1
                    playerchar = "◤"
                case "c":
                    x += 1
                    y += 1
                    playerchar = "◢"
                case _:
                    pass
            await trio.sleep(0.05)
        while not game:
            await trio.sleep(1)


async def end() -> NoReturn:
    """End the game as a winner."""
    global game
    global killthread

    game = True
    killthread = False
    await print_live_panel(
        """Que cutscene!

You Win!""",
    )
    sys.exit()


async def main() -> None:
    """Run the game!"""
    global level

    for _ in progress.track(range(11), description="Starting..."):
        await trio.sleep(0.1)
    await trio.sleep(1)
    clear()

    level = 1

    start = False
    while not start:
        await print_live_panel(
            """Welcome to the game!
Things to note:

- Use `w` `a` `s` `d` to move cardinally.
- Use `q` `e` `z` `c` to move diagonally.
- Answer questions with number keys.
  (If the answer has no number, the last option will be the default)
""",
            title="Instructions",
        )

        start = prompt.Confirm.ask("Do you understand?")
        clear()

    await print_live_panel(
        """You just found a map to an ancient city in your grandfather's attic.
What do you do?

1. Follow the map.
2. Stay home and go to sleep.
3. Research about the city.""",
        title="Introduction",
    )

    match prompt.IntPrompt.ask("What do you do?", choices=["1", "2", "3"]):
        case 1:
            await tprint(
                "You follow the map and find a cave entrance. You enter the cave.",
            )
            await trio.sleep(2)
            await run_level(p / "level1.txt")
        case 2:
            await tprint("You go to sleep. You are The Real Winner!")
            await trio.sleep(2)
            sys.exit()
        case 3:
            await tprint("You decide to research about the city.")
            await trio.sleep(2)
            await run_level(p / "city.txt")


async def print_live_panel(
    lines: str,
    title: str | None = None,
    interval: float = 0.8,
) -> None:
    """Print a rich live panel."""
    lines_list = lines.splitlines()
    text = lines_list[0]
    with live.Live(
        panel.Panel(text, title=title),
    ) as pan:
        for line in lines.splitlines()[1:]:
            await trio.sleep(interval)
            pan.update(
                panel.Panel(
                    markdown.Markdown(text := text + "\n" + line),
                    title=title,
                ),
            )
    await trio.sleep(interval)


async def run_level(file: Path) -> None:
    """Run a level."""
    open_level(file)

    async with trio.open_nursery() as nursery:
        nursery.start_soon(cave_explore)
        nursery.start_soon(control)


if __name__ == "__main__":
    logging.basicConfig(
        level=100,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                tracebacks_suppress=[trio, rchar],
            ),
        ],
    )

    clear()
    traceback.install()
    trio.run(main)
