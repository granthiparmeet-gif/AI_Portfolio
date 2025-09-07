import os
from langsmith import Client

def get_langsmith_client() -> Client:
    """
    Returns a LangSmith client if environment variables are set.
    Requires:
      - LANGSMITH_API_KEY
      - (Optional) LANGSMITH_ENDPOINT
    """
    api_key = os.getenv("LANGSMITH_API_KEY")
    endpoint = os.getenv("LANGSMITH_ENDPOINT")  # defaults to https://api.smith.langchain.com

    if not api_key:
        raise RuntimeError("LANGSMITH_API_KEY not set in environment.")

    client = Client(api_key=api_key, api_url=endpoint)
    return client

def trace_event(event_name: str, metadata: dict = None):
    """
    Records a custom trace event in LangSmith.
    """
    client = get_langsmith_client()
    client.create_event(
        name=event_name,
        metadata=metadata or {},
    )