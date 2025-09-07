class ExcelVizException(Exception):
    """Base class for Excel Viz-related errors."""


class InvalidExcelError(ExcelVizException):
    """Raised when the uploaded Excel is invalid or empty."""


class SpecValidationError(ExcelVizException):
    """Raised when the generated chart spec is invalid for the data."""