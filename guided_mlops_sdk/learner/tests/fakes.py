import asyncio
from collections.abc import Mapping


class FakeMLflowBackend:
    def __init__(self, *, delay: float = 0) -> None:
        self.delay = delay
        self.events: list[tuple[object, ...]] = []
        self.active = 0
        self.max_active = 0
        self.closed = False

    def create_experiment(self, name: str) -> str:
        self.events.append(("create_experiment", name))
        return "exp-1"

    def get_run(self, run_id: str) -> Mapping[str, object]:
        self.events.append(("get_run", run_id))
        return {"run_id": run_id, "experiment_id": "exp-1", "status": "FINISHED"}

    def start_run(self, experiment_id: str, name: str) -> str:
        self.events.append(("start_run", experiment_id, name))
        return "run-1"

    def end_run(self, run_id: str, status: str) -> None:
        self.events.append(("end_run", run_id, status))

    async def get_run_async(self, run_id: str) -> Mapping[str, object]:
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        try:
            await asyncio.sleep(self.delay)
            return {"run_id": run_id, "experiment_id": "exp-1", "status": "FINISHED"}
        finally:
            self.active -= 1

    async def aclose(self) -> None:
        self.closed = True

