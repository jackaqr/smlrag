"""
聊天历史管理器 - 使用内存存储，重启自动清除
"""
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class Message:
    """消息数据类"""
    role: str  # "user" 或 "assistant"
    content: str
    timestamp: str
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ChatMetadata:
    """对话元数据"""
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int
    
    def to_dict(self):
        return asdict(self)


class ChatHistoryManager:
    """聊天历史管理器 - 纯内存存储"""
    
    def __init__(self, max_messages_per_chat: int = 100):
        # 存储结构: {chat_id: {"messages": [], "metadata": {}}}
        self._storage: Dict[str, Dict] = {}
        self.max_messages = max_messages_per_chat
    
    def create_chat(self, chat_id: str, title: str = "新对话") -> ChatMetadata:
        """创建新对话"""
        now = datetime.now().isoformat()
        metadata = ChatMetadata(
            id=chat_id,
            title=title,
            created_at=now,
            updated_at=now,
            message_count=0
        )
        
        self._storage[chat_id] = {
            "messages": [],
            "metadata": metadata
        }
        
        return metadata
    
    def add_message(self, chat_id: str, role: str, content: str) -> Message:
        """添加消息到对话"""
        # 如果对话不存在，自动创建
        if chat_id not in self._storage:
            self.create_chat(chat_id)
        
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat()
        )
        
        self._storage[chat_id]["messages"].append(message)
        
        # 限制消息数量，只保留最近的N条
        if len(self._storage[chat_id]["messages"]) > self.max_messages:
            self._storage[chat_id]["messages"] = \
                self._storage[chat_id]["messages"][-self.max_messages:]
        
        # 更新元数据
        self._storage[chat_id]["metadata"].updated_at = datetime.now().isoformat()
        self._storage[chat_id]["metadata"].message_count = len(
            self._storage[chat_id]["messages"]
        )
        
        return message
    
    def get_messages(self, chat_id: str, limit: Optional[int] = None) -> List[Message]:
        """获取对话的消息列表"""
        if chat_id not in self._storage:
            return []
        
        messages = self._storage[chat_id]["messages"]
        
        if limit:
            return messages[-limit:]
        return messages
    
    def get_chat_metadata(self, chat_id: str) -> Optional[ChatMetadata]:
        """获取对话元数据"""
        if chat_id not in self._storage:
            return None
        return self._storage[chat_id]["metadata"]
    
    def get_all_chats(self) -> List[ChatMetadata]:
        """获取所有对话的元数据列表"""
        return [
            storage["metadata"] 
            for storage in self._storage.values()
        ]
    
    def update_chat_title(self, chat_id: str, title: str) -> bool:
        """更新对话标题"""
        if chat_id not in self._storage:
            return False
        
        self._storage[chat_id]["metadata"].title = title
        self._storage[chat_id]["metadata"].updated_at = datetime.now().isoformat()
        return True
    
    def delete_chat(self, chat_id: str) -> bool:
        """删除对话"""
        if chat_id in self._storage:
            del self._storage[chat_id]
            return True
        return False
    
    def clear_all(self):
        """清除所有数据"""
        self._storage.clear()
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        total_messages = sum(
            len(storage["messages"]) 
            for storage in self._storage.values()
        )
        
        return {
            "total_chats": len(self._storage),
            "total_messages": total_messages,
            "max_messages_per_chat": self.max_messages
        }


# 全局单例实例
chat_manager = ChatHistoryManager(max_messages_per_chat=100)

