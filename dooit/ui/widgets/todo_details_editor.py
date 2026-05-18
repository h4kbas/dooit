from typing import Callable, Optional

from textual.binding import Binding
from textual.widgets import TextArea

from dooit.api import Todo
from dooit.ui.api.events import ModeChanged
from dooit.utils.editor import edit_in_external_editor


class TodoDetailsEditor(TextArea):
    BINDINGS = [
        Binding("escape", "escape_key", "Exit", show=True, priority=True),
        Binding("s", "save_and_close", "Save", show=True),
        Binding("i", "enter_insert", "Insert", show=True),
        Binding("a", "enter_insert_after", "Append", show=True),
        Binding(
            "ctrl+e",
            "open_in_editor",
            "Open in $EDITOR",
            show=True,
            priority=True,
        ),
        Binding("j", "vim_down", show=False),
        Binding("k", "vim_up", show=False),
        Binding("h", "vim_left", show=False),
        Binding("l", "vim_right", show=False),
        Binding("w", "vim_word_forward", show=False),
        Binding("b", "vim_word_backward", show=False),
        Binding("0", "vim_line_start", show=False),
        Binding("$", "vim_line_end", show=False),
        Binding("G", "vim_document_end", show=False),
        Binding("x", "vim_delete_char", show=False),
        Binding("d,d", "vim_delete_line", show=False),
    ]

    _NORMAL_ONLY_ACTIONS = frozenset(
        {
            "save_and_close",
            "enter_insert",
            "enter_insert_after",
            "vim_down",
            "vim_up",
            "vim_left",
            "vim_right",
            "vim_word_forward",
            "vim_word_backward",
            "vim_line_start",
            "vim_line_end",
            "vim_document_end",
            "vim_delete_char",
            "vim_delete_line",
        }
    )

    def __init__(self) -> None:
        super().__init__(id="todo_details_editor", show_cursor=True)
        self._editing = False
        self._insert_mode = False
        self._todo: Optional[Todo] = None
        self.can_focus = False
        self.read_only = True

    @property
    def is_editing(self) -> bool:
        return self._editing

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if not self._editing:
            return False
        if action in self._NORMAL_ONLY_ACTIONS:
            return not self._insert_mode
        return True

    def sync_visibility(self) -> None:
        if self._editing or self.text.strip():
            self.add_class("-visible")
        else:
            self.remove_class("-visible")

    def show_preview(self, details: str) -> None:
        if self._editing:
            return
        self.text = details
        self.border_title = "Details" if details.strip() else ""
        self.sync_visibility()

    def begin_edit(self, todo: Todo) -> None:
        self._todo = todo
        self._editing = True
        self.can_focus = True
        self.text = todo.details or ""
        self.add_class("-visible")
        self._set_insert_mode(False)
        self.focus()

    def stop_editing(self, *, save: bool) -> None:
        if not self._editing or self._todo is None:
            return

        todo = self._todo
        if save:
            todo.details = self.text
            todo.save()
        else:
            self.text = todo.details or ""

        self._editing = False
        self._insert_mode = False
        self._todo = None
        self.can_focus = False
        self.read_only = True
        self.border_title = "Details" if self.text.strip() else ""
        self.sync_visibility()
        self.app.post_message(ModeChanged("NORMAL"))

        from .trees.todos_tree import TodosTree

        panel = self.parent
        if panel is not None:
            tree = panel.query(TodosTree).first()
            if tree is not None:
                tree.focus()
                tree.force_refresh()

    def _set_insert_mode(self, insert: bool) -> None:
        self._insert_mode = insert
        self.read_only = not insert
        self.border_title = "Details" + (" [INSERT]" if insert else " [NORMAL]")
        self.app.post_message(ModeChanged("INSERT" if insert else "NORMAL"))

    def _vim(self, action: Callable[[TextArea], None]) -> None:
        if self._insert_mode:
            return
        action(self)

    def _vim_edit(self, action: Callable[[TextArea], None]) -> None:
        if self._insert_mode:
            return
        was_ro = self.read_only
        self.read_only = False
        action(self)
        self.read_only = was_ro

    def action_escape_key(self) -> None:
        if self._insert_mode:
            self._set_insert_mode(False)
            self.focus()
            return
        self.stop_editing(save=False)

    def action_save_and_close(self) -> None:
        self.stop_editing(save=True)

    def action_enter_insert(self) -> None:
        if self._insert_mode:
            return
        self._set_insert_mode(True)
        self.focus()

    def action_enter_insert_after(self) -> None:
        if self._insert_mode:
            return
        self._vim(lambda ta: ta.action_cursor_right())
        self._set_insert_mode(True)
        self.focus()

    def action_open_in_editor(self) -> None:
        with self.app.suspend():
            self.text = edit_in_external_editor(self.text)
        if not self._insert_mode:
            self.read_only = True
        self.focus()

    def action_vim_down(self) -> None:
        self._vim(lambda ta: ta.action_cursor_down())

    def action_vim_up(self) -> None:
        self._vim(lambda ta: ta.action_cursor_up())

    def action_vim_left(self) -> None:
        self._vim(lambda ta: ta.action_cursor_left())

    def action_vim_right(self) -> None:
        self._vim(lambda ta: ta.action_cursor_right())

    def action_vim_word_forward(self) -> None:
        self._vim(lambda ta: ta.action_cursor_word_right())

    def action_vim_word_backward(self) -> None:
        self._vim(lambda ta: ta.action_cursor_word_left())

    def action_vim_line_start(self) -> None:
        self._vim(lambda ta: ta.action_cursor_line_start())

    def action_vim_line_end(self) -> None:
        self._vim(lambda ta: ta.action_cursor_line_end())

    def action_vim_document_end(self) -> None:
        def go(ta: TextArea) -> None:
            last = ta.document.line_count - 1
            col = len(ta.document[last])
            ta.move_cursor((last, col))

        self._vim(go)

    def action_vim_delete_char(self) -> None:
        self._vim_edit(lambda ta: ta.action_delete_right())

    def action_vim_delete_line(self) -> None:
        self._vim_edit(lambda ta: ta.action_delete_line())
