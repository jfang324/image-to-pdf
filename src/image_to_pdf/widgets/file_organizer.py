import os

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView


class FileOrganizer(Widget):
    """
    A FileOrganizer widget that allows the user to select and organize files.

    Attributes:
        title (str): The title to be displayed in the widget border

    Reactive Attributes:
        file_list (list[str]): A list of full paths for the currently selected files
    """

    DEFAULT_CSS = """
        FileOrganizer {
            border: solid $primary;
            height: 1fr;
        }

        FileOrganizer ListView {
            height: 100%;
            margin: 0 1;
            padding: 1;
        }

        FileOrganizer ListView > ListItem.selected-for-swap {
            background: $primary-darken-2;
            color: $text;
        }
    """

    file_list: reactive[list[str]] = reactive([], init=False)

    # A set of indices for the currently selected items in the list view
    _selected_swap_indices: reactive[set[int]] = reactive(set)

    class SwapRequest(Message):
        """
        Message to request 2 selected items in the file_list to be swapped

        Attributes:
            index_1 (int): The index of the first item to swap
            index_2 (int): The index of the second item to swap
            control (Widget): A reference to the FileOrganizer widget
        """

        @property
        def control(self) -> Widget:
            """Required for @on decorator selector matching."""
            return self._control

        def __init__(self, index_1: int, index_2: int, control: Widget) -> None:
            """
            Initializes the SwapRequest message

            Args:
                index_1 (int): The index of the first item to swap
                index_2 (int): The index of the second item to swap
                control (Widget): A reference to the FileOrganizer widget
            """
            super().__init__()

            self.index_1 = index_1
            self.index_2 = index_2
            self._control = control

    def __init__(self, title: str = "File Organizer", **kwargs) -> None:
        """
        Initializes the FileOrganizer widget

        Args:
            title (str): The title to be displayed in the widget border. Defaults to "File Organizer".
        """
        super().__init__(**kwargs)

        self.border_title = title

    def compose(self) -> ComposeResult:
        with Vertical():
            yield ListView(id="file_list")

    def _build_list_view(self) -> None:
        """Builds the list view with the current file_list"""
        list_view = self.query_one("#file_list", ListView)
        list_items = [ListItem(Label(os.path.basename(path))) for path in self.file_list]

        list_view.clear()
        list_view.extend(list_items)

        self._selected_swap_indices = set()

    def watch_file_list(self) -> None:
        """Watches the file_list reactive attribute and rebuilds the list view when it changes"""
        self._build_list_view()

    def watch__selected_swap_indices(self) -> None:
        """Update visual styling for selected items"""
        if not self.is_mounted:
            return

        list_view: ListView = self.query_one("#file_list", ListView)

        for i, child in enumerate(list_view.children):
            if i in self._selected_swap_indices:
                child.add_class("selected-for-swap")
            else:
                child.remove_class("selected-for-swap")

    @on(ListView.Selected)
    def _signal_selected_items_swap(self, event: ListView.Selected) -> None:
        """Toggle selection; when 2 selected, emit swap message"""
        index = event.index

        if index not in self._selected_swap_indices:
            self._selected_swap_indices = self._selected_swap_indices | {index}

        if len(self._selected_swap_indices) == 2:
            index_1, index_2 = self._selected_swap_indices

            self.post_message(self.SwapRequest(index_1, index_2, self))
            self._selected_swap_indices = set()
