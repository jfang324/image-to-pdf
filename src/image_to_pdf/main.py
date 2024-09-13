from .utils import *
import os


def main():
    try:
        input_path: str = ""
        while True:
            input_path = (
                input(
                    "\033[92m"
                    + "Enter the directory containing the images(default is current directory): "
                    + "\033[0m"
                )
                or os.getcwd()
            )

            if validate_path(input_path):
                break
            else:
                print(
                    "\033[91m" + f"{input_path} is not a valid directory." + "\033[0m"
                )

        file_list: list[str] = get_file_list(input_path)
        print(f"Files in {input_path}:")

        for i in range(len(file_list)):
            print(f"{i + 1}. {file_list[i]}")

        while True:
            excluded_file_indexes: list[str] = (
                input(
                    "\033[92m"
                    + "Enter the indexes of the files to exclude(default is none): "
                    + "\033[0m"
                ).split()
                or []
            )
            valid: bool = True

            for index in excluded_file_indexes:
                if int(index) - 1 < 0 or int(index) - 1 > len(file_list):
                    valid = False
                    print("\033[91m" + f"Invalid index: {index}" + "\033[0m")

            if valid:
                break

        excluded_files: list[str] = [
            file_list[int(index) - 1] for index in excluded_file_indexes
        ]
        file_list = [f for f in file_list if f not in excluded_files]

        output_path: str = ""
        while True:
            output_path = (
                input(
                    "\033[92m"
                    + "Enter the directory to save the PDF file(default is current directory): "
                    + "\033[0m"
                )
                or os.getcwd()
            )

            if validate_path(output_path):
                break
            else:
                print(
                    "\033[91m" + f"{output_path} is not a valid directory." + "\033[0m"
                )

        output_name: str = (
            input(
                "\033[92m"
                + "Enter the name of the PDF file(default is 'output'): "
                + "\033[0m"
            )
            or "output"
        )

        if len(file_list) == 0:
            print("\033[91m" + "No images found." + "\033[0m")
        else:
            print("\033[92m" + "Converting images to PDF..." + "\033[0m")
            convert_images_to_pdf(file_list, output_path, output_name)

    except KeyboardInterrupt:
        print("\033[92m" + "Exiting..." + "\033[0m")


if __name__ == "__main__":
    main()
