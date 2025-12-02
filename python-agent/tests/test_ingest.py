"""
Tests for document ingestion functionality
"""
import pytest
import tempfile
from pathlib import Path
from io import BytesIO

from ingest import DocumentIngester
from models import DocumentMetadata


@pytest.fixture
def ingester():
    """Create ingester instance"""
    return DocumentIngester()


@pytest.fixture
def sample_text_file():
    """Create a sample text file"""
    content = b"""
    Smart City Policy Document
    
    Section 1: Water Management
    All water quality must meet WHO standards.
    Testing is required daily for pH and chlorine levels.
    
    Section 2: Road Maintenance
    Potholes must be repaired within 7 business days.
    """
    return BytesIO(content), "policy.txt"


@pytest.mark.asyncio
async def test_ingest_text_file(ingester, sample_text_file):
    """Test ingesting a text file"""
    file_obj, filename = sample_text_file
    
    metadata = DocumentMetadata(
        source_name="Test Policy",
        uploaded_by="test_user"
    )
    
    response = await ingester.ingest_file(file_obj, filename, metadata)
    
    assert response.status == "ok"
    assert response.ingested > 0
    assert len(response.ids) == response.ingested
    assert response.metadata["source"] == filename


def test_text_splitter(ingester):
    """Test text chunking"""
    text = "This is a test. " * 100  # Long text
    chunks = ingester.text_splitter.split_text(text)
    
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 1200  # chunk_size + some buffer


@pytest.mark.asyncio
async def test_ingest_empty_file(ingester):
    """Test handling of empty file"""
    empty_file = BytesIO(b"")
    
    with pytest.raises(ValueError, match="No text extracted"):
        await ingester.ingest_file(empty_file, "empty.txt", None)


def test_extract_text_unsupported_format(ingester):
    """Test unsupported file format"""
    fake_file = BytesIO(b"binary data")
    
    with pytest.raises(ValueError, match="Unsupported file type"):
        ingester._extract_text(fake_file, "file.exe")
