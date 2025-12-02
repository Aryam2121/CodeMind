"""
Export Manager for CodeMind
Export conversations and summaries to various formats
"""

import json
import csv
from io import StringIO, BytesIO
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ExportManager:
    """Export conversations and data"""
    
    @staticmethod
    def export_conversation_json(
        conversation: Dict,
        messages: List[Dict]
    ) -> str:
        """Export conversation to JSON"""
        export_data = {
            'conversation': conversation,
            'messages': messages,
            'exported_at': datetime.utcnow().isoformat(),
            'version': '1.0'
        }
        return json.dumps(export_data, indent=2)
    
    @staticmethod
    def export_conversation_markdown(
        conversation: Dict,
        messages: List[Dict]
    ) -> str:
        """Export conversation to Markdown"""
        lines = []
        
        # Header
        lines.append(f"# {conversation.get('title', 'Conversation')}")
        lines.append(f"\n**Created:** {conversation.get('created_at', 'Unknown')}")
        lines.append(f"**Messages:** {len(messages)}\n")
        lines.append("---\n")
        
        # Messages
        for msg in messages:
            role = msg['role'].capitalize()
            content = msg['content']
            
            lines.append(f"## {role}")
            lines.append(f"\n{content}\n")
            
            # Add sources if present
            if msg.get('sources'):
                lines.append("\n**Sources:**")
                for source in msg['sources']:
                    lines.append(f"- {source.get('title', 'Unknown')} - {source.get('snippet', '')[:100]}")
                lines.append("")
            
            lines.append("---\n")
        
        # Footer
        lines.append(f"\n*Exported from CodeMind on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return '\n'.join(lines)
    
    @staticmethod
    def export_conversation_txt(
        conversation: Dict,
        messages: List[Dict]
    ) -> str:
        """Export conversation to plain text"""
        lines = []
        
        # Header
        lines.append(f"Conversation: {conversation.get('title', 'Untitled')}")
        lines.append(f"Created: {conversation.get('created_at', 'Unknown')}")
        lines.append(f"Messages: {len(messages)}")
        lines.append("=" * 80)
        lines.append("")
        
        # Messages
        for msg in messages:
            role = msg['role'].upper()
            content = msg['content']
            timestamp = msg.get('created_at', 'Unknown')
            
            lines.append(f"[{timestamp}] {role}:")
            lines.append(content)
            lines.append("")
            
            if msg.get('sources'):
                lines.append("Sources:")
                for i, source in enumerate(msg['sources'], 1):
                    lines.append(f"  {i}. {source.get('title', 'Unknown')}")
                lines.append("")
            
            lines.append("-" * 80)
            lines.append("")
        
        return '\n'.join(lines)
    
    @staticmethod
    def export_conversations_csv(conversations: List[Dict]) -> str:
        """Export conversation list to CSV"""
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=['session_id', 'title', 'created_at', 'updated_at', 'message_count']
        )
        
        writer.writeheader()
        for conv in conversations:
            writer.writerow({
                'session_id': conv.get('session_id', ''),
                'title': conv.get('title', ''),
                'created_at': conv.get('created_at', ''),
                'updated_at': conv.get('updated_at', ''),
                'message_count': conv.get('message_count', 0)
            })
        
        return output.getvalue()
    
    @staticmethod
    def generate_summary(messages: List[Dict]) -> Dict:
        """Generate summary statistics for conversation"""
        user_messages = [m for m in messages if m['role'] == 'user']
        assistant_messages = [m for m in messages if m['role'] == 'assistant']
        
        # Count sources
        total_sources = sum(
            len(m.get('sources', [])) for m in assistant_messages
        )
        
        # Count agents used
        agents_used = set()
        for m in assistant_messages:
            if m.get('agent_used'):
                agents_used.add(m['agent_used'])
        
        # Average message length
        avg_user_length = sum(len(m['content']) for m in user_messages) / len(user_messages) if user_messages else 0
        avg_assistant_length = sum(len(m['content']) for m in assistant_messages) / len(assistant_messages) if assistant_messages else 0
        
        return {
            'total_messages': len(messages),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'total_sources_cited': total_sources,
            'unique_agents_used': list(agents_used),
            'avg_user_message_length': round(avg_user_length),
            'avg_assistant_message_length': round(avg_assistant_length)
        }


# Singleton instance
_export_manager = None

def get_export_manager() -> ExportManager:
    """Get or create export manager instance"""
    global _export_manager
    if _export_manager is None:
        _export_manager = ExportManager()
    return _export_manager
