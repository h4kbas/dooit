import os
from typing import Optional

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from ._vars import DATABASE_FILE


def _ensure_todo_timestamp_columns(engine) -> None:
    insp = inspect(engine)
    if not insp.has_table("todo"):
        return

    cols = {c["name"] for c in insp.get_columns("todo")}

    with engine.begin() as conn:
        if "created_at" not in cols:
            conn.execute(text("ALTER TABLE todo ADD COLUMN created_at DATETIME"))
            conn.execute(
                text(
                    "UPDATE todo SET created_at = CURRENT_TIMESTAMP "
                    "WHERE created_at IS NULL"
                )
            )
        if "completed_at" not in cols:
            conn.execute(text("ALTER TABLE todo ADD COLUMN completed_at DATETIME"))


class Manager:
    """
    Class for managing sqlalchemy sessions
    """

    def connect(self, path: Optional[str] = None):
        """
        Connect to database using a file path

        Args:
            path: Path to SQLite database file. Can include ~ for home directory.
        """

        from dooit.api import BaseModel

        path = path or DATABASE_FILE
        path = os.path.expanduser(path)
        connection_string = f"sqlite:///{path}"
        self.engine = create_engine(connection_string)
        self.session = Session(self.engine)

        BaseModel.metadata.create_all(bind=self.engine)
        _ensure_todo_timestamp_columns(self.engine)
        self._db_last_modified = self._get_db_last_modified()

    def _get_db_last_modified(self) -> Optional[float]:
        database = self.engine.url.database
        assert database is not None

        try:
            return os.path.getmtime(database)
        except OSError:
            return None

    def has_changed(self) -> bool:
        current_last_modified = self._get_db_last_modified()
        if current_last_modified and self._db_last_modified != current_last_modified:
            self._db_last_modified = current_last_modified
            manager.session.expire_all()
            return True
        return False

    def delete(self, obj):
        self.session.delete(obj)
        self.commit()

    def save(self, obj):
        self.session.add(obj)
        self.commit()

    def commit(self):
        self.session.commit()
        self._db_last_modified = self._get_db_last_modified()


manager = Manager()
