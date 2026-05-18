import os
import shlex
import subprocess
import tempfile
from pathlib import Path


def edit_in_external_editor(content: str) -> str:
    editor_cmd = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vi"
    editor = shlex.split(editor_cmd)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        path = Path(f.name)

    try:
        subprocess.call([*editor, str(path)])
        return path.read_text(encoding="utf-8")
    finally:
        path.unlink(missing_ok=True)
