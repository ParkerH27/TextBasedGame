import os
import threading
import time
from pathlib import Path

import numpy as np
from readchar import readchar


def clear() -> None:
    """Clear the terminal."""
    print("\033[H\033[2J", end="", flush=True)


def heartcount(hearts):
    heartstring = "".join("♥" for _i in range(hearts))
    return heartstring


p = Path(os.path.realpath(__file__)).parent
lvl1_file = p / "level1.txt"
with lvl1_file.open("r") as f:
    lines = f.readlines()

width = 12

num_rows = len(lines)
num_cols = max(len(line.strip()) for line in lines)


lines = [line.strip().ljust(num_cols) for line in lines]


arr = np.full((num_rows, num_cols), ".")

for row in range(num_rows):
    for col in range(num_cols):
        arr[row][col] = lines[row][col]

arr = np.char.replace(arr, ".", " ")

heartstring = ""

x = 1
y = 1
playerchar = ""
ox = 0
oy = 0
hearts = 0
screen = ""
grid = np.array(arr, dtype=object)
toggletrap = False


def t1():
    global x, y, ox, oy, hearts, screen, heartstring
    heartstring = heartcount(hearts)
    while True:
        if grid[y][x] == "♥":
            arr[y][x] = " "
            hearts += 1
            heartstring = heartcount(hearts)
        if grid[y][x] not in (" ", "♥"):
            x = ox
            y = oy
            oy = 0
            ox = 0
        else:
            clear()
            grid[y][x] = playerchar

            grid[oy][ox] = arr[oy][ox]
            screenstr = ""
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
            screenstr += heartstring
            screenstr += "\n"
            print(screenstr)
        ox = x
        oy = y
        time.sleep(0.05)


def t2():
    global x, y, playerchar
    while True:
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
        time.sleep(0.05)


def t3():
    while True:
        # Get the location in the grid variable of all of the "▣" in the smgrid variable
        # find the indices of all "▣" in the smgrid
        indices = np.argwhere(grid == "▣")

        # adjust the indices to the corresponding positions in the grid variable

        # print the valid indices
        for i in indices:
            if toggletrap is False:
                grid[i[0]][i[1] + 1] = "F"
                grid[i[0]][i[1] - 1] = "B"
            elif toggletrap is True:
                grid[i[0]][i[1] - 1] = "V"
                grid[i[0]][i[1] + 1] = "A"


def t4():
    global toggletrap
    while True:
        time.sleep(0.5)
        toggletrap = False
        time.sleep(0.5)
        toggletrap = True


def main():
    thread1 = threading.Thread(group=None, target=t1)
    thread2 = threading.Thread(group=None, target=t2)
    thread3 = threading.Thread(group=None, target=t3)
    thread4 = threading.Thread(group=None, target=t4)
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()


if __name__ == "__main__":
    main()
