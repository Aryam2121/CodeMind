"""
Task Agent - Specialized for task management and planning
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from app.agents.base_agent import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)


TASK_AGENT_PROMPT = """You are an expert task manager and productivity assistant.

Your capabilities:
- Break down complex tasks into subtasks
- Estimate time requirements
- Prioritize tasks
- Suggest deadlines
- Create action plans
- Track progress

Current date: {current_date}

User's existing tasks:
{existing_tasks}

User query: {query}

Provide a structured response with actionable recommendations:"""


class TaskAgent(BaseAgent):
    """Agent specialized in task management"""
    
    def __init__(self):
        super().__init__(
            name="Task Agent",
            description="Expert in task management and productivity",
            system_prompt="You are an expert productivity coach and task manager.",
            temperature=0.6
        )
        
        self.task_keywords = [
            'task', 'todo', 'plan', 'schedule', 'deadline',
            'remind', 'reminder', 'organize', 'prioritize',
            'break down', 'subtask', 'action item', 'agenda',
            'productivity', 'time management'
        ]
    
    def can_handle(self, query: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Determine if this agent should handle the query"""
        query_lower = query.lower()
        
        # Check for task-related keywords
        keyword_matches = sum(1 for keyword in self.task_keywords if keyword in query_lower)
        
        # Calculate confidence
        confidence = keyword_matches / 3.0
        
        return min(confidence, 1.0)
    
    def format_tasks(self, tasks: list) -> str:
        """Format tasks for context"""
        if not tasks:
            return "No existing tasks."
        
        formatted = []
        for task in tasks:
            formatted.append(
                f"- {task.get('title')} "
                f"[{task.get('status')}] "
                f"(Priority: {task.get('priority')})"
            )
        return "\n".join(formatted)
    
    async def process(
        self,
        query: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process task-related query"""
        try:
            logger.info(f"Task Agent processing query for user {user_id}")
            
            # Get existing tasks from context
            existing_tasks = context.get('tasks', []) if context else []
            tasks_text = self.format_tasks(existing_tasks)
            
            # Create prompt
            prompt = PromptTemplate(
                input_variables=["current_date", "existing_tasks", "query"],
                template=TASK_AGENT_PROMPT
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Generate response
            response = await chain.arun(
                current_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                existing_tasks=tasks_text,
                query=query
            )
            
            # Try to extract structured task data
            suggested_tasks = self.extract_tasks_from_response(response)
            
            # Create agent response
            agent_response = AgentResponse(
                agent_name=self.name,
                content=response,
                metadata={
                    "suggested_tasks": suggested_tasks,
                    "existing_task_count": len(existing_tasks)
                }
            )
            
            return agent_response.to_dict()
        
        except Exception as e:
            logger.error(f"Error in Task Agent: {str(e)}")
            return {
                "agent_name": self.name,
                "content": f"I encountered an error while processing your task: {str(e)}",
                "error": str(e)
            }
    
    def extract_tasks_from_response(self, response: str) -> list:
        """Extract structured tasks from LLM response"""
        # Simple extraction - can be improved with function calling
        tasks = []
        
        # Look for bullet points or numbered lists
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '*', '•')) or (len(line) > 0 and line[0].isdigit() and line[1] == '.'):
                task_text = line.lstrip('-*•0123456789. ')
                if len(task_text) > 5:  # Minimum task length
                    tasks.append({
                        "title": task_text,
                        "status": "pending",
                        "priority": "medium"
                    })
        
        return tasks


# Create singleton instance
task_agent = TaskAgent()
