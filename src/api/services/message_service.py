import json
import os
from typing import List, Dict, Any
from fastapi import HTTPException
from ..models.schemas import Message

class MessageService:
    def __init__(self):
        self.messages_file = "messages.json"
    
    def _load_messages(self) -> List[Dict[str, Any]]:
        """Load messages from file"""
        if not os.path.exists(self.messages_file):
            return []
        
        try:
            with open(self.messages_file, "r", encoding="utf-8") as f:
                messages = json.load(f)
                return messages if isinstance(messages, list) else []
        except json.JSONDecodeError:
            return []
    
    def _save_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Save messages to file"""
        with open(self.messages_file, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=4)
    
    def get_titles(self) -> List[str]:
        """Get all message titles"""
        messages = self._load_messages()
        return [msg.get("title", "") for msg in messages if "title" in msg]
    
    def load_message(self, title: str) -> List[Dict[str, Any]]:
        """Load message by title"""
        messages = self._load_messages()
        
        for msg in messages:
            if msg.get("title", "").strip().lower() == title.strip().lower():
                content = msg.get("content")
                if isinstance(content, list):
                    return content
                elif isinstance(content, dict):
                    return [content]
                elif isinstance(content, str):
                    return [{"role": msg.get("role", ""), "content": content}]
                else:
                    raise HTTPException(status_code=500, detail="Invalid content format")
        
        raise HTTPException(status_code=404, detail=f"Message with title '{title}' not found")
    
    def delete_message(self, title: str) -> bool:
        """Delete message by title"""
        messages = self._load_messages()
        initial_count = len(messages)
        
        messages = [
            msg for msg in messages
            if msg.get("title", "").strip().lower() != title.strip().lower()
        ]
        
        if len(messages) == initial_count:
            return False
        
        self._save_messages(messages)
        return True
    
    def append_message(self, title: str, message: Message) -> None:
        """Append message to existing title or create new"""
        messages = self._load_messages()
        
        # Find existing message
        for msg in messages:
            if msg.get("title") == title:
                content = msg.get("content")
                message_dict = {"role": message.role, "content": message.content}
                
                if isinstance(content, list):
                    content.append(message_dict)
                elif isinstance(content, dict):
                    msg["content"] = [content, message_dict]
                elif isinstance(content, str):
                    msg["content"] = [
                        {"role": msg.get("role", ""), "content": content},
                        message_dict
                    ]
                else:
                    msg["content"] = [message_dict]
                
                self._save_messages(messages)
                return
        
        # Create new message
        new_message = {
            "title": title,
            "role": message.role,
            "content": [{"role": message.role, "content": message.content}]
        }
        messages.append(new_message)
        self._save_messages(messages)
