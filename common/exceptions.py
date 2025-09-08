# common/exceptions.py

class BaseAIError(Exception):
    """Base class for AI-related errors."""
    pass


# ----------------- YouTube RAG -----------------
class RAGException(BaseAIError):
    """Base class for RAG-related errors."""
    pass


class TranscriptNotFoundError(RAGException):
    """Raised when no transcript is available for the YouTube video."""
    pass


class InvalidYouTubeURLError(RAGException):
    """Raised when the provided YouTube URL is invalid."""
    pass


class OpenAIError(RAGException):
    """Raised when an OpenAI API error occurs."""
    pass


# ----------------- NetZero Advisor -----------------
class NetZeroError(BaseAIError):
    """Raised when NetZero Advisor fails to generate a roadmap."""
    pass


# ----------------- Research Agent -----------------
class ResearchError(BaseAIError):
    """Raised when Research Agent fails to complete task."""
    pass


# ----------------- Legal Doc Analyzer -----------------
class ContractParseError(BaseAIError):
    """Raised when PDF contract cannot be parsed."""
    pass


class ContractAnalysisError(BaseAIError):
    """Raised when LLM fails to analyze a contract."""
    pass