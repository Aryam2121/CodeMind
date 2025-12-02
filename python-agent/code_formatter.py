"""
Code Formatter for CodeMind
Detects and formats code blocks with syntax highlighting metadata
"""

import re
from typing import List, Dict, Tuple

class CodeFormatter:
    """Format code blocks in AI responses"""
    
    # Common programming languages
    LANGUAGES = {
        'python', 'javascript', 'typescript', 'java', 'cpp', 'c', 'csharp',
        'go', 'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r',
        'html', 'css', 'scss', 'sql', 'bash', 'shell', 'powershell',
        'json', 'yaml', 'xml', 'markdown', 'dockerfile', 'makefile'
    }
    
    # Code block patterns
    CODE_BLOCK_PATTERN = r'```(\w+)?\n(.*?)```'
    INLINE_CODE_PATTERN = r'`([^`]+)`'
    
    @staticmethod
    def detect_language(code: str) -> str:
        """
        Detect programming language from code snippet
        Uses simple heuristics
        """
        code_lower = code.lower()
        
        # Python indicators
        if any(keyword in code for keyword in ['def ', 'import ', 'class ', 'print(', '__init__']):
            return 'python'
        
        # JavaScript/TypeScript indicators  
        if any(keyword in code for keyword in ['function ', 'const ', 'let ', 'var ', '=>', 'console.log']):
            if 'interface ' in code or ': string' in code or ': number' in code:
                return 'typescript'
            return 'javascript'
        
        # Java indicators
        if any(keyword in code for keyword in ['public class', 'private ', 'public static void main']):
            return 'java'
        
        # C/C++ indicators
        if '#include' in code or 'int main(' in code:
            if 'std::' in code or 'iostream' in code:
                return 'cpp'
            return 'c'
        
        # Go indicators
        if 'func ' in code and 'package ' in code:
            return 'go'
        
        # HTML indicators
        if re.search(r'<\w+[^>]*>', code):
            return 'html'
        
        # CSS indicators
        if re.search(r'[\w-]+\s*:\s*[^;]+;', code) and '{' in code:
            return 'css'
        
        # JSON indicators
        if code.strip().startswith('{') or code.strip().startswith('['):
            try:
                import json
                json.loads(code)
                return 'json'
            except:
                pass
        
        # SQL indicators
        if any(keyword in code_lower for keyword in ['select ', 'insert ', 'update ', 'delete ', 'create table']):
            return 'sql'
        
        # Bash/Shell indicators
        if code.startswith('#!') or any(cmd in code for cmd in ['echo ', 'grep ', 'sed ', 'awk ']):
            return 'bash'
        
        return 'text'
    
    @staticmethod
    def format_response(text: str) -> Dict:
        """
        Format AI response with code block metadata
        
        Returns:
            {
                'formatted_text': str,
                'code_blocks': [{'language': str, 'code': str, 'index': int}],
                'has_code': bool
            }
        """
        code_blocks = []
        
        # Find all code blocks
        matches = list(re.finditer(CodeFormatter.CODE_BLOCK_PATTERN, text, re.DOTALL))
        
        for idx, match in enumerate(matches):
            language = match.group(1) or CodeFormatter.detect_language(match.group(2))
            code = match.group(2).strip()
            
            code_blocks.append({
                'language': language,
                'code': code,
                'index': idx,
                'start': match.start(),
                'end': match.end()
            })
        
        return {
            'formatted_text': text,
            'code_blocks': code_blocks,
            'has_code': len(code_blocks) > 0
        }
    
    @staticmethod
    def extract_code_snippets(text: str) -> List[Tuple[str, str]]:
        """
        Extract all code snippets (both block and inline)
        
        Returns:
            List of (language, code) tuples
        """
        snippets = []
        
        # Extract code blocks
        for match in re.finditer(CodeFormatter.CODE_BLOCK_PATTERN, text, re.DOTALL):
            language = match.group(1) or CodeFormatter.detect_language(match.group(2))
            code = match.group(2).strip()
            snippets.append((language, code))
        
        # Extract inline code
        for match in re.finditer(CodeFormatter.INLINE_CODE_PATTERN, text):
            snippets.append(('inline', match.group(1)))
        
        return snippets
    
    @staticmethod
    def highlight_keywords(code: str, language: str) -> str:
        """
        Add keyword highlighting markers for frontend
        This is basic - frontend should use proper syntax highlighter
        """
        # This is a placeholder - actual highlighting should be done client-side
        # Return code with language hint for frontend
        return f"```{language}\n{code}\n```"


# Singleton instance
_code_formatter = None

def get_code_formatter() -> CodeFormatter:
    """Get or create code formatter instance"""
    global _code_formatter
    if _code_formatter is None:
        _code_formatter = CodeFormatter()
    return _code_formatter
