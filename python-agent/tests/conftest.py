"""
Pytest configuration and fixtures
"""
import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment
os.environ["USE_MOCK_LLM"] = "true"
os.environ["CHROMA_DB_DIR"] = "./test_chroma_db"


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment"""
    # Ensure mock mode
    os.environ["USE_MOCK_LLM"] = "true"
    
    yield
    
    # Cleanup
    import shutil
    test_db = Path("./test_chroma_db")
    if test_db.exists():
        shutil.rmtree(test_db)
