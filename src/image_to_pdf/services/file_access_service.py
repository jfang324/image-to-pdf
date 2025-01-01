import os
import imghdr
from PIL import Image
import tempfile


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
    """

    try:
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"The directory {dir_path} does not exist")

        if not os.path.isdir(dir_path):
            raise NotADirectoryError(f"{dir_path} is not a directory")

        path_list: list[str] = os.listdir(dir_path)
        image_list: list[str] = []

        for path in path_list:
            full_path: str = os.path.join(dir_path, path)

            if is_image(full_path):
                image_list.append(full_path)

        return image_list
    except Exception as e:
        print(e)
        return []


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
    image_list: list[str], output_path: str, output_name: str
) -> None:
    """
    Converts a list of images to a PDF file

    :param image_list: A list of image files to be converted
    :param output_path: The path to the output directory
    :param output_name: The name of the output PDF file
    """

    with tempfile.TemporaryDirectory() as temp_dir:
        images: list[Image.Image] = []

        for image in image_list:
            if is_image(image):
                img: Image.Image = Image.open(image)
                png_path = f"{os.path.join(temp_dir, image.split(os.path.sep)[-1].split('.')[0])}.png"
                img.save(
                    png_path,
                    format="PNG",
                    optimize=True,
                )

                images.append(Image.open(png_path))

        if len(images) > 0 and os.path.exists(output_path):
            images[0].save(
                f"{os.path.join(output_path, output_name)}.pdf",
                quality=100,
                save_all=True,
                append_images=images[1:],
                optimize=True,
            )
