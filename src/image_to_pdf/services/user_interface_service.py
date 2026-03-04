import curses
import re
from typing import Union


def prompt_user_input(stdscr: curses.window, message: str) -> Union[str, None]:
    """
    Prompts the user to enter a string and returns the string entered by the user

    :param stdscr: The curses object
    :param message: The message to display to the user
    :return: The string entered by the user
    """

    curses.curs_set(1)
    user_input: Union[str, None] = ""

    # Capture user input until they press enter or escape
    while True:
        stdscr.clear()
        try:
            stdscr.addstr(0, 0, f"{message}: ", curses.color_pair(1))
            stdscr.addstr(f"{user_input}")
        except curses.error:
            pass

        key: int = stdscr.getch()
        if key in [ord("\n"), curses.KEY_ENTER]:
            break
        elif key in [ord("\b"), curses.KEY_BACKSPACE]:
            if user_input:
                user_input = user_input[:-1]
        elif key == 27:
            user_input = None
            break
        else:
            if 32 <= key <= 126:
                user_input += chr(key)

    curses.curs_set(0)
    return user_input


def prompt_list_selection(
    stdscr: curses.window, result_list: list[str], page_size: int, title: str
) -> Union[list[int], None]:
    """
    Displays the result list to the user and prompt them to select an item

    :param stdscr: The curses object
    :param result_list: The list of items to display
    :param page_size: The number of results to display per page
    :param title: The title at the top of the list
    :return: The index of the selected item
    """

    result_list_copy: list[str] = result_list.copy()
    excluded_files: set[str] = set()
    current_index: int = 0
    item_to_swap: Union[int, None] = None
    search_query: str = ""

    max_y, max_x = stdscr.getmaxyx()

    while True:
        stdscr.clear()

        filtered_list: list[str] = result_list_copy.copy()
        if search_query:
            try:
                pattern = re.compile(search_query, re.IGNORECASE)
                filtered_list = [f for f in filtered_list if pattern.search(f)]
            except re.error:
                filtered_list = []

        page_start: int = (current_index // page_size) * page_size
        page_end: int = min(page_start + page_size, len(filtered_list))

        if max_y < 4 or max_x < 10:
            break

        # Display the list of results
        try:
            stdscr.addstr(0, 0, f"{title}:", curses.color_pair(1))
            stdscr.addstr(1, 0, "Use ", curses.color_pair(1))
            stdscr.addstr("↑/↓", curses.color_pair(4))
            stdscr.addstr(" for navigation ", curses.color_pair(1))
            if not search_query:
                stdscr.addstr("→", curses.color_pair(4))
                stdscr.addstr(" to swap ", curses.color_pair(1))
            stdscr.addstr("←")
            stdscr.addstr(" to exclude ", curses.color_pair(1))
            stdscr.addstr("ESC")
            stdscr.addstr(" clear search/exit ", curses.color_pair(1))
            stdscr.addstr("ENTER")
            stdscr.addstr(" proceed", curses.color_pair(1))
            stdscr.addstr(2, 0, "Search: ", curses.color_pair(1))
            stdscr.addstr(f"{search_query}_")
        except curses.error:
            pass

        for i in range(page_start, page_end):
            row = i - page_start + 3
            if row >= max_y:
                break
            try:
                if i == current_index:
                    stdscr.addstr(row, 0, "> ", curses.color_pair(2))

                    if i == item_to_swap:
                        stdscr.addstr(
                            f" {filtered_list[i]}",
                            curses.color_pair(3),
                        )
                    elif filtered_list[i] in excluded_files:
                        stdscr.addstr(
                            f" {filtered_list[i]}",
                            curses.color_pair(2),
                        )
                    else:
                        stdscr.addstr(
                            f" {filtered_list[i]}",
                            curses.A_REVERSE,
                        )
                else:
                    if i == item_to_swap:
                        stdscr.addstr(row, 0, " ", curses.A_REVERSE)
                        stdscr.addstr(" ")
                        stdscr.addstr(f" {filtered_list[i]}", curses.color_pair(3))
                    elif filtered_list[i] in excluded_files:
                        stdscr.addstr(row, 0, " ", curses.A_REVERSE)
                        stdscr.addstr(" ")
                        stdscr.addstr(f" {filtered_list[i]}", curses.color_pair(2))
                    else:
                        stdscr.addstr(row, 0, " ", curses.A_REVERSE)
                        stdscr.addstr(" ")
                        stdscr.addstr(f" {filtered_list[i]}")
            except curses.error:
                pass

        try:
            display_start = page_start + 1
            display_end = min(page_start + page_size, len(filtered_list))
            stdscr.addstr(
                f"\n{display_start}-{display_end} of {len(filtered_list)} files ({len(result_list_copy)} total)",
                curses.color_pair(1),
            )
        except curses.error:
            pass
        stdscr.refresh()

        # Process user input
        if len(result_list) == 0:
            return []

        key: int = stdscr.getch()

        if key in [ord("\b"), curses.KEY_BACKSPACE]:
            if search_query:
                search_query = search_query[:-1]
                current_index = 0
                item_to_swap = None
        elif key == 27:
            if search_query:
                search_query = ""
                current_index = 0
                item_to_swap = None
            else:
                return None
        elif key == curses.KEY_UP:
            current_index = (
                (current_index - 1) % len(filtered_list) if filtered_list else 0
            )
        elif key == curses.KEY_DOWN:
            current_index = (
                (current_index + 1) % len(filtered_list) if filtered_list else 0
            )
        elif key == curses.KEY_LEFT:
            if filtered_list and current_index < len(filtered_list):
                file_name = filtered_list[current_index]
                if file_name not in excluded_files:
                    excluded_files.add(file_name)
                else:
                    excluded_files.remove(file_name)
        elif key == curses.KEY_RIGHT:
            if (
                not search_query
                and filtered_list
                and current_index < len(filtered_list)
            ):
                if item_to_swap is None:
                    item_to_swap = current_index
                else:
                    temp = filtered_list[item_to_swap]
                    filtered_list[item_to_swap] = filtered_list[current_index]
                    filtered_list[current_index] = temp
                    result_list_copy = filtered_list.copy()
                    item_to_swap = None
        elif key in [ord("\n"), curses.KEY_ENTER]:
            original_indices: dict[str, int] = {
                name: i for i, name in enumerate(result_list)
            }
            return [
                original_indices[name]
                for name in result_list_copy
                if name not in excluded_files
            ]
        elif 32 <= key <= 126:
            search_query += chr(key)
            current_index = 0
            item_to_swap = None
        else:
            continue
