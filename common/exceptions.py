# common/exceptions.py

class BaseAIError(Exception):
    """Base class for all custom AI-related errors."""
    pass


# ---------- YouTube RAG ----------
class RAGException(BaseAIError):
    """General RAG pipeline error."""
    pass

class TranscriptNotFoundError(RAGException):
    """Raised when transcript is missing for a YouTube video."""
    pass

class InvalidYouTubeURLError(RAGException):
    """Raised when the provided YouTube URL is invalid."""
    pass

class OpenAIError(RAGException):
    """Raised when an OpenAI API call fails."""
    pass


# ---------- NetZero Advisor ----------
class NetZeroError(BaseAIError):
    """General NetZero Advisor project error."""
    pass


# ---------- Research Agent ----------
class ResearchAgentError(BaseAIError):
    """General Research Agent error."""
    pass


# ---------- Chat With Code ----------
class ChatWithCodeError(BaseAIError):
    """General ChatWithCode project error."""
    pass


# ---------- AI Knowledge Tutor ----------
class TutorAgentError(BaseAIError):
    """General AI Knowledge Tutor error."""
    pass


# ---------- Legal Document Analyzer ----------
class LegalDocError(BaseAIError):
    """General Legal Document Analyzer error."""
    pass