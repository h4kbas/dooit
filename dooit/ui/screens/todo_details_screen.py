from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static, TextArea

from dooit.api import Todo


class TodoDetailsScreen(ModalScreen[bool]):
    DEFAULT_CSS = """
    TodoDetailsScreen {
        align: center middle;
    }

    #details-dialog {
        width: 90%;
        max-width: 100;
        height: 80%;
        max-height: 28;
        border: heavy $primary;
        background: $background2;
        padding: 0 1;
    }

    #details-hint {
        height: 1;
        color: $foreground1;
        text-style: italic;
    }

    #details-ta {
        height: 1fr;
        border: none;
    }
    """

    BINDINGS = [
        Binding("escape", "save_and_close", "Save", show=True, priority=True),
    ]

    def __init__(self, todo_id: str) -> None:
        super().__init__()
        self.todo_id = todo_id

    def compose(self) -> ComposeResult:
        with Vertical(id="details-dialog"):
            yield Static(
                "escape: save and close  |  enter: new line",
                id="details-hint",
            )
            yield TextArea(id="details-ta")

    def on_mount(self) -> None:
        todo = Todo.from_id(self.todo_id)
        ta = self.query_one("#details-ta", TextArea)
        ta.text = todo.details or ""
        ta.border_title = "details"
        ta.focus()

    def action_save_and_close(self) -> None:
        ta = self.query_one("#details-ta", TextArea)
        todo = Todo.from_id(self.todo_id)
        todo.details = ta.text
        todo.save()
        self.dismiss(True)
