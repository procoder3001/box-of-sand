class MLOpsError(Exception):
    pass


class ConfigurationError(MLOpsError):
    pass


class TrackingError(MLOpsError):
    pass


class RunNotFoundError(TrackingError):
    pass


class MLOpsTimeoutError(MLOpsError):
    pass

