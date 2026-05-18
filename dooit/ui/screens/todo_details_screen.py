from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static, TextArea

from dooit.api import Todo
from dooit.utils.editor import edit_in_external_editor


class TodoDetailsScreen(ModalScreen[bool]):
    BINDINGS = [
        Binding("escape", "save_and_close", "Save", show=True, priority=True),
        Binding(
            "ctrl+e",
            "open_in_editor",
            "Open in $EDITOR",
            show=True,
            priority=True,
        ),
    ]

    def __init__(self, todo_id: str) -> None:
        super().__init__()
        self.todo_id = todo_id

    def compose(self) -> ComposeResult:
        with Vertical(id="details-dialog"):
            yield Static(
                "escape: save  |  ctrl+e: $EDITOR  |  enter: new line",
                id="details-hint",
            )
            yield TextArea(id="details-ta")

    def on_mount(self) -> None:
        todo = Todo.from_id(self.todo_id)
        ta = self.query_one("#details-ta", TextArea)
        ta.text = todo.details or ""
        ta.border_title = "details"
        ta.focus()

    def action_open_in_editor(self) -> None:
        ta = self.query_one("#details-ta", TextArea)
        with self.app.suspend():
            ta.text = edit_in_external_editor(ta.text)
        ta.focus()

    def action_save_and_close(self) -> None:
        ta = self.query_one("#details-ta", TextArea)
        todo = Todo.from_id(self.todo_id)
        todo.details = ta.text
        todo.save()
        self.dismiss(True)
