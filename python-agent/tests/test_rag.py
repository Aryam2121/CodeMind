"""
Tests for RAG pipeline
"""
import pytest
from unittest.mock import Mock, patch

from rag import RAGPipeline, MockLLM
from models import Source


@pytest.fixture
def mock_vector_store():
    """Mock vector store"""
    with patch('rag.get_vector_store') as mock:
        store = Mock()
        mock.return_value = store
        yield store


@pytest.fixture
def rag_pipeline(mock_vector_store):
    """Create RAG pipeline with mock"""
    with patch.dict('os.environ', {'USE_MOCK_LLM': 'true'}):
        pipeline = RAGPipeline()
        return pipeline


@pytest.mark.asyncio
async def test_query_with_results(rag_pipeline, mock_vector_store):
    """Test query with document results"""
    from langchain.schema import Document
    
    # Mock retrieval
    mock_docs = [
        (Document(
            page_content="Water quality must meet WHO standards.",
            metadata={"source": "policy.pdf", "page": 1, "doc_id": "doc1"}
        ), 0.1),
        (Document(
            page_content="Testing required daily.",
            metadata={"source": "policy.pdf", "page": 2, "doc_id": "doc2"}
        ), 0.2)
    ]
    mock_vector_store.similarity_search_with_score.return_value = mock_docs
    
    response = await rag_pipeline.query("What are water quality standards?")
    
    assert response.answer != ""
    assert len(response.sources) == 2
    assert response.sources[0].title == "policy.pdf"
    assert response.confidence > 0


@pytest.mark.asyncio
async def test_query_no_results(rag_pipeline, mock_vector_store):
    """Test query with no documents found"""
    mock_vector_store.similarity_search_with_score.return_value = []
    
    response = await rag_pipeline.query("Random query")
    
    assert "No relevant documents" in response.answer
    assert len(response.sources) == 0
    assert response.fallback is True


def test_mock_llm():
    """Test mock LLM responses"""
    llm = MockLLM()
    
    # Test pothole query
    response = llm.generate("How to fix potholes?", "")
    assert "pothole" in response.lower() or "repair" in response.lower()
    
    # Test water query
    response = llm.generate("Water quality standards?", "")
    assert "water" in response.lower() or "quality" in response.lower()


def test_calculate_confidence(rag_pipeline):
    """Test confidence calculation"""
    # Low scores (high distance) = low confidence
    confidence = rag_pipeline._calculate_confidence([1.5, 1.8])
    assert confidence < 0.5
    
    # High scores (low distance) = high confidence
    confidence = rag_pipeline._calculate_confidence([0.1, 0.2])
    assert confidence > 0.8
