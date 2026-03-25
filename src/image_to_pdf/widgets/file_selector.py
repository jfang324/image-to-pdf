from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import SelectionList
from textual.widgets.selection_list import Selection


class FileSelector(Widget):
    """
    A FileSelector widget that allows the user to select files from a directory.

    Attributes:
        title (str): The title to be displayed in the widget border

    Reactive Attributes:
        current_directory (str): The directory path that this widget will source files from
        file_list (list[tuple[str, str, bool]]): A list of tuples that represent files in the directory in the format (display_name, path, selected)
    """

    DEFAULT_CSS = """
        FileSelector {
            border: solid $primary;
            height: 1fr;
        }

        FileSelector SelectionList {
            height: 100%;
        }
    """

    current_directory: reactive[str] = reactive("")
    file_list: reactive[list[tuple[str, str, bool]]] = reactive([])

    class SelectionChanged(Message):
        """
        Message to indicate that the selection list has changed

        Attributes:
            selected_files (list[str]): A list of paths for the currently selected files
            deselected_files (list[str]): A list of paths for the files that were de-selected
            control (Widget): A reference to the FileSelector widget
        """

        @property
        def control(self) -> Widget:
            """Required for @on decorator selector matching"""
            return self._control

        def __init__(
            self,
            selected_files: list[str],
            deselected_files: list[str],
            control: Widget,
        ) -> None:
            """
            Initializes the SelectionChanged message

            Args:
                selected_files (list[str]): A list of paths for the currently selected files
                deselected_files (list[str]): A list of paths for the files that were de-selected
                control (Widget): A reference to the FileSelector widget
            """
            super().__init__()

            self.selected_files = selected_files
            self.deselected_files = deselected_files
            self._control = control

    def __init__(
        self,
        title: str = "File Selector",
        **kwargs,
    ) -> None:
        """
        Initializes the FileSelector widget

        Args:
            title (str): The title to be displayed in the widget border. Defaults to "File Selector".
        """
        super().__init__(**kwargs)

        self.border_title = title
        self._previous_selection: set[str] = set()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield SelectionList[str](id="file_list")

    def _build_selection_list(self) -> None:
        """Builds the SelectionList with the current file_list"""
        selection_list = self.query_one("#file_list", SelectionList)
        selections = [Selection(name, path, selected) for name, path, selected in self.file_list]

        selection_list.clear_options()
        selection_list.add_options(selections)

    def watch_current_directory(self) -> None:
        """Update the SelectionList if current_directory changes (this would change the files available)"""
        if self._is_mounted:
            self._build_selection_list()

        self._previous_selection = set()

    @on(SelectionList.SelectedChanged)
    def _signal_selection_changed(self, event: SelectionList.SelectedChanged) -> None:
        """Signals parent widget that the selection list has changed"""
        selected_files: list[str] = event.selection_list.selected
        deselected: list[str] = list(self._previous_selection - set(selected_files))

        self._previous_selection = set(selected_files)
        self.post_message(self.SelectionChanged(selected_files, deselected, self))
