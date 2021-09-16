from typing import List

import os
import sys
import time
import curses
import curses.textpad

banner1 = """
██╗    ██╗ █████╗ ████████╗ ██████╗██╗  ██╗███████╗ ██████╗ ██╗     
██║    ██║██╔══██╗╚══██╔══╝██╔════╝██║  ██║██╔════╝██╔═══██╗██║     
██║ █╗ ██║███████║   ██║   ██║     ███████║███████╗██║   ██║██║     
██║███╗██║██╔══██║   ██║   ██║     ██╔══██║╚════██║██║▄▄ ██║██║     
╚███╔███╔╝██║  ██║   ██║   ╚██████╗██║  ██║███████║╚██████╔╝███████╗
 ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝╚══════╝ ╚══▀▀═╝ ╚══════╝
"""


def showBanner(stdscr):
    banner = stdscr.subwin(0, 0, 0, 9)
    banner.addstr(banner1)
    banner.refresh()

def getInput(stdscr, prompt_str: str):
    curses.echo()
    stdscr.addstr(10, 0, prompt_str)
    stdscr.refresh()

    return stdscr.getstr(11, 0, 20).decode("utf-8")

def select_option(stdscr, title: str, options: List[str]) -> str:
    win = stdscr.subwin(0, 0, 10, 0)
    enum_options = [(i, o) for i, o in enumerate(options)]
    current_option = 0
    selected_option = None

    win.addstr(title + "\n")

    while True:
        for option_id, option_txt in enum_options:
            win.addstr(option_id+1, 1,
                       "◉ "+option_txt + "\n",
                       curses.color_pair(1) if option_id == current_option
                                            else curses.color_pair(2)) 
        win.refresh()
        c = stdscr.getch()

        if c == curses.KEY_UP:
            if current_option != 0 and 0 < current_option < len(options):
                current_option -= 1
        elif c == curses.KEY_DOWN:
            if current_option != len(options)-1 and 0 <= current_option < len(options):
                current_option += 1
        elif c == curses.KEY_ENTER or c == 10 or c == 13:
            selected_option = options[current_option]
            break

        win.refresh()

    win.clear()
    win.refresh()

    return selected_option

def start_editor(stdscr, db: str, db_name: str) -> None:
    stdscr.clear()
    stdscr.refresh()

    cols = curses.COLS-1
    rows = curses.LINES-1

    editor = stdscr.subpad(rows, cols//2, 0, 0)
    monitor = stdscr.subpad(rows, cols//2+1, 0, cols//2+1)

    editor.bkgd(' ', curses.color_pair(4) | curses.A_BOLD | curses.A_REVERSE)
    monitor.bkgd(' ', curses.color_pair(3) | curses.A_BOLD | curses.A_REVERSE)


def list_database(stdscr, db: str) -> str:
    if db == "postgresql":
        dbs = os.popen("psql -c 'SELECT datname FROM pg_database;'").read().strip().split()[2:-1]
        return select_option(stdscr, "Select an database", dbs)


def connect_to_database(stdscr, db: str, db_name: str) -> None:
    if db == "postgresql":
        os.popen("psql -c '\c {}'" .format(db_name)).read().strip()

    start_editor(stdscr, db, db_name)

def create_database(stdscr, db: str) -> None:
    if db == "postgresql":
        db_name = getInput(stdscr, "Enter database name")
        out = os.popen("psql -c 'CREATE DATABASE {};'" .format(db_name)).read().strip()

        if out == '':
            time.sleep(1.5)
            stdscr.clear()
            stdscr.refresh()
            showBanner(stdscr)
            create_database(stdscr, db)
        else:
            connect_to_database(stdscr, db, db_name)

def start_database(stdscr, db: str) -> None:
    if db == "postgresql":
        option = select_option(stdscr, "Select an option", ["Create a database", "Connect to a database"])

        if option == "Create a database":
            create_database(stdscr, db)
        else:
            db_name = list_database(stdscr, db)
            connect_to_database(stdscr, db, db_name)
    else:
        return

def main(stdscr):
    curses.cbreak()
    curses.noecho()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLUE)

    stdscr.clear()
    showBanner(stdscr)

    option = select_option(stdscr, "Select Database Engine", ["postgresql", "mysql"])
    start_database(stdscr, option)

    stdscr.refresh()
    stdscr.getkey()

if __name__ == '__main__':
    curses.wrapper(main)
