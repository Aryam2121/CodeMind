"""
Chat endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import logging

from app.db.session import get_db
from app.core.security import get_current_user
from app.agents.agent_router import agent_router
from app.models.chat import Chat, Message

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    chat_id: str = None
    context: dict = None


class ChatResponse(BaseModel):
    chat_id: str
    message_id: str
    content: str
    agent_name: str
    sources: list = []
    metadata: dict = {}


@router.post("/", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message and get AI response"""
    try:
        user_id = current_user["id"]
        
        # Get or create chat session
        if request.chat_id:
            chat = db.query(Chat).filter(
                Chat.id == request.chat_id,
                Chat.user_id == user_id
            ).first()
            if not chat:
                raise HTTPException(status_code=404, detail="Chat not found")
        else:
            # Create new chat
            chat = Chat(user_id=user_id)
            db.add(chat)
            db.commit()
            db.refresh(chat)
        
        # Save user message
        user_message = Message(
            chat_id=chat.id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()
        
        # Process with agent router
        response = await agent_router.process_query(
            query=request.message,
            user_id=user_id,
            context=request.context
        )
        
        # Save assistant message
        assistant_message = Message(
            chat_id=chat.id,
            role="assistant",
            content=response["content"],
            agent_type=response.get("agent_name"),
            metadata={
                "sources": response.get("sources", []),
                **response.get("metadata", {})
            }
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)
        
        return ChatResponse(
            chat_id=chat.id,
            message_id=assistant_message.id,
            content=response["content"],
            agent_name=response.get("agent_name", "Unknown"),
            sources=response.get("sources", []),
            metadata=response.get("metadata", {})
        )
    
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{chat_id}")
async def get_chat_history(
    chat_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history"""
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user["id"]
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(Message.created_at).all()
    
    return {
        "chat_id": chat.id,
        "title": chat.title,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "agent_type": msg.agent_type,
                "metadata": msg.metadata,
                "created_at": msg.created_at
            }
            for msg in messages
        ]
    }


@router.get("/list")
async def list_chats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all user chats"""
    chats = db.query(Chat).filter(
        Chat.user_id == current_user["id"]
    ).order_by(Chat.updated_at.desc()).all()
    
    return [
        {
            "id": chat.id,
            "title": chat.title,
            "created_at": chat.created_at,
            "updated_at": chat.updated_at
        }
        for chat in chats
    ]


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat"""
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user["id"]
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    db.delete(chat)
    db.commit()
    
    return {"message": "Chat deleted successfully"}
