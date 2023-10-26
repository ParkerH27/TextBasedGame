"""A fun little text-based game."""


# ruff: noqa: PLW0603


from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path
from typing import Literal, NoReturn

import numpy as np
from readchar import readchar
from rich import traceback


def clear() -> None:
    """Clear the terminal."""
    print("\033[H\033[2J", end="", flush=True)


def heartcount(hearts: int) -> str:
    """Return a string of hearts."""
    return "".join(["♥" for _i in range(hearts)])


def tprint(text: str, sleep_time: float = 0.08) -> None:
    """Print a string, typewriter style!"""
    for character in text:
        sys.stdout.write(character)
        sys.stdout.flush()
        time.sleep(sleep_time)


def tinput(text: str) -> str:
    """Get input, typewriter style!"""
    tprint(text, sleep_time=0.05)

    return input()


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


def scrprt(width: int) -> None:
    """Create the items bar."""
    global screen
    screen = heartstring + " " * (((width) + 2) - (items[0] + items[1])) + keystring


def cave_explore() -> None:
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
    heartstring = heartcount(items[0])
    keystring = keycount(items[1])
    scrprt(px - abs(nx))
    while not killthread:
        if items[0] == 0:
            print("You died!")
            sys.exit()
        if grid[y][x] == heartcolor:
            arr[y][x] = " "
            items[0] += 1
            heartstring = heartcount(items[0])
            scrprt(px - abs(nx))
        elif grid[y][x] == keycolor:
            arr[y][x] = " "
            items[1] += 1
            keystring = keycount(items[1])
            scrprt(px - abs(nx))
        elif grid[y][x] == "☰":
            arr[y][x] = " "
            tprint("You found a note!\n")
            tprint(
                """It reads:
 5/6/1926\n I found a river today near the Library. I think I will follow it tomorrow.
 """,
            )
            if "1" in input("Do you find and follow the river?\n1. Yes\n2. No\n>:"):
                clear()
                print("You follow the river and find a cave.")
                endroom()
        elif grid[y][x] == watercolor:
            game = False
            print()
            print()
            if "1" in input("Follow the underground river?\n1. Yes\n2. No\n>:"):
                clear()
                print("You follow the river and find a cave.")
                endroom()
            else:
                game = True
        elif grid[y][x] == "∆":
            items[0] -= 1
            heartstring = heartcount(items[0])
            scrprt(px - abs(nx))
        elif grid[y][x] == "⊡":
            if items[1] > 0:
                items[1] -= 1
                scrprt(px - abs(nx))
                if level == 1:
                    key()
                    game = True
            if level == 2:
                end()

        scrprt(px - abs(nx))
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
        time.sleep(0.05)
    clear()
    killthread = True


def key() -> None:
    """Use the key."""
    global game
    global killthread
    game = False
    killthread = True
    inpt = tinput(
        """Door Opened!

You find treasure behind the door.
What do you do?

1. Take the treasure.
2. Leave the treasure and continue looking for the city.
""",
    )
    if "1" in str(inpt):
        tprint("It was a trap! You died!")
        sys.exit()
    else:
        inpt2 = tinput(
            """You continue looking for the city.
You are tired, do you continue looking for the city or leave?
1. Continue
2. Leave""",
        )
        if "1" in str(inpt2):
            endroom()
        else:
            tprint("You leave the cave and go home.")
            tprint("You Loose!")
            sys.exit()


def endroom() -> None:
    """Go to end room."""
    end_cave_file = p / "endcave.txt"
    open_level(end_cave_file)
    print("You follow the river and find a deep cave.")
    global game
    global killthread
    global level
    global x
    global y
    game = True
    killthread = False
    x = 1
    y = 1
    level = 2


def control() -> NoReturn:
    """Control the player."""
    global x
    global y
    global playerchar
    while True:
        print("Control")
        while game:
            print("on")
            rc = readchar()
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
            time.sleep(0.05)
        while not game:
            time.sleep(1)


def end() -> NoReturn:
    """End the game as a winner."""
    global game
    global killthread
    game = True
    killthread = False
    tprint("Que cutscene!")
    print()
    tprint("You Win!")
    sys.exit()


def main() -> None:
    """Run the game!"""
    global level
    print("\n")
    tprint("Starting")
    time.sleep(0.4)
    tprint("...\n", sleep_time=0.4)
    time.sleep(0.9)
    tprint("-----------")
    time.sleep(0.2)
    clear()

    time.sleep(3)
    level = 1

    ce_thread = threading.Thread(target=cave_explore)
    control_thread = threading.Thread(target=control)
    start = False
    while not start:
        tprint("Welcome to the game!\n")
        inpt = tinput(
            """use wasd to move
qezc to move diagonally
Answer questions with number keys.
(If the answer has no number, the last option will be the default)
1. I understand
2. I very clearly do not understand
:""",
        )
        if "1" in str(inpt):
            start = True
    inpt = tinput(
        """You just found a map to an ancient city in your grandfather's attic.
What do you do?
1. Follow the map
2. Stay home and go to sleep
3. Research about the city
:""",
    )
    if "1" in str(inpt):
        lvl1_file = p / "level1.txt"
        open_level(lvl1_file)
        tprint("You follow the map and find a cave entrance. You enter the cave.")
        time.sleep(2)
        ce_thread.start()
        control_thread.start()
    elif "2" in str(inpt):
        tprint("You go to sleep. You are The Real Winner!")
        sys.exit()
    else:
        city_file = p / "city.txt"
        open_level(city_file)
        tprint("You decide to research about the city.")
        ce_thread.start()
        control_thread.start()


if __name__ == "__main__":
    traceback.install()
    main()
