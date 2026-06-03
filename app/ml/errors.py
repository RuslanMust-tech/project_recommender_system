"""Custom exceptions for ML module."""


class MLError(Exception):
    """Base exception for ML operations."""
    pass


class ModelLoadError(MLError):
    """Raised when model cannot be loaded."""
    pass


class PredictionError(MLError):
    """Raised when prediction fails."""
    pass


class InvalidInputError(MLError):
    """Raised when input data is invalid."""
    pass
