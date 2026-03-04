import argparse
import curses
import os
import time
from typing import Union

from .services.file_access_service import (
    convert_images_to_pdf,
    get_image_list,
    validate_directory,
)
from .services.user_interface_service import (
    prompt_list_selection,
    prompt_user_input,
)


def end() -> None:
    quit()


def start(
    stdscr: curses.window,
    page_size: int = 20,
    quality: int = 75,
    optimize: bool = False,
) -> None:
    # Main body of the program

    # Initialize curses settings for UI
    curses.curs_set(0)
    curses.noecho()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)

    # Prompt user for a valid directory containing images
    message: str = (
        "Enter the directory containing the images (default is current directory)"
    )
    input_directory_path: Union[str, None] = ""
    while True:
        result: Union[str, None] = prompt_user_input(stdscr, message)
        if result is None:
            end()
        else:
            input_directory_path = result or os.getcwd()
            if validate_directory(input_directory_path):
                break
            else:
                message = f"'{input_directory_path}' is not a valid directory. Enter a valid directory"

    # Prompt user to select which files to include and in which order to convert to PDF
    image_list: list[str] = get_image_list(input_directory_path)
    processed_image_indexes: Union[list[int], None] = prompt_list_selection(
        stdscr,
        [os.path.basename(image) for image in image_list],
        page_size,
        f"files in {input_directory_path}",
    )

    if processed_image_indexes is None:
        end()

    assert processed_image_indexes is not None

    # Remove any files that were excluded from the list of files and exit if no files are left/found
    processed_image_list: list[str] = [image_list[i] for i in processed_image_indexes]
    while len(processed_image_list) == 0:
        stdscr.clear()
        stdscr.addstr(
            0, 0, "No images found. Press escape to exit.", curses.color_pair(1)
        )
        key: int = stdscr.getch()
        if key == 27:
            end()

    # Prompt user for a valid directory to save the PDF file
    message = "Enter the path to save the PDF file (default is current directory)"
    output_directory_path: Union[str, None] = ""
    while True:
        result = prompt_user_input(stdscr, message)
        if result is None:
            end()
        else:
            output_directory_path = result or os.getcwd()
            if validate_directory(output_directory_path):
                break
            else:
                message = f"'{output_directory_path}' is not a valid directory. Enter a valid directory"

    # Prompt user for a valid name for the PDF file
    message = "Enter the name of the PDF file (default is 'output')"
    output_name: str = ""
    invalid_chars: set[str] = {"\\", "/", ":", "*", "?", '"', "<", ">", "|"}

    while True:
        output_name = prompt_user_input(stdscr, message) or "output"
        valid: bool = True

        for invalid_character in invalid_chars:
            if invalid_character in output_name:
                message = f"'{output_name}' is not a valid name. Enter a valid name"
                valid = False
                break

        if valid:
            break

    # Convert images to PDF and save the PDF file
    start_time = time.time()
    convert_images_to_pdf(
        processed_image_list, output_directory_path, output_name, quality, optimize
    )
    elapsed_time = time.time() - start_time
    print(f"{output_name}.pdf saved to {output_directory_path} ({elapsed_time:.2f}s)")


def main():
    parser = argparse.ArgumentParser(description="Convert images to PDF")
    parser.add_argument(
        "-n",
        "--page-size",
        type=int,
        default=20,
        help="Number of files to display per page (default: 20)",
    )
    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=75,
        help="PDF quality (1-100, default: 75)",
    )
    parser.add_argument(
        "-o",
        "--optimize",
        action="store_true",
        default=False,
        help="Optimize PDF file size",
    )
    args = parser.parse_args()

    curses.wrapper(
        lambda stdscr: start(stdscr, args.page_size, args.quality, args.optimize)
    )


if __name__ == "__main__":
    main()
