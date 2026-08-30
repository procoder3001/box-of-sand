"""Public ETL use cases remain independent of Spark and Beam imports."""

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
        """Delegate execution strategy without provider conditionals."""
        raise NotImplementedError

