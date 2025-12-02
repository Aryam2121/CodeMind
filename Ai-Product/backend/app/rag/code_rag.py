"""
Code RAG System - Specialized for code analysis
"""

import logging
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
import ast
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound

from app.rag.rag_system import RAGSystem
from app.core.config import settings

logger = logging.getLogger(__name__)


class CodeRAGSystem(RAGSystem):
    """Specialized RAG system for code analysis"""
    
    def __init__(self):
        """Initialize Code RAG system"""
        super().__init__()
        self.supported_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', 
            '.java', '.cpp', '.c', '.h', '.hpp',
            '.go', '.rs', '.rb', '.php', '.swift'
        }
    
    def analyze_code_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a code file and extract metadata"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_ext = Path(file_path).suffix
            metadata = {
                "file_type": file_ext,
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "lines_of_code": len(content.splitlines())
            }
            
            # Python-specific analysis
            if file_ext == '.py':
                try:
                    tree = ast.parse(content)
                    
                    # Extract functions and classes
                    functions = []
                    classes = []
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            functions.append({
                                "name": node.name,
                                "line": node.lineno,
                                "docstring": ast.get_docstring(node)
                            })
                        elif isinstance(node, ast.ClassDef):
                            classes.append({
                                "name": node.name,
                                "line": node.lineno,
                                "docstring": ast.get_docstring(node)
                            })
                    
                    metadata.update({
                        "functions": functions,
                        "classes": classes,
                        "function_count": len(functions),
                        "class_count": len(classes)
                    })
                except SyntaxError:
                    logger.warning(f"Syntax error in {file_path}")
            
            # Detect language using Pygments
            try:
                lexer = get_lexer_for_filename(file_path)
                metadata["language"] = lexer.name
            except ClassNotFound:
                pass
            
            return metadata
        
        except Exception as e:
            logger.error(f"Error analyzing code file: {str(e)}")
            return {}
    
    def process_codebase(
        self,
        repo_path: str,
        user_id: str,
        project_id: str
    ) -> Dict[str, Any]:
        """
        Process an entire codebase
        
        Args:
            repo_path: Path to code repository
            user_id: User ID
            project_id: Project identifier
        
        Returns:
            Processing results
        """
        try:
            processed_files = []
            skipped_files = []
            
            # Walk through directory
            for root, dirs, files in os.walk(repo_path):
                # Skip common directories
                dirs[:] = [d for d in dirs if d not in {
                    'node_modules', '.git', '__pycache__', 
                    'venv', 'env', '.venv', 'dist', 'build'
                }]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = Path(file_path).suffix
                    
                    # Only process supported code files
                    if file_ext in self.supported_extensions:
                        try:
                            # Analyze file
                            metadata = self.analyze_code_file(file_path)
                            
                            # Read content
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Add to metadata
                            metadata.update({
                                "project_id": project_id,
                                "user_id": user_id,
                                "relative_path": os.path.relpath(file_path, repo_path)
                            })
                            
                            # Split content into chunks
                            chunks = self.text_splitter.split_text(content)
                            
                            # Add to vector store
                            collection = self.get_collection(user_id, "code")
                            
                            for i, chunk in enumerate(chunks):
                                doc_id = f"{project_id}_{file}_{i}"
                                chunk_metadata = {
                                    **metadata,
                                    "chunk_index": i,
                                    "content": chunk
                                }
                                
                                collection.add(
                                    documents=[chunk],
                                    metadatas=[chunk_metadata],
                                    ids=[doc_id]
                                )
                            
                            processed_files.append(file_path)
                            logger.info(f"Processed: {file_path}")
                        
                        except Exception as e:
                            logger.error(f"Error processing {file_path}: {str(e)}")
                            skipped_files.append(file_path)
            
            return {
                "success": True,
                "processed_files": len(processed_files),
                "skipped_files": len(skipped_files),
                "project_id": project_id
            }
        
        except Exception as e:
            logger.error(f"Error processing codebase: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_code(
        self,
        query: str,
        user_id: str,
        project_id: Optional[str] = None,
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search code with optional project filter"""
        filter_metadata = {"project_id": project_id} if project_id else None
        return self.search_documents(query, user_id, k, filter_metadata)


# Create singleton instance
code_rag_system = CodeRAGSystem()
