import imghdr
import os
from io import BytesIO

from PIL import Image


def is_image(file_path: str) -> bool:
    """
    Checks if a file is an image

    :param file_path: The path to the file
    :return: True if the file is an image, False otherwise
    """

    return (
        os.path.exists(file_path)
        and os.path.isfile(file_path)
        and imghdr.what(file_path) is not None
    )


def get_image_list(dir_path: str) -> list[str]:
    """
    Get a list of image files in a directory

    :param dir_path: The path to the directory
    :return: A list of all images in the directory
    :raises FileNotFoundError: If the directory does not exist
    :raises NotADirectoryError: If the path is not a directory
    :raises PermissionError: If the directory cannot be accessed
    """

    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"The directory {dir_path} does not exist")

    if not os.path.isdir(dir_path):
        raise NotADirectoryError(f"{dir_path} is not a directory")

    try:
        path_list: list[str] = os.listdir(dir_path)
    except PermissionError:
        raise PermissionError(f"Permission denied to access directory: {dir_path}")

    image_list: list[str] = []

    for path in path_list:
        full_path: str = os.path.join(dir_path, path)

        if is_image(full_path):
            image_list.append(full_path)

    return image_list


def validate_directory(dir_path: str) -> bool:
    """
    Validates if a path is a valid directory

    :param dir_path: The path to be validated
    :return: True if the path is a valid directory, False otherwise
    """

    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        return True
    else:
        return False


def convert_images_to_pdf(
    image_list: list[str],
    output_path: str,
    output_name: str,
    quality: int = 75,
    optimize: bool = False,
) -> None:
    """
    Converts a list of images to a PDF file

    :param image_list: A list of image files to be converted
    :param output_path: The path to the output directory
    :param output_name: The name of the output PDF file
    :param quality: PDF quality (1-100, default: 75)
    :param optimize: Whether to optimize PDF file size (default: False)
    :raises ValueError: If image_list is empty, output_path is invalid, or output_name is empty
    """

    if not image_list:
        raise ValueError("image_list cannot be empty")

    if not output_path or not os.path.isdir(output_path):
        raise ValueError(f"output_path must be a valid directory: {output_path}")

    if not output_name or not output_name.strip():
        raise ValueError("output_name cannot be empty")

    images: list[Image.Image] = []

    for image in image_list:
        if is_image(image):
            img: Image.Image = Image.open(image)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            images.append(Image.open(buffer))

    if images and os.path.exists(output_path):
        images[0].save(
            f"{os.path.join(output_path, output_name)}.pdf",
            quality=quality,
            optimize=optimize,
            save_all=True,
            append_images=images[1:],
        )
