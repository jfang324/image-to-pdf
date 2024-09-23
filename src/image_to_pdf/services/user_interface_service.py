import curses


def prompt_user_input(stdscr: curses, message: str) -> str:
    """
    Prompts the user to enter a string and returns the string entered by the user

    :param stdscr: The curses object
    :param message: The message to display to the user
    :return: The string entered by the user
    """
    curses.curs_set(1)
    user_input = ""

    # Capture user input until they press enter or escape
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"{message}: ", curses.color_pair(1))
        stdscr.addstr(f"{user_input}")

        key: str = stdscr.getch()
        if key in [ord("\n"), curses.KEY_ENTER]:
            break
        elif key in [ord("\b"), curses.KEY_BACKSPACE]:
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
    stdscr: curses, result_list: list[dict], page_size: int, title: str
) -> list[int]:
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
    item_to_swap: int = None

    while True:
        stdscr.clear()
        page_start: int = (current_index // page_size) * page_size
        page_end: int = min(page_start + page_size, len(result_list))

        # Display the list of results
        stdscr.addstr(0, 0, f"{title}:", curses.color_pair(1))
        stdscr.addstr(1, 0, "Use ", curses.color_pair(1))
        stdscr.addstr("↑/↓", curses.color_pair(4))
        stdscr.addstr(" for navigation, ", curses.color_pair(1))
        stdscr.addstr("→", curses.color_pair(4))
        stdscr.addstr(" to swap, ", curses.color_pair(1))
        stdscr.addstr("←", curses.color_pair(4))
        stdscr.addstr(" to exclude, ", curses.color_pair(1))
        stdscr.addstr("ESC", curses.color_pair(4))
        stdscr.addstr(" to exit, ", curses.color_pair(1))
        stdscr.addstr("ENTER", curses.color_pair(4))
        stdscr.addstr(" to proceed.", curses.color_pair(1))

        for i in range(page_start, page_end):
            if i == current_index:
                stdscr.addstr(i - page_start + 2, 0, "> ", curses.color_pair(2))

                if i == item_to_swap:
                    stdscr.addstr(
                        f" {result_list_copy[i]}",
                        curses.color_pair(3),
                    )
                elif result_list_copy[i] in excluded_files:
                    stdscr.addstr(
                        f" {result_list_copy[i]}",
                        curses.color_pair(2),
                    )
                else:
                    stdscr.addstr(
                        f" {result_list_copy[i]}",
                        curses.A_REVERSE,
                    )
            else:
                if i == item_to_swap:
                    stdscr.addstr(i - page_start + 2, 0, " ", curses.A_REVERSE)
                    stdscr.addstr(" ")
                    stdscr.addstr(f" {result_list_copy[i]}", curses.color_pair(3))
                elif result_list_copy[i] in excluded_files:
                    stdscr.addstr(i - page_start + 2, 0, " ", curses.A_REVERSE)
                    stdscr.addstr(" ")
                    stdscr.addstr(f" {result_list_copy[i]}", curses.color_pair(2))
                else:
                    stdscr.addstr(i - page_start + 2, 0, " ", curses.A_REVERSE)
                    stdscr.addstr(" ")
                    stdscr.addstr(f" {result_list_copy[i]}")
        stdscr.addstr(
            f"\n{page_start + 1}-{page_end} of {len(result_list)} files",
            curses.color_pair(1),
        )
        stdscr.refresh()

        # Process user input
        key: int = stdscr.getch()

        if key == curses.KEY_UP:
            current_index = max(current_index - 1, 0)
        elif key == curses.KEY_DOWN:
            current_index = min(current_index + 1, len(result_list) - 1)
        elif key == curses.KEY_LEFT:
            if result_list_copy[current_index] not in excluded_files:
                excluded_files.add(result_list_copy[current_index])
            else:
                excluded_files.remove(result_list_copy[current_index])
        elif key == curses.KEY_RIGHT:
            if item_to_swap is None:
                item_to_swap = current_index
            else:
                temp = result_list_copy[item_to_swap]
                result_list_copy[item_to_swap] = result_list_copy[current_index]
                result_list_copy[current_index] = temp

                item_to_swap = None
        elif key in [ord("\n"), curses.KEY_ENTER]:
            return [
                result_list.index(result_list_copy[i])
                for i in range(len(result_list))
                if result_list_copy[i] not in excluded_files
            ]
        elif key == 27:
            return None
        else:
            continue
