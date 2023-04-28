from readchar import readchar
import replit
import time
import numpy as np
import threading


width = 12





with open("level1.txt", "r") as f:
    lines = f.readlines()


num_rows = len(lines)
num_cols = max([len(line.strip()) for line in lines])


lines = [line.strip().ljust(num_cols) for line in lines]


arr = np.full((num_rows, num_cols), ".")

for row in range(num_rows):
    for col in range(num_cols):
        arr[row][col] = lines[row][col]

arr = np.char.replace(arr, ".", " ")

heartstring = ""
def heartcount(hearts):
    heartstring = ""
    for i in range(hearts):
        heartstring += "♥"
    return heartstring












global x
x = 1
global y
y = 1
global playerchar
playerchar = ""
global ox
ox = 0
global oy
oy = 0
global hearts
hearts = 0
global screen
screen = ""
global grid
grid = np.array(arr, dtype=object)
global smgrid
global toggletrap
toggletrap = 0


def t1():
    global x
    global y
    global playerchar
    global ox
    global oy
    global hearts
    global screen
    global grid
    global smgrid
    global toggletrap
    a = True
    heartstring = heartcount(hearts)
    screen = heartstring
    while a == True:
        if grid[y][x] == "♥":
            arr[y][x] = " "
            hearts += 1
            heartstring = heartcount(hearts)
            screen = heartstring
        if grid[y][x] != " " and grid[y][x] != "♥":
            x = ox
            y = oy
            oy = 0
            ox = 0
        else:
            replit.clear()
            grid[y][x] = playerchar

            grid[oy][ox] = arr[oy][ox]
            str = ""
            nx = x - width
            ny = y - width
            px = x + width
            py = y + width
            if nx < 0:
                nx = 0
            if ny < 0:
                ny = 0
            if px > num_cols:
                px = num_cols
            if py > num_cols:
                py = num_cols
            str += "╔" + ("═" * (px-abs(nx))) + "╗"+"\n"
            smgrid = grid[ny:py, nx:px]
            for i in smgrid:
                str += "║"
                str += "".join(i)
                str += "║"
                str += "\n"
            str += "╚" + ("═" * (px-abs(nx))) + "╝"
            str += "\n"
            str += screen
            str += "\n"
            print(str)
        ox = x
        oy = y
        time.sleep(0.05)
def t2():
    global x
    global y
    global playerchar
    global ox
    global oy
    global hearts
    global screen
    global grid
    global smgrid
    global toggletrap
    while True:
        rc = readchar()
        if rc == 'w':
            y-=1
            playerchar = "▲"
        elif rc == 'a':
            x-=1
            playerchar = "◀"
        elif rc == 's':
            y+=1
            playerchar = "▼"
        elif rc == 'd':
            x+=1
            playerchar = "▶"
        elif rc == 'z':
            x-=1
            y+=1
            playerchar = "◣"
        elif rc == 'e':
            x+=1
            y-=1
            playerchar = "◥"
        elif rc == 'q':
            x-=1
            y-=1
            playerchar = "◤"
        elif rc == 'c':
            x+=1
            y+=1
            playerchar = "◢"
        else:
            pass
        time.sleep(0.05)

def t3():
    global x
    global y
    global playerchar
    global ox
    global oy
    global hearts
    global screen
    global grid
    global smgrid
    global toggletrap
    while True:
        # Get the location in the grid variable of all of the "▣" in the smgrid variable
        # find the indices of all "▣" in the smgrid
        indices = np.argwhere(grid == "▣")

        # adjust the indices to the corresponding positions in the grid variable
       
        # print the valid indices
        for i in indices:
            if toggletrap == 1:
                grid[i[0]][i[1]+1] = "F"
                grid[i[0]][i[1]-1] = "B"
            elif toggletrap == 2:
                grid[i[0]][i[1]-1] = "V"
                grid[i[0]][i[1]+1] = "A"

def t4():
    global toggletrap
    while True:
        time.sleep(0.5)
        toggletrap = 1
        time.sleep(0.5)
        toggletrap = 2

thread1 = threading.Thread(target=t1)
thread2 = threading.Thread(target=t2)
thread3 = threading.Thread(target=t3)
thread4 = threading.Thread(target=t4)
thread1.start()
thread2.start()
thread3.start()
thread4.start()
 