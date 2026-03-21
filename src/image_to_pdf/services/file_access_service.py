import os
from io import BytesIO

from PIL import Image


def is_image(file_path: str) -> bool:
    """
    Checks if a file is an image

    :param file_path: The path to the file
    :return: True if the file is an image, False otherwise
    """

    if not os.path.isfile(file_path):
        return False
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False


def scan_directory(
    directory: str, current_selected_files: list[str]
) -> list[tuple[str, str, bool]]:
    """
    Scan a directory for image files.

    :param directory: The directory path to scan
    :param current_selected_files: List of currently selected file paths
    :return: List of (filename, full_path, is_selected) tuples for each image
    """
    contents = os.listdir(directory)
    selected_set = set(current_selected_files)
    results = []

    for path in contents:
        if path.startswith("."):
            continue
        full_path = os.path.join(directory, path)
        if not is_image(full_path):
            continue
        results.append((path, full_path, full_path in selected_set))

    return results


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
    :raises ValueError: If image_list is empty, output_path is invalid, output_name is empty, or none of the files could be converted
    """

    if not image_list:
        raise ValueError("image_list cannot be empty")

    if not output_path or not os.path.isdir(output_path):
        raise ValueError(f"output_path must be a valid directory: {output_path}")

    if not output_name or not output_name.strip():
        raise ValueError("output_name cannot be empty")

    full_output_path = f"{os.path.join(output_path, output_name)}.pdf"

    if os.path.exists(full_output_path):
        raise ValueError(f"{output_name}.pdf already exists in {output_path}")

    images: list[Image.Image] = []
    buffers: list[BytesIO] = []

    try:
        for image in image_list:
            if is_image(image):
                # Normalize the image by converting it to RGB and to PNG format for lossless embedding
                with Image.open(image) as img:
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")

                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    buffer.seek(0)
                    buffers.append(buffer)
                    images.append(Image.open(buffer))

        if not images:
            raise ValueError("None of the selected files could be converted to images")

        images[0].save(
            full_output_path,
            quality=quality,
            optimize=optimize,
            save_all=True,
            append_images=images[1:],
        )
    finally:
        for img in images:
            img.close()
        for buf in buffers:
            buf.close()
