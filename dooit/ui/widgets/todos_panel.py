from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static

from dooit.api import Workspace
from dooit.ui.api.events import TodoDetailsChanged, TodoSelected
from .trees.todos_tree import TodosTree


class TodosPanel(Container):
    DEFAULT_CSS = """
    TodosPanel {
        layout: vertical;
        height: 1fr;
    }

    TodosPanel > TodosTree {
        height: 1fr;
        min-height: 3;
    }

    TodosPanel > #todo_details_preview {
        height: auto;
        max-height: 12;
        min-height: 0;
        display: none;
        border: tall $background3;
        border-title-color: $foreground1;
        border-title-background: $background3;
        padding: 0 1;
        overflow-y: auto;
    }

    TodosPanel > #todo_details_preview.-visible {
        display: block;
    }
    """

    def __init__(self, workspace: Workspace) -> None:
        super().__init__(id=f"TodosPanel_{workspace.uuid}")
        self._workspace = workspace

    def compose(self) -> ComposeResult:
        yield TodosTree(self._workspace)
        yield Static("", id="todo_details_preview")

    def refresh_details_preview(self) -> None:
        tree = self.query_one(TodosTree)
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
        tree = self.query_one(TodosTree)
        if tree.highlighted is not None and tree.current_model.uuid == event.todo.uuid:
            self.refresh_details_preview()
        tree.force_refresh()
