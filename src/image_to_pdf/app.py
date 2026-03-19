from textual.app import App, ComposeResult
from textual.widgets import Footer, Static
from textual.reactive import reactive
from textual.containers import Horizontal, Vertical
from .widgets.directory_explorer import DirectoryExplorer
from textual import on
from .widgets.file_selector import FileSelector
import os
from .widgets.file_organizer import FileOrganizer
from .widgets.save_modal import SaveModal
from .services.file_access_service import is_image, convert_images_to_pdf
from textual import work
import time
from dataclasses import dataclass
from typing import Union


@dataclass
class PDFConfig:
    quality: int = 75
    optimize: bool = False


class ImageToPDFApp(App):
    """The core Textual application class for top level event handling

    Attributes:
    """

    DEFAULT_CSS = """
        Vertical {
            height: 100%;
            width: 1fr;
        }
    """

    BINDINGS = [("ctrl+s", "request_save", "Save file")]

    input_directory = reactive("")
    output_directory = reactive("")
    input_directory_files: reactive[list[tuple[str, str, bool]]] = reactive([])
    current_selected_files: reactive[list[str]] = reactive([])

    def __init__(self, quality: int = 75, optimize: bool = False) -> None:
        super().__init__()
        self.config = PDFConfig(quality=quality, optimize=optimize)

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
                yield FileOrganizer().data_bind(
                    file_list=ImageToPDFApp.current_selected_files
                )
        yield Footer()

    @work(thread=True)
    def _handle_save_request(self, output_file_name: str = "output") -> None:
        try:
            start_time = time.perf_counter_ns()

            convert_images_to_pdf(
                self.current_selected_files,
                self.output_directory,
                output_file_name,
                quality=self.config.quality,
                optimize=self.config.optimize,
            )

            elapsed_time = (time.perf_counter_ns() - start_time) / (10**9)

            self.call_from_thread(
                self.notify,
                f"{output_file_name}.pdf saved to {self.output_directory} ({elapsed_time:.2f}s)",
            )
        except (OSError, ValueError) as e:
            self.call_from_thread(
                self.notify, message=f"Failed to save PDF: {e}", severity="error"
            )
            self.log.error("PDF conversion failed", exception=e)

    def action_request_save(self) -> None:
        self.push_screen(SaveModal(), self._on_save_modal_close)

    def _on_save_modal_close(self, output_file_name: Union[str, None]) -> None:
        if output_file_name is None:
            return

        self._handle_save_request(output_file_name)
        self.notify("Job started, you will be notified on completion")

    def on_mount(self) -> None:
        """Initialize on app startup"""
        cwd = os.getcwd()
        self.input_directory = cwd
        self.output_directory = cwd

    def scan_directory(self, directory: str) -> list[tuple[str, str, bool]]:
        """Scan the input directory and return a list of (name, path, selected)"""
        try:
            directory_contents = os.listdir(directory)
            current_selected_files_set = set(self.current_selected_files)
            results = []

            for path in directory_contents:
                if path.startswith("."):
                    continue

                full_path = os.path.join(directory, path)
                if not is_image(full_path):
                    continue

                results.append(
                    (path, full_path, full_path in current_selected_files_set)
                )

            return results
        except OSError:
            self.notify(message="Failed to scan directory", severity="error")
            return []

    def watch_input_directory(self) -> None:
        if not self.input_directory:
            return

        new_input_directory_files = self.scan_directory(self.input_directory)
        self.input_directory_files = new_input_directory_files

    @on(DirectoryExplorer.DirectoryChanged, "#input_directory")
    def on_input_directory_changed(
        self, event: DirectoryExplorer.DirectoryChanged
    ) -> None:
        self.input_directory = event.new_directory

    @on(DirectoryExplorer.DirectoryChanged, "#output_directory")
    def on_output_directory_changed(
        self, event: DirectoryExplorer.DirectoryChanged
    ) -> None:
        self.output_directory = event.new_directory

    @on(FileSelector.SelectionChanged)
    def on_image_selector_selection_changed(
        self, event: FileSelector.SelectionChanged
    ) -> None:
        selected_files = event.selected_files
        deselected_files = set(event.deselected_files)

        new_current_selected_files = [
            file for file in self.current_selected_files if file not in deselected_files
        ]

        new_current_selected_files_set = set(new_current_selected_files)

        new_current_selected_files.extend(
            [
                file
                for file in selected_files
                if file not in new_current_selected_files_set
            ]
        )

        self.current_selected_files = new_current_selected_files

    @on(FileOrganizer.SwapRequest)
    def on_file_organizer_swap(self, event: FileOrganizer.SwapRequest) -> None:
        new_current_selected_files = list(self.current_selected_files)

        (
            new_current_selected_files[event.index_1],
            new_current_selected_files[event.index_2],
        ) = (
            new_current_selected_files[event.index_2],
            new_current_selected_files[event.index_1],
        )

        self.current_selected_files = new_current_selected_files
