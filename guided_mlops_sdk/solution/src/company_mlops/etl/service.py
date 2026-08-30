from .executors import ETLExecutor
from .models import MaterializationResult
from .plan import FeaturePlan


class ETLService:
    def materialize(
        self,
        plan: FeaturePlan,
        *,
        executor: ETLExecutor,
    ) -> MaterializationResult:
        return executor.execute(plan)

