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
    """A custom DirectoryTree widget that filters out files and hidden directories."""

    def filter_paths(self, paths: Iterable[Path]) -> list[Path]:
        """Return only directories that are not hidden."""
        return [p for p in paths if not p.name.startswith(".") and p.is_dir()]


class DirectoryExplorer(Widget):
    """A widget that allows users to explore directories."""

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

    current_directory = reactive(".", init=False)

    class DirectoryChanged(Message):
        """Message posted when the user navigates to a different directory."""

        @property
        def control(self) -> Widget:
            """Required for @on decorator selector matching."""
            return self._control

        def __init__(self, new_directory: str, control: Widget) -> None:
            super().__init__()
            self.new_directory = new_directory
            self._control = control

    def __init__(
        self, directory_path: str = ".", title: str = "Directory Explorer", **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.border_title = title
        self.border_subtitle = directory_path
        self.current_directory = directory_path

    def compose(self) -> ComposeResult:
        with Vertical():
            yield FilteredDirectoryTree(self.current_directory, id="directory_tree")

    def watch_current_directory(self, new_directory: str) -> None:
        self.border_subtitle = new_directory
        if self.is_mounted:
            self._reload_tree(new_directory)
            self.post_message(self.DirectoryChanged(new_directory, self))

    def _reload_tree(self, new_directory: str) -> None:
        try:
            tree = self.query_one("#directory_tree", FilteredDirectoryTree)
            tree.root.collapse()
            tree.path = new_directory
            tree.reload()
        except Exception as e:
            self.notify(f"Failed to reload directory: {e}")

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        self.current_directory = str(event.path)

    @on(events.Key)
    def on_key(self, event: events.Key) -> None:
        if event.key != "escape":
            return

        parent = Path(self.current_directory).parent
        if parent != Path(self.current_directory):
            self.current_directory = str(parent)

        event.stop()
