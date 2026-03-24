import os
from io import BytesIO

from PIL import Image


def is_image(file_path: str) -> bool:
    """
    Checks if a file is an image.

    Args:
        file_path (str): The path to the file

    Returns:
        bool: True if the file is an image, False otherwise
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
    directory_path: str, current_selected_files: list[str]
) -> list[tuple[str, str, bool]]:
    """
    Scan a directory for image files.

    Args:
        directory_path (str): The path to the directory to scan
        current_selected_files (list[str]): A list of currently selected file paths

    Returns:
        list[tuple[str, str, bool]]: A list of tuples containing the filename, full path, and whether the files is contained in the current_selected_files list

    Raises:
        ValueError: If directory_path is not a directory
    """
    if not os.path.isdir(directory_path):
        raise ValueError(f"directory_path must be a valid directory: {directory_path}")

    contents = os.listdir(directory_path)
    selected_set = set(current_selected_files)
    results = []

    for path in contents:
        if path.startswith("."):
            continue

        full_path = os.path.join(directory_path, path)

        if not is_image(full_path):
            continue

        results.append((path, full_path, full_path in selected_set))

    return results


def convert_images_to_pdf(
    image_paths: list[str],
    output_path: str,
    output_name: str,
    quality: int = 75,
    optimize: bool = False,
) -> str:
    """
    Converts a list of images to a PDF file

    Args:
        image_paths (list[str]): A list of image file paths to be converted
        output_path (str): The path to the output directory
        output_name (str): The name of the output PDF file
        quality (int, optional): PDF quality (1-100, default: 75). Defaults to 75.
        optimize (bool, optional): Whether to optimize PDF file size (default: False). Defaults to False.

    Returns:
        str: The full path to the output PDF file

    Raises:
        ValueError: If any of the following conditions are met:
            - image_paths is empty
            - output_path is not a valid directory
            - output_name is empty
            - quality is not between 1 and 100
            - output_path + output_name + ".pdf" already exists
            - any of the image_paths fail to open
    """
    if not image_paths:
        raise ValueError("image_paths cannot be empty")

    if not output_path or not os.path.isdir(output_path):
        raise ValueError(f"output_path must be a valid directory: {output_path}")

    if not output_name or not output_name.strip():
        raise ValueError("output_name cannot be empty")

    if quality < 1 or quality > 100:
        raise ValueError("quality must be between 1 and 100")

    full_output_path = f"{os.path.join(output_path, output_name)}.pdf"

    if os.path.exists(full_output_path):
        raise ValueError(f"{output_name}.pdf already exists in {output_path}")

    images: list[Image.Image] = []
    buffers: list[BytesIO] = []

    try:
        for image_path in image_paths:
            if not is_image(image_path):
                continue

            try:
                # Normalize the image by converting it to RGB and to PNG format for lossless embedding
                with Image.open(image_path) as img:
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")

                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    buffer.seek(0)
                    buffers.append(buffer)
                    images.append(Image.open(buffer))
            except Exception as e:
                raise ValueError(f"Failed to open image: {image_path}") from e

        if not images:
            raise ValueError("None of the selected files could be converted to images")

        images[0].save(
            full_output_path,
            quality=quality,
            optimize=optimize,
            save_all=True,
            append_images=images[1:],
        )

        return full_output_path
    finally:
        for img in images:
            img.close()
        for buf in buffers:
            buf.close()
