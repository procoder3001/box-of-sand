"""Lesson 4: stable, package-owned errors."""


class MLOpsError(Exception):
    """Base exception callers may intentionally catch."""


class ConfigurationError(MLOpsError):
    pass


class TrackingError(MLOpsError):
    pass


class RunNotFoundError(TrackingError):
    pass


class MLOpsTimeoutError(MLOpsError):
    pass

