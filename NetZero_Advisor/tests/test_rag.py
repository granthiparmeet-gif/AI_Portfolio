from NetZero_Advisor.rag import build_retriever_from_text

def test_retriever_builds():
    r = build_retriever_from_text("This is a short PDF text chunk.")
    assert r is not None