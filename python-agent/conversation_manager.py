"""
Conversation History Manager for CodeMind
Stores and retrieves chat conversations with SQLite
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConversationManager:
    """Manage conversation history and memory"""
    
    def __init__(self, db_path: str = "./conversations.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                sources TEXT,
                agent_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES conversations(session_id)
            )
        ''')
        
        # Indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON messages(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON conversations(created_at DESC)')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized: {self.db_path}")
    
    def create_conversation(self, session_id: str, title: Optional[str] = None) -> Dict:
        """Create a new conversation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO conversations (session_id, title) VALUES (?, ?)',
                (session_id, title or "New Conversation")
            )
            conn.commit()
            
            return {
                "session_id": session_id,
                "title": title or "New Conversation",
                "created_at": datetime.utcnow().isoformat()
            }
        except sqlite3.IntegrityError:
            # Conversation already exists
            return self.get_conversation(session_id)
        finally:
            conn.close()
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        sources: Optional[List[Dict]] = None,
        agent_used: Optional[str] = None
    ) -> Dict:
        """Add a message to conversation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Ensure conversation exists
            self.create_conversation(session_id)
            
            # Insert message
            cursor.execute(
                '''
                INSERT INTO messages (session_id, role, content, sources, agent_used)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (
                    session_id,
                    role,
                    content,
                    json.dumps(sources) if sources else None,
                    agent_used
                )
            )
            
            # Update conversation
            cursor.execute(
                '''
                UPDATE conversations 
                SET updated_at = CURRENT_TIMESTAMP, 
                    message_count = message_count + 1
                WHERE session_id = ?
                ''',
                (session_id,)
            )
            
            conn.commit()
            
            return {
                "id": cursor.lastrowid,
                "session_id": session_id,
                "role": role,
                "content": content,
                "sources": sources,
                "agent_used": agent_used
            }
        finally:
            conn.close()
    
    def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Get messages from a conversation"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT id, role, content, sources, agent_used, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY created_at ASC
            '''
            
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query, (session_id,))
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                message = {
                    "id": row["id"],
                    "role": row["role"],
                    "content": row["content"],
                    "created_at": row["created_at"]
                }
                
                if row["sources"]:
                    message["sources"] = json.loads(row["sources"])
                
                if row["agent_used"]:
                    message["agent_used"] = row["agent_used"]
                
                messages.append(message)
            
            return messages
        finally:
            conn.close()
    
    def get_all_conversations(self, limit: int = 50) -> List[Dict]:
        """Get list of all conversations"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                '''
                SELECT session_id, title, created_at, updated_at, message_count
                FROM conversations
                ORDER BY updated_at DESC
                LIMIT ?
                ''',
                (limit,)
            )
            
            rows = cursor.fetchall()
            conversations = [dict(row) for row in rows]
            
            return conversations
        finally:
            conn.close()
    
    def get_conversation(self, session_id: str) -> Optional[Dict]:
        """Get conversation metadata"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                '''
                SELECT session_id, title, created_at, updated_at, message_count
                FROM conversations
                WHERE session_id = ?
                ''',
                (session_id,)
            )
            
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def update_conversation_title(self, session_id: str, title: str):
        """Update conversation title"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'UPDATE conversations SET title = ? WHERE session_id = ?',
                (title, session_id)
            )
            conn.commit()
        finally:
            conn.close()
    
    def delete_conversation(self, session_id: str):
        """Delete a conversation and its messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
            cursor.execute('DELETE FROM conversations WHERE session_id = ?', (session_id,))
            conn.commit()
        finally:
            conn.close()
    
    def search_conversations(self, query: str, limit: int = 20) -> List[Dict]:
        """Search conversations by content"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                '''
                SELECT DISTINCT c.session_id, c.title, c.created_at, c.updated_at, c.message_count
                FROM conversations c
                JOIN messages m ON c.session_id = m.session_id
                WHERE m.content LIKE ? OR c.title LIKE ?
                ORDER BY c.updated_at DESC
                LIMIT ?
                ''',
                (f'%{query}%', f'%{query}%', limit)
            )
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def get_stats(self) -> Dict:
        """Get conversation statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM conversations')
            total_conversations = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM messages')
            total_messages = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM messages WHERE role = "user"')
            user_messages = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM messages WHERE role = "assistant"')
            assistant_messages = cursor.fetchone()[0]
            
            return {
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "user_messages": user_messages,
                "assistant_messages": assistant_messages
            }
        finally:
            conn.close()


# Singleton instance
_conversation_manager = None

def get_conversation_manager() -> ConversationManager:
    """Get or create conversation manager instance"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager
