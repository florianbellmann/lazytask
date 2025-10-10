from __future__ import annotations

from lazytask.application.ports.editor import SuspendableApp


class StubDescriptionEditor:
    def __init__(self) -> None:
        self.calls: list[tuple[SuspendableApp, str]] = []
        self.next_response: str | None = None

    async def edit(self, app: SuspendableApp, initial_text: str) -> str | None:
        self.calls.append((app, initial_text))
        return self.next_response
