from enum import Enum
from typing import List


class WorkspaceWidget(Enum):
    description = "description"


class TodoWidget(Enum):
    description = "description"
    due = "due"
    created_at = "created_at"
    completed_at = "completed_at"
    urgency = "urgency"
    recurrence = "recurrence"
    status = "status"
    effort = "effort"


WorkspaceLayout = List[WorkspaceWidget]
TodoLayout = List[TodoWidget]
