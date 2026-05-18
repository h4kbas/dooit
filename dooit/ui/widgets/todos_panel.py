from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static

from dooit.api import Workspace
from dooit.ui.api.events import TodoDetailsChanged, TodoSelected
from .trees.todos_tree import TodosTree


class TodosPanel(Container):
    def __init__(self, workspace: Workspace) -> None:
        super().__init__(id=f"TodosPanel_{workspace.uuid}")
        self._workspace = workspace

    def compose(self) -> ComposeResult:
        yield TodosTree(self._workspace)
        yield Static("", id="todo_details_preview")

    def on_mount(self) -> None:
        self.call_after_refresh(self.refresh_details_preview)

    def refresh_details_preview(self) -> None:
        if not self.is_mounted:
            return

        tree = self.query(TodosTree).first()
        if tree is None:
            return

        preview = self.query_one("#todo_details_preview", Static)
        if tree.highlighted is None:
            preview.update("")
            preview.remove_class("-visible")
            preview.border_title = ""
            return

        todo = tree.current_model
        details = (todo.details or "").strip()
        if not details:
            preview.update("")
            preview.remove_class("-visible")
            preview.border_title = ""
            return

        preview.border_title = "details"
        preview.update(details)
        preview.add_class("-visible")

    @on(TodoSelected)
    def on_todo_selected(self, event: TodoSelected) -> None:
        event.stop()
        self.refresh_details_preview()

    @on(TodoDetailsChanged)
    def on_details_changed(self, event: TodoDetailsChanged) -> None:
        event.stop()
        tree = self.query(TodosTree).first()
        if tree is None:
            return

        if tree.highlighted is not None and tree.current_model.uuid == event.todo.uuid:
            self.refresh_details_preview()
        tree.force_refresh()
