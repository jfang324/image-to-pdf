from textual.app import App, ComposeResult
from textual.widgets import Footer
from .state import AppState
from textual.reactive import reactive
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, DirectoryTree
from .widgets.directory_explorer import DirectoryExplorer
from textual import on


class ImageToPDFApp(App):
    """The core Textual application class for managing the UI and state of the image to PDF converter."""

    DEFAULT_CSS = """
        Vertical {
            height: 100%;
            width: 1fr;
        }
    """

    state = reactive(AppState())

    def compose(self) -> ComposeResult:

        with Horizontal():
            with Vertical():
                yield DirectoryExplorer(
                    directory_path=self.state.input_directory_path,
                    title="Input Directory",
                    id="input_directory",
                )
                yield DirectoryExplorer(
                    directory_path=self.state.input_directory_path,
                    title="Output Directory",
                    id="output_directory",
                )
            with Vertical():
                yield Static()
            with Vertical():
                yield Static()

        yield Footer()

    @on(DirectoryExplorer.DirectoryChanged, "#input_directory")
    def on_input_directory_changed(
        self, event: DirectoryExplorer.DirectoryChanged
    ) -> None:
        self.notify(f"Input directory changed: {event.new_directory}")

    @on(DirectoryExplorer.DirectoryChanged, "#output_directory")
    def on_output_directory_changed(
        self, event: DirectoryExplorer.DirectoryChanged
    ) -> None:
        self.notify(f"Output directory changed: {event.new_directory}")
