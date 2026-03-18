from textual.app import App, ComposeResult
from textual.widgets import Footer, Static
from textual.reactive import reactive
from textual.containers import Horizontal, Vertical
from .widgets.directory_explorer import DirectoryExplorer
from textual import on
from .widgets.file_selector import FileSelector
import os
from .widgets.file_organizer import FileOrganizer


class ImageToPDFApp(App):
    """The core Textual application class for managing the UI and state of the image to PDF converter."""

    DEFAULT_CSS = """
        Vertical {
            height: 100%;
            width: 1fr;
        }
    """

    input_directory = reactive("")
    output_directory = reactive("")
    input_directory_files: reactive[list[str]] = reactive([])
    current_selected_files: reactive[list[str]] = reactive([])

    def compose(self) -> ComposeResult:

        with Horizontal():
            with Vertical():
                yield DirectoryExplorer(
                    directory_path=self.input_directory,
                    title="Input Directory",
                    id="input_directory",
                )
                yield DirectoryExplorer(
                    directory_path=self.output_directory,
                    title="Output Directory",
                    id="output_directory",
                )
            with Vertical():
                yield FileSelector(
                    current_directory=self.input_directory,
                    id="image_selector",
                ).data_bind(
                    file_list=ImageToPDFApp.input_directory_files,
                    current_directory=ImageToPDFApp.input_directory,
                )
            with Vertical(id="image_organizer"):
                yield FileOrganizer(id="file_organizer").data_bind(
                    file_list=ImageToPDFApp.current_selected_files
                )

        yield Footer()

    def on_mount(self) -> None:
        """Initialize on app startup."""
        cwd = os.getcwd()
        self.input_directory = cwd
        self.output_directory = cwd
        self.input_directory_files = self.scan_directory(cwd)
        self.current_selected_files = []

        # Initialize DirectoryExplorers with the current directory
        self.query_one("#input_directory", DirectoryExplorer).current_directory = cwd
        self.query_one("#output_directory", DirectoryExplorer).current_directory = cwd

    def scan_directory(self, directory: str) -> list[tuple[str, str, bool]]:
        """Scan the input directory and return a list of (name, path, selected)."""
        try:
            directory_contents = os.listdir(directory)
            current_selected_files = set(self.current_selected_files)

            return [
                (
                    path,
                    os.path.join(directory, path),
                    os.path.join(directory, path) in current_selected_files,
                )
                for path in directory_contents
                if not path.startswith(".")
                and os.path.isfile(os.path.join(directory, path))
            ]
        except OSError:
            self.notify("Failed to scan directory")
            return []

    @on(DirectoryExplorer.DirectoryChanged, "#input_directory")
    def on_input_directory_changed(
        self, event: DirectoryExplorer.DirectoryChanged
    ) -> None:
        self.input_directory_files = self.scan_directory(event.new_directory)
        self.input_directory = event.new_directory
        # self.query_one("#input_directory", DirectoryExplorer).border_subtitle = (
        #     event.new_directory
        # )
        self.mutate_reactive(ImageToPDFApp.input_directory_files)

    @on(DirectoryExplorer.DirectoryChanged, "#output_directory")
    def on_output_directory_changed(
        self, event: DirectoryExplorer.DirectoryChanged
    ) -> None:
        self.output_directory = event.new_directory

    @on(FileSelector.SelectionChanged, "#image_selector")
    def on_image_selector_selection_changed(
        self, event: FileSelector.SelectionChanged
    ) -> None:
        selected_files = event.selected_files
        deselected_files = event.deselected_files
        current_selected_files = set(self.current_selected_files)

        for file in selected_files:
            if file not in current_selected_files:
                self.current_selected_files.append(file)

        for file in deselected_files:
            index = self.current_selected_files.index(file)
            del self.current_selected_files[index]

        self.mutate_reactive(ImageToPDFApp.current_selected_files)

        # self.notify(f"selected_images: {selected_files}")
        # self.notify(f"deselected_images: {deselected_files}")
        # self.notify(f"current_images: {self.current_selected_files}")

    @on(FileOrganizer.SwapRequest, "#file_organizer")
    def on_file_organizer_swap(self, event: FileOrganizer.SwapRequest) -> None:
        """Swap files at the given indices."""
        files = list(self.current_selected_files)
        files[event.index1], files[event.index2] = (
            files[event.index2],
            files[event.index1],
        )
        self.current_selected_files = files
