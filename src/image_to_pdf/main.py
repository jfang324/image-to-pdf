import curses
import os
from .services.file_access_service import *
from .services.user_interface_service import *


def end() -> None:
    quit()


def start(stdscr: curses) -> None:
    # Main body of the program

    # Initialize curses settings for UI
    curses.curs_set(0)
    curses.noecho()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_WHITE)

    # Prompt user for a valid directory containing images
    message: str = (
        "Enter the directory containing the images (default is current directory)"
    )
    input_directory_path: str = ""
    while True:
        input_directory_path = prompt_user_input(stdscr, message)

        if input_directory_path == None:
            end()
        else:
            input_directory_path = input_directory_path or os.getcwd()
            if validate_path(input_directory_path):
                break
            else:
                message = f"'{input_directory_path}' is not a valid directory. Enter a valid directory"

    # Prompt user to select which files to include and in which order to convert to PDF
    file_list: list[str] = get_file_list(input_directory_path)
    processed_file_indexes: list[int] = prompt_list_selection(
        stdscr,
        [os.path.basename(file) for file in file_list],
        20,
        f"files in {input_directory_path}",
    )

    if processed_file_indexes == None:
        end()

    # Remove any files that were excluded from the list of files and exit if no files are left/found
    processed_file_list: list[str] = [file_list[i] for i in processed_file_indexes]
    while len(processed_file_list) == 0:
        stdscr.clear()
        stdscr.addstr(
            0, 0, "No images found. Press escape to exit.", curses.color_pair(1)
        )
        key: int = stdscr.getch()
        if key == 27:
            end()

    # Prompt user for a valid directory to save the PDF file
    message = f"Enter the path to save the PDF file (default is current directory)"
    output_directory_path: str = ""
    while True:
        output_directory_path = prompt_user_input(stdscr, message)
        if output_directory_path == None:
            end()
        else:
            output_directory_path = output_directory_path or os.getcwd()
            if validate_path(output_directory_path):
                break
            else:
                message = f"'{output_directory_path}' is not a valid directory. Enter a valid directory"

    # Prompt user for a valid name for the PDF file
    message = "Enter the name of the PDF file (default is 'output')"
    output_name: str = ""
    while True:
        output_name = prompt_user_input(stdscr, message) or "output"
        invalid_characters: list[str] = [
            "\\",
            "/",
            ":",
            "*",
            "?",
            '"',
            "<",
            ">",
            "|",
        ]
        valid: bool = True

        for invalid_character in invalid_characters:
            if invalid_character in output_name:
                message = f"'{output_name}' is not a valid name. Enter a valid name"
                valid = False
                break

        if valid:
            break

    # Convert images to PDF and save the PDF file
    convert_images_to_pdf(processed_file_list, output_directory_path, output_name)
    print(f"{output_name}.pdf saved to {output_directory_path}")


def main():
    # wrap start in curses.wrapper to initialize curses
    curses.wrapper(start)


if __name__ == "__main__":
    main()
