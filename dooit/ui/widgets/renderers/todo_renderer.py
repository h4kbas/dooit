from ..inputs.model_inputs import (
    CompletedAt,
    CreatedAt,
    Due,
    Effort,
    Recurrence,
    Status,
    TodoDescription,
    Urgency,
)
from .base_renderer import BaseRenderer, Todo


class TodoRender(BaseRenderer[Todo]):
    @property
    def model(self) -> Todo:
        return self._model

    def matches_filter(self, filter: str) -> bool:
        if filter in self.model.description:
            return True

        return filter in (self.model.details or "")

    def post_init(self):
        self.description = TodoDescription(self.model)
        self.due = Due(self.model)
        self.created_at = CreatedAt(self.model)
        self.completed_at = CompletedAt(self.model)
        self.status = Status(self.model)
        self.urgency = Urgency(self.model)
        self.effort = Effort(self.model)
        self.recurrence = Recurrence(self.model)
