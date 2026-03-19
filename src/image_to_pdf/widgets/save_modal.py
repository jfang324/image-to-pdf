from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, Label
from textual.containers import Vertical
from textual.reactive import reactive
from typing import Union


class SaveModal(ModalScreen[Union[str, None]]):
    """A modal form that prompts users for a save name"""

    DEFAULT_CSS = """
        SaveModal {
            align: center middle;
        }

        #dialog {
            width: 50;
            height: 15;
            border: solid $primary;
            padding: 1 2;
        }

        #title {
            text-style: bold;
            color: $primary;
            margin-bottom: 1;
        }

        #subtitle {
            color: $text-muted;
            margin-bottom: 1;
        }

        Input {
            width: 100%;
            border: solid $primary;
        }
    """

    BINDINGS = [
        ("escape", "cancel_request", "cancel"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Save PDF", id="title")
            yield Label("Enter a file name:", id="subtitle")
            yield Input(placeholder="e.g. class_final_report", id="input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    def action_cancel_request(self) -> None:
        self.app.pop_screen()
