from collections.abc import Iterable
from pathlib import Path

from textual import events, on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import DirectoryTree


class FilteredDirectoryTree(DirectoryTree):
    """A custom DirectoryTree widget that filters out files and hidden directories"""

    def filter_paths(self, paths: Iterable[Path]) -> list[Path]:
        return [p for p in paths if not p.name.startswith(".") and p.is_dir()]


class DirectoryExplorer(Widget):
    """
    A DirectoryExplorer widget that allows the user to navigate through directories and select files.

    Attributes:
        title (str): The title to be displayed in the widget border

    Reactive Attributes:
        current_directory (str): The directory path that will act as the root of the directory explorer
    """

    DEFAULT_CSS = """
        DirectoryExplorer {
            border: solid $primary;
            height: 1fr;
        }

        DirectoryExplorer DirectoryTree {
            margin-left: 1;
            margin-right: 1;
        }
    """

    current_directory: reactive[str] = reactive(".")

    class DirectoryChanged(Message):
        """
        Message to indicate that the current directory has changed

        Attributes:
            new_directory (str): The path of the new root directory
            control (Widget): A reference to the widget sending the message
        """

        @property
        def control(self) -> Widget:
            """Required for @on decorator selector matching"""
            return self._control

        def __init__(self, new_directory: str, control: Widget) -> None:
            super().__init__()
            self.new_directory = new_directory
            self._control = control

    def __init__(self, title: str = "Directory Explorer", **kwargs) -> None:
        super().__init__(**kwargs)
        self.border_title = title

    def compose(self) -> ComposeResult:
        with Vertical():
            yield FilteredDirectoryTree(self.current_directory, id="directory_tree")

    def _reload_directory_tree(self, new_directory: str) -> None:
        """Reloads the directory tree with the new directory"""
        self.border_subtitle = new_directory

        if self._is_mounted:
            directory_tree = self.query_one("#directory_tree", FilteredDirectoryTree)

            directory_tree.path = new_directory
            directory_tree.root.collapse()

    def watch_current_directory(self) -> None:
        """Watches the current_directory reactive attribute and reloads the directory tree when it changes"""
        self._reload_directory_tree(self.current_directory)

    @on(DirectoryTree.DirectorySelected)
    def _signal_navigate_to_child_directory(self, event: DirectoryTree.DirectorySelected) -> None:
        """Signals parent widget that the current directory has changed to a child directory"""
        new_directory = str(event.path)

        self.post_message(self.DirectoryChanged(new_directory, self))

    @on(events.Key)
    def _signal_navigate_to_parent_directory(self, event: events.Key) -> None:
        """Signals parent widget that the current directory has changed to the parent directory"""
        if event.key != "escape":
            return

        parent = Path(self.current_directory).parent

        if parent != Path(self.current_directory):
            self.post_message(self.DirectoryChanged(str(parent), self))
