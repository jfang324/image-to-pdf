import os
import time
from dataclasses import dataclass
from typing import Union

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Footer

from .services.file_access_service import convert_images_to_pdf, scan_directory
from .widgets import DirectoryExplorer, FileOrganizer, FileSelector, SaveModal


@dataclass
class PDFConfig:
    """
    A data container for PDF configuration options

    Attributes:
        quality (int): An integer ranging from 1 to 100 that determines how much quality is preserved in the PDF generation
        optimize (bool): Whether or not an effort will be made to compress the final PDF
    """

    quality: int
    optimize: bool

    def __init__(self, quality: int = 75, optimize: bool = False) -> None:
        if quality < 1 or quality > 100:
            raise ValueError("quality must be between 1 and 100")

        self.quality = quality
        self.optimize = optimize


class ImageToPDFApp(App):
    """
    The core Textual application class for top level event handling

    Attributes:
        quality (int): An integer ranging from 1 to 100 that determines how much quality is preserved in the PDF generation
        optimize (bool): Whether or not an effort will be made to compress the final PDF

    Reactive Attributes:
        input_directory (str): The path to the input directory
        output_directory (str): The path to the output directory
        input_directory_files (list[tuple[str, str, bool]]): A list of tuples that represent files in the input directory in the format (display_name, path, selected)
        current_selected_files (list[str]): A list of paths for the currently selected files
    """

    DEFAULT_CSS = """
        Vertical {
            height: 100%;
            width: 1fr;
        }
    """

    BINDINGS = [("ctrl+s", "request_save", "Save file")]

    input_directory: reactive[str] = reactive("")
    output_directory: reactive[str] = reactive("")
    input_directory_files: reactive[list[tuple[str, str, bool]]] = reactive([])
    current_selected_files: reactive[list[str]] = reactive([])

    def __init__(self, quality: int = 75, optimize: bool = False) -> None:
        super().__init__()
        self.config = PDFConfig(quality=quality, optimize=optimize)

        cwd = os.getcwd()
        self.input_directory = cwd
        self.output_directory = cwd

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical():
                yield DirectoryExplorer(
                    title="Input Directory",
                    id="input_directory",
                ).data_bind(current_directory=ImageToPDFApp.input_directory)
                yield DirectoryExplorer(
                    title="Output Directory",
                    id="output_directory",
                ).data_bind(current_directory=ImageToPDFApp.output_directory)
            with Vertical():
                yield FileSelector(
                    title="Image Selector",
                ).data_bind(
                    current_directory=ImageToPDFApp.input_directory,
                    file_list=ImageToPDFApp.input_directory_files,
                )
            with Vertical():
                yield FileOrganizer().data_bind(file_list=ImageToPDFApp.current_selected_files)
        yield Footer()

    @work(thread=True)
    def _handle_save_request(
        self,
        current_selected_files: list[str],
        output_directory: str,
        output_file_name: str,
        quality: int,
        optimize: bool,
    ) -> None:
        """Handles the save request on a separate thread and notifies the user of the result"""
        try:
            start_time = time.perf_counter_ns()

            convert_images_to_pdf(
                current_selected_files,
                output_directory,
                output_file_name,
                quality,
                optimize,
            )

            elapsed_time = (time.perf_counter_ns() - start_time) / (10**9)

            self.call_from_thread(
                self.notify,
                f"{output_file_name}.pdf saved to {output_directory} ({elapsed_time:.2f}s)",
            )
        except (OSError, ValueError, PermissionError, FileNotFoundError) as e:
            self.call_from_thread(self.notify, message=f"Failed to save PDF: {e}", severity="error")
            self.log.error("PDF conversion failed", exception=e)

    def action_request_save(self) -> None:
        """Opens the save modal"""
        self.push_screen(SaveModal(), self._on_save_modal_close)

    def _on_save_modal_close(self, output_file_name: Union[str, None]) -> None:
        """Captures user input from the save model and forwards it to the worker"""
        if output_file_name is None:
            return

        if not self.current_selected_files:
            self.notify(
                "No files selected - please select at least one image.",
                severity="error",
            )
            return

        self._handle_save_request(
            self.current_selected_files,
            self.output_directory,
            output_file_name,
            self.config.quality,
            self.config.optimize,
        )
        self.notify("Job started, you will be notified on completion")

    def scan_directory(self, directory: str) -> list[tuple[str, str, bool]]:
        """Scan the input directory and return a list of (name, path, selected)"""
        try:
            return scan_directory(directory, self.current_selected_files)
        except (OSError, ValueError) as e:
            self.notify(message=f"Failed to scan directory: {e}", severity="error")
            return []

    def watch_input_directory(self) -> None:
        """Update the input directory files when the input directory changes"""
        if not self.input_directory:
            return

        new_input_directory_files = self.scan_directory(self.input_directory)
        self.input_directory_files = new_input_directory_files

    @on(DirectoryExplorer.DirectoryChanged, "#input_directory")
    def on_input_directory_changed(self, event: DirectoryExplorer.DirectoryChanged) -> None:
        """Update the input directory when the input directory explorer changes"""
        self.input_directory = event.new_directory

    @on(DirectoryExplorer.DirectoryChanged, "#output_directory")
    def on_output_directory_changed(self, event: DirectoryExplorer.DirectoryChanged) -> None:
        """Update the output directory when the output directory explorer changes"""
        self.output_directory = event.new_directory

    @on(FileSelector.SelectionChanged)
    def _updated_current_selected_files(self, event: FileSelector.SelectionChanged) -> None:
        """Update the current selected files when the image selector selection changes"""
        selected_files = event.selected_files
        deselected_files = set(event.deselected_files)

        new_current_selected_files = [
            file for file in self.current_selected_files if file not in deselected_files
        ]

        new_current_selected_files_set = set(new_current_selected_files)

        new_current_selected_files.extend(
            [file for file in selected_files if file not in new_current_selected_files_set]
        )

        self.current_selected_files = new_current_selected_files

    @on(FileOrganizer.SwapRequest)
    def _handle_file_reorder(self, event: FileOrganizer.SwapRequest) -> None:
        """Swaps the selected items in current_selected_files"""
        new_current_selected_files = list(self.current_selected_files)

        (
            new_current_selected_files[event.index_1],
            new_current_selected_files[event.index_2],
        ) = (
            new_current_selected_files[event.index_2],
            new_current_selected_files[event.index_1],
        )

        self.current_selected_files = new_current_selected_files
