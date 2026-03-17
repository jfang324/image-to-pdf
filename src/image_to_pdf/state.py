import os


class AppState:
    """Global state for the application.

    This class holds the global state for the application such as:
    - The input directory path
    - The output directory path
    - The list of images to be processed
    """

    def __init__(self) -> None:
        current_directory: str = os.getcwd()

        self.input_directory_path: str = current_directory
        self.output_directory_path: str = current_directory

        current_image_list: list[str] = [
            os.path.join(current_directory, f)
            for f in os.listdir(current_directory)
            if os.path.isfile(os.path.join(current_directory, f))
        ]

        self.image_list: list[str] = current_image_list
