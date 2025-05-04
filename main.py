import curses
import random
import time
import csv

stdscr = curses.initscr()

curses.start_color()
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_GREEN)
curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_CYAN)
curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_CYAN)
curses.init_pair(4, curses.COLOR_RED, curses.COLOR_CYAN)
curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLUE)
curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_CYAN)
curses.curs_set(0)
curses.noecho()
curses.cbreak()
curses.update_lines_cols()
stdscr.nodelay(True)
stdscr.keypad(True)
stdscr.refresh()

MAXL = curses.LINES - 1
MAXC = curses.COLS - 1
playing = True
player_l = player_c = 0

score = 0
FUEL = 5000

PLAYER_CHAR = 'P'
ENEMY_CHAR = 'E'
FUEL_CHAR = '$'
BULLET_CHAR_UP = '^'
BULLET_CHAR_DOWN = '|'

world = []
enemy = []
fuel = []
bullet = []


def random_in_range(n1, n2, range):
    return random.randint(n1 - range, n1 + range), random.randint(n2 - range, n2 + range)


def in_range(n, min, max):
    if n < min:
        return min
    if n > max:
        return max
    return n


def random_place(a_range=10):
    a_range = min(a_range, MAXL-1)
    if a_range != 0:
        a = random.randint(0, MAXL-a_range)
    else:
        a = 0
    b = random.randint(left_size+1, MAXC-right_size)
    while world[a][b] != ' ':
        if a_range != 0:
            a = random.randint(0, MAXL-a_range)
        else:
            a = 0
        b = random.randint(left_size+1, MAXC-right_size)
    return a, b


def init():
    global left_size, right_size, player_c, player_l, lastbest
    with open("score.csv", 'r') as f:
        reader = csv.DictReader(f)
        lastbest = next(reader)["bestscore"]

    # Initally we make a row as a sample that helps us to make upper rows without inappropriate left-right size
    world.append([])
    left_size = 50
    right_size = 50
    for _ in range(left_size):
        world[0].append("+")
    for _ in range(MAXC - (left_size + right_size)):
        world[0].append(" ")
    for _ in range(right_size):
        world[0].append("+")

    for _ in range(MAXL - 1):
        world.insert(0, [])
        left_size, right_size = random_in_range(left_size, right_size, 1)
        # Controling Errors
        if left_size < 0:
            left_size = 20
        if right_size < 0:
            right_size = 20
        total = left_size + right_size
        if total >= MAXC - 8:
            right_size = MAXC - left_size - random.randint(4, 10)
            if right_size < 8:
                left_size = MAXC - random.randint(20, 25)
                right_size = 10
        # Making new row finally
        for _ in range(left_size):
            world[0].append('+')
        for _ in range(MAXC - (left_size + right_size)):
            world[0].append(' ')
        for _ in range(right_size):
            world[0].append('+')

    el, ec = random_place(0)
    enemy.append((el, ec))

    fl, fc = random_place(0)
    fuel.append((fl, fc))

    player_l, player_c = MAXL - \
        5, (MAXC - right_size - left_size) // 2 + left_size


def river():
    global left_size, right_size
    world.pop()
    left_size, right_size = random_in_range(left_size, right_size, 2)

    # Error Controling
    if left_size < 0:
        left_size = 5
    if right_size < 0:
        right_size = 5
    total = left_size + right_size
    if total >= MAXC - 8:
        if total >= MAXC:
            right_size -= random.randint(5, 10)
            left_size -= random.randint(5, 10)
            if right_size < 8:
                left_size -= 10
                right_size += 10
        else:
            right_size -= random.randint(5, 10)
    if total < MAXC - 50:
        right_size += 5
        left_size += 5

    # Finally making new row
    world.insert(0, [])
    for _ in range(left_size):
        world[0].append('+')
    for _ in range(MAXC - (left_size + right_size)):
        world[0].append(' ')
    for _ in range(right_size):
        world[0].append('+')


def make_enemy():
    el, ec = random_place(0)
    enemy.append((el, ec))


def make_fuel():
    fl, fc = random_place(0)
    fuel.append((fl, fc))


def shoot():
    bullet.append((player_l, player_c))


def move(key):
    global player_l, player_c
    if key == 'w':
        player_l -= 1
    elif key == 's':
        player_l += 1
    elif key == 'a':
        player_c -= 1
    elif key == 'd':
        player_c += 1

    player_c = in_range(player_c, 0, MAXC-1)
    player_l = in_range(player_l, 0, MAXL-1)


def enemy_move():
    global enemy
    for i in range(len(enemy)):
        el, ec = enemy[i]
        el += 1
        el = in_range(el, 0, MAXL-1)
        enemy[i] = (el, ec)


def enemy_pos():
    global enemy
    enemy = list(filter(lambda x: x[0] < MAXL-1, enemy))


def fuel_move():
    global fuel
    for i in range(len(fuel)):
        fl, fc = fuel[i]
        fl += 1
        fl = in_range(fl, 0, MAXL-1)
        fuel[i] = (fl, fc)


def fuel_pos():
    global fuel
    fuel = list(filter(lambda x: x[0] < MAXL-1, fuel))


def bullet_move():
    global bullet
    for i in range(len(bullet)):
        bl, bc = bullet[i]
        bl -= 2
        bullet[i] = (bl, bc)
    bullet = list(filter(lambda x: x[0] > 0, bullet))


def draw():
    if not playing:
        stdscr.addstr(MAXL//2, MAXC//2, "You died!", curses.color_pair(6))
        stdscr.refresh()
        time.sleep(3)

    # Drawing river
    for i in range(len(world)):
        for j in range(len(world[i])):
            if world[i][j] == '+':
                stdscr.addch(i, j, world[i][j], curses.color_pair(1))
            else:
                stdscr.addch(i, j, world[i][j], curses.color_pair(2))

    # Drawing enemies
    for e in enemy:
        el, ec = e
        stdscr.addch(el, ec, ENEMY_CHAR, curses.color_pair(3))

    # Drawing fuels
    for f in fuel:
        fl, fc = f
        stdscr.addch(fl, fc, FUEL_CHAR, curses.color_pair(4))

    # Drawing bullets
    for b in bullet:
        bl, bc = b
        stdscr.addch(bl, bc, BULLET_CHAR_UP, curses.color_pair(8))
        stdscr.addch(bl+1, bc, BULLET_CHAR_DOWN, curses.color_pair(8))

    # score
    stdscr.addstr(3, 2, f" Score: {score} ", curses.color_pair(7))

    # best score
    stdscr.addstr(1, 2, f" Best score: {lastbest} ", curses.color_pair(7))

    # fuel
    stdscr.addstr(5, 2, f" Fuel: {FUEL//100} ", curses.color_pair(7))

    # Drawing the player
    stdscr.addch(player_l, player_c, PLAYER_CHAR, curses.color_pair(5))
    stdscr.refresh()

# Checkings


def check_river():
    global playing
    if world[player_l][player_c] == '+':
        playing = False


def check_enemy():
    global playing
    for e in enemy:
        if (player_l, player_c) == e:
            playing = False


def check_fuel():
    global FUEL, playing
    for f in fuel:
        if (player_l, player_c) == f:
            FUEL += 100
            fuel.remove(f)
        for b in bullet:
            if b == f or (b[0] - 1 == f[0] and b[1] == f[1]):
                FUEL += 1000
                fuel.remove(f)
    if FUEL < 0:
        playing = False


def check_bullet():
    global enemy, score
    for b in bullet:
        for e in enemy:
            if b == e or (b[0] - 1 == e[0] and b[1] == e[1]):
                score += 1
                enemy.remove(e)


# Running and using functions (It works like a main function)
count = 0
init()
while playing:
    count += 1
    try:
        c = stdscr.getkey()
    except:
        c = ''
    if c in "asdw":
        move(c)
    elif c == ' ':
        shoot()
    elif c == 'q':
        playing = False
    if random.random() > 0.9:
        river()
        enemy_move()
        fuel_move()
    if random.random() < 0.005:
        make_enemy()
    if random.random() < 0.003:
        make_fuel()
    if count % 100 == 0:
        FUEL -= 100
    enemy_pos()
    fuel_pos()
    bullet_move()
    check_river()
    check_enemy()
    check_fuel()
    check_bullet()
    draw()
    if not playing:
        if int(lastbest) < score:
            with open("score.csv", 'w+', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["bestscore"])
                writer.writerow([f"{score}"])

stdscr.clear()
stdscr.refresh()
