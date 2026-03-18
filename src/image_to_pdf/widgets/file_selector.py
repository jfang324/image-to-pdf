from textual.widgets import SelectionList
from textual.widget import Widget
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets.selection_list import Selection
from textual.message import Message


class FileSelector(Widget):
    """A widget that allows users to select from a list of files."""

    DEFAULT_CSS = """
        FileSelector {
            border: solid $primary;
            height: 1fr;
        }
        
        FileSelector SelectionList {
            height: 100%;
        }
    """

    file_list: reactive[list[tuple[str, str, bool]]] = reactive([], init=False)
    current_directory: reactive[str] = reactive("")

    class SelectionChanged(Message):
        """Message posted when the user changes their selection."""

        @property
        def control(self) -> Widget:
            """Required for @on decorator selector matching."""
            return self._control

        def __init__(
            self,
            selected_files: list[str],
            deselected_files: list[str],
            control: Widget,
        ) -> None:
            super().__init__()
            self.selected_files = selected_files
            self.deselected_files = deselected_files
            self._control = control

    def __init__(
        self,
        file_list: list[tuple[str, str, bool]] | None = None,
        current_directory: str = "",
        title: str = "File Selector",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.border_title = title
        if file_list is not None:
            self.file_list = file_list
        self.current_directory = current_directory
        self._previous_selection = set()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield SelectionList[str](id="file_list")

    def _build_selection_list(self) -> None:
        """Build the SelectionList from file_list."""
        selection_list = self.query_one("#file_list", SelectionList)
        selections = [
            Selection(name, path, selected) for name, path, selected in self.file_list
        ]
        selection_list.clear_options()
        selection_list.add_options(selections)

    def on_mount(self) -> None:
        """Populate SelectionList on initial mount."""
        if self.file_list:
            self._build_selection_list()

    def watch_file_list(self, file_list: list[tuple[str, str, bool]]) -> None:
        """Update the SelectionList when file_list changes via data_bind."""
        if not self.is_mounted:
            return
        self._previous_selection = {path for _, path, selected in file_list if selected}
        self._build_selection_list()

    def on_selection_list_selected_changed(
        self, event: SelectionList.SelectedChanged
    ) -> None:
        selected_files = event.selection_list.selected
        current_set = set(selected_files)

        # Skip if selection hasn't actually changed
        if current_set == self._previous_selection:
            return

        deselected = self._previous_selection - current_set
        self._previous_selection = current_set
        self.post_message(self.SelectionChanged(selected_files, list(deselected), self))
