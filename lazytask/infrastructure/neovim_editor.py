from __future__ import annotations

import logging
import os
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable, Sequence

from lazytask.application.errors import DescriptionEditorError
from lazytask.application.ports.editor import DescriptionEditor, SuspendableApp


class NeovimDescriptionEditor(DescriptionEditor):
    """Edit task descriptions using Neovim."""

    def __init__(self, command: str | Sequence[str] | None = None) -> None:
        self._command_source = command or os.environ.get(
            "LAZYTASK_NVIM_COMMAND", "nvim"
        )

    async def edit(
        self,
        app: SuspendableApp,
        initial_text: str,
    ) -> str | None:
        command = self._resolve_command()
        if not command:
            raise DescriptionEditorError("Neovim command is empty.")

        temporary_directory = Path(tempfile.mkdtemp(prefix="lazytask_desc_"))
        temporary_file_path = temporary_directory / "description.md"

        try:
            temporary_file_path.write_text(initial_text, encoding="utf-8")
        except OSError as error:
            raise DescriptionEditorError(
                f"Failed to prepare temporary file for editing: {error}"
            ) from error

        try:
            edited_text = self._invoke_editor(app, command, temporary_file_path)
        except DescriptionEditorError:
            raise
        except FileNotFoundError as error:
            raise DescriptionEditorError(
                f"Neovim executable '{command[0]}' not found."
            ) from error
        except subprocess.SubprocessError as error:
            raise DescriptionEditorError(
                f"Neovim exited unexpectedly: {error}"
            ) from error
        except Exception as error:  # pragma: no cover - defensive
            logging.exception("Unexpected error while launching Neovim")
            raise DescriptionEditorError(
                f"Unexpected error while running Neovim: {error}"
            ) from error
        finally:
            self._cleanup_file(temporary_directory)

        return edited_text

    def _invoke_editor(
        self,
        app: SuspendableApp,
        command: Sequence[str],
        file_path: Path,
    ) -> str:
        full_command = (*command, str(file_path))
        with app.suspend():
            completed = subprocess.run(full_command, check=False)
        if completed.returncode not in (0, None):
            raise DescriptionEditorError(
                f"Neovim exited with status {completed.returncode}."
            )
        try:
            return file_path.read_text(encoding="utf-8")
        except OSError as error:
            raise DescriptionEditorError(
                f"Failed to read edited description: {error}"
            ) from error

    def _resolve_command(self) -> Sequence[str]:
        if isinstance(self._command_source, str):
            return tuple(shlex.split(self._command_source))
        return tuple(self._command_source)

    @staticmethod
    def _cleanup_file(directory: Path) -> None:
        try:
            for path in _iter_directory_entries(directory):
                path.unlink(missing_ok=True)
            directory.rmdir()
        except OSError as error:
            logging.debug("Failed to clean up temporary editor files: %s", error)


def _iter_directory_entries(directory: Path) -> Iterable[Path]:
    try:
        yield from directory.iterdir()
    except FileNotFoundError:
        return
