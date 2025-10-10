from __future__ import annotations

from typing import ContextManager, Protocol, runtime_checkable


@runtime_checkable
class SuspendableApp(Protocol):
    """Protocol for apps that support suspending to run external programs."""

    def suspend(self) -> ContextManager[None]: ...


class DescriptionEditor(Protocol):
    """Protocol for services that edit task descriptions."""

    async def edit(
        self,
        app: SuspendableApp,
        initial_text: str,
    ) -> str | None: ...
