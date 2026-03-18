"""File organizer widget for reordering selected files via swap."""

import os
from typing import Set

from textual.widgets import ListView, ListItem, Label
from textual.containers import Vertical
from textual.reactive import reactive
from textual.message import Message
from textual.widget import Widget
from textual.app import ComposeResult


class FileListItem(ListItem):
    """ListItem that displays a filename but stores the full file path.

    Attributes:
        file_path: The complete path to the file.
    """

    def __init__(self, display_text: str, file_path: str) -> None:
        super().__init__(Label(display_text))
        self.file_path = file_path


class FileOrganizer(Widget):
    """Widget that allows users to swap positions of files in a list.

    Users can select two items to swap their positions. Selected items
    are visually highlighted until the swap is completed.
    """

    DEFAULT_CSS = """
        FileOrganizer {
            border: solid $primary;
            height: 1fr;
        }

        FileOrganizer ListView {
            height: 100%;
            margin-left: 1;
            margin-right: 1;
            padding: 1;
        }

        FileOrganizer ListView > ListItem.selected-for-swap {
            background: $primary-darken-2;
            color: $text;
        }
    """

    file_list: reactive[list[str]] = reactive([], init=False)
    """List of file paths to display in the organizer."""

    _selected_swap_indices: reactive[Set[int]] = reactive(set)
    """Set of indices currently selected for a swap operation."""

    class SwapRequest(Message):
        """Emitted when two items are selected to be swapped.

        Attributes:
            index1: The index of the first item to swap.
            index2: The index of the second item to swap.
            control: The FileOrganizer widget that sent this message.
        """

        @property
        def control(self) -> Widget:
            """Required for @on decorator selector matching."""
            return self._control

        def __init__(self, index1: int, index2: int, control: Widget) -> None:
            if index1 == index2:
                raise ValueError("Cannot swap an item with itself")
            self.index1 = index1
            self.index2 = index2
            self._control = control
            super().__init__()

    def __init__(self, title: str = "File Organizer", **kwargs):
        super().__init__(**kwargs)
        self.border_title = title

    def compose(self) -> ComposeResult:
        with Vertical():
            yield ListView(id="file_list")

    def on_mount(self) -> None:
        if self.file_list:
            self._build_list_view()

    def _build_list_view(self) -> None:
        list_view = self.query_one("#file_list", ListView)
        list_items = [
            FileListItem(self._get_display_name(path), path) for path in self.file_list
        ]
        list_view.clear()
        list_view.extend(list_items)
        self._selected_swap_indices = set()

    def _get_display_name(self, path: str) -> str:
        """Extract filename from path for display.

        Args:
            path: Full file path.

        Returns:
            The base filename, or the original path if basename fails.
        """
        try:
            return os.path.basename(path) or path
        except (TypeError, ValueError):
            return path

    def watch_file_list(self) -> None:
        if not self.is_mounted:
            return

        self._build_list_view()

    def watch__selected_swap_indices(self) -> None:
        """Update visual styling for selected items."""
        if not self.is_mounted:
            return
        list_view = self.query_one("#file_list", ListView)
        for i, child in enumerate(list_view.children):
            if i in self._selected_swap_indices:
                child.add_class("selected-for-swap")
            else:
                child.remove_class("selected-for-swap")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Toggle selection; when 2 selected, emit swap message."""
        index = event.index

        if index in self._selected_swap_indices:
            new_set = self._selected_swap_indices.copy()
            new_set.discard(index)
            self._selected_swap_indices = new_set
        else:
            self._selected_swap_indices = self._selected_swap_indices | {index}

        if len(self._selected_swap_indices) == 2:
            idx1, idx2 = self._selected_swap_indices
            self.post_message(self.SwapRequest(idx1, idx2, self))
            self._selected_swap_indices = set()
