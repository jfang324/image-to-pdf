import os
from PIL import Image


def get_file_list(path: str) -> list[str]:
    """
    Get a list of all files in a directory.

    :param path: The path to the directory.
    :return: A list of all files in the directory.
    """
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"The directory {path} does not exist.")

        if os.path.isfile(path):
            raise Exception(f"{path} is not a directory.")

        everything_list: list[str] = os.listdir(path)
        file_list: list[str] = []

        for item in everything_list:
            if os.path.isfile(os.path.join(path, item)) and item.endswith(
                (".png", ".jpg", ".jpeg")
            ):
                file_list.append(os.path.join(path, item))

        return file_list
    except Exception as e:
        print(e)
        return []


def validate_path(path: str) -> bool:
    """
    Validates if a path is a valid directory.

    :param path: The path to be validated.
    :return: True if the path is a valid directory, False otherwise.
    """
    if os.path.exists(path) and os.path.isdir(path):
        return True
    else:
        return False


def convert_images_to_pdf(
    file_list: list[str], output_path: str, output_name: str
) -> None:
    """
    Converts a list of images to a PDF file.

    :param file_list: A list of image files to be converted.
    :param output_path: The path to the output directory.
    :param output_name: The name of the output PDF file.
    """
    images: Image.Image = [
        Image.open(file)
        for file in file_list
        if os.path.exists(file) and os.path.isfile(file)
    ]
    images[0].save(
        os.path.join(output_path, output_name + ".pdf"),
        "PDF",
        resolution=100.0,
        save_all=True,
        append_images=images[1:],
    )
