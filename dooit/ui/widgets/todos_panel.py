from textual import on
from textual.app import ComposeResult
from textual.containers import Container

from dooit.api import Workspace
from dooit.ui.api.events import TodoDetailsChanged, TodoSelected
from .todo_details_editor import TodoDetailsEditor
from .trees.todos_tree import TodosTree


class TodosPanel(Container):
    def __init__(self, workspace: Workspace) -> None:
        super().__init__(id=f"TodosPanel_{workspace.uuid}")
        self._workspace = workspace

    def compose(self) -> ComposeResult:
        yield TodosTree(self._workspace)
        yield TodoDetailsEditor()

    def on_mount(self) -> None:
        self.call_after_refresh(self.refresh_details_preview)

    def _editor(self) -> TodoDetailsEditor:
        return self.query_one(TodoDetailsEditor)

    def start_editing_details(self) -> None:
        tree = self.query(TodosTree).first()
        if tree is None or tree.highlighted is None:
            return

        self._editor().begin_edit(tree.current_model)

    def refresh_details_preview(self) -> None:
        if not self.is_mounted:
            return

        editor = self._editor()
        if editor.is_editing:
            return

        tree = self.query(TodosTree).first()
        if tree is None:
            return

        if tree.highlighted is None:
            editor.show_preview("")
            return

        details = (tree.current_model.details or "").strip()
        editor.show_preview(details)

    @on(TodoSelected)
    def on_todo_selected(self, event: TodoSelected) -> None:
        event.stop()
        editor = self._editor()
        if editor.is_editing:
            editor.stop_editing(save=False)
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
