"""
GitHub Repository Loader for CodeMind
Clones and processes code repositories for RAG indexing
"""

import os
import tempfile
import shutil
from typing import List, Dict, Optional
from pathlib import Path
import subprocess
from langchain_core.documents import Document

class GitHubLoader:
    """Load and process code from GitHub repositories"""
    
    SUPPORTED_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
        '.go', '.rs', '.rb', '.php', '.cs', '.swift', '.kt', '.scala',
        '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.xml'
    }
    
    IGNORE_DIRS = {
        'node_modules', '.git', '__pycache__', 'venv', 'env',
        'dist', 'build', 'target', '.next', '.cache', 'coverage'
    }
    
    def __init__(self, max_file_size: int = 500_000):  # 500KB max per file
        self.max_file_size = max_file_size
    
    def load_from_url(self, repo_url: str, branch: str = "main") -> List[Document]:
        """
        Clone repository and load documents
        
        Args:
            repo_url: GitHub repo URL (https://github.com/user/repo)
            branch: Branch name to clone
            
        Returns:
            List of Document objects
        """
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Clone repository
            print(f"Cloning {repo_url}...")
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', '--branch', branch, repo_url, temp_dir],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                raise Exception(f"Git clone failed: {result.stderr}")
            
            # Process files
            documents = self._process_directory(temp_dir, repo_url)
            print(f"Loaded {len(documents)} files from repository")
            
            return documents
            
        finally:
            # Cleanup
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _process_directory(self, directory: str, repo_url: str) -> List[Document]:
        """Process all files in directory recursively"""
        documents = []
        
        for root, dirs, files in os.walk(directory):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            
            for file in files:
                file_path = Path(root) / file
                
                # Check extension
                if file_path.suffix not in self.SUPPORTED_EXTENSIONS:
                    continue
                
                # Check file size
                try:
                    if file_path.stat().st_size > self.max_file_size:
                        continue
                except:
                    continue
                
                # Read file
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Create relative path
                    rel_path = file_path.relative_to(directory)
                    
                    # Create document
                    doc = Document(
                        page_content=content,
                        metadata={
                            'source': str(rel_path),
                            'file_type': file_path.suffix,
                            'repo_url': repo_url,
                            'file_name': file_path.name,
                            'file_path': str(rel_path)
                        }
                    )
                    documents.append(doc)
                    
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    continue
        
        return documents
    
    def load_from_local(self, local_path: str) -> List[Document]:
        """
        Load documents from local directory
        
        Args:
            local_path: Path to local code directory
            
        Returns:
            List of Document objects
        """
        if not os.path.exists(local_path):
            raise ValueError(f"Directory not found: {local_path}")
        
        documents = self._process_directory(local_path, f"local://{local_path}")
        print(f"Loaded {len(documents)} files from local directory")
        
        return documents
    
    def get_file_stats(self, documents: List[Document]) -> Dict:
        """Get statistics about loaded files"""
        file_types = {}
        total_size = 0
        
        for doc in documents:
            file_type = doc.metadata.get('file_type', 'unknown')
            file_types[file_type] = file_types.get(file_type, 0) + 1
            total_size += len(doc.page_content)
        
        return {
            'total_files': len(documents),
            'file_types': file_types,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / 1024 / 1024, 2)
        }
