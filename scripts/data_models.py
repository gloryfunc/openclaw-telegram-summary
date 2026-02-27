#!/usr/bin/env python3
"""
数据模型定义
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class MessageType(Enum):
    """消息类型枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


class SessionType(Enum):
    """会话类型枚举"""
    DIRECT = "direct"      # 直接消息
    GROUP = "group"        # 群组消息
    CHANNEL = "channel"    # 频道消息


@dataclass
class Message:
    """消息数据模型"""
    id: str
    timestamp: datetime
    message_type: MessageType
    content: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "message_type": self.message_type.value,
            "content": self.content,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "session_id": self.session_id,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """从字典创建"""
        return cls(
            id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            message_type=MessageType(data["message_type"]),
            content=data["content"],
            user_id=data.get("user_id"),
            user_name=data.get("user_name"),
            session_id=data.get("session_id"),
            metadata=data.get("metadata", {})
        )


@dataclass
class Session:
    """会话数据模型"""
    session_id: str
    session_type: SessionType
    display_name: str
    participants: List[str] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def add_message(self, message: Message):
        """添加消息到会话"""
        self.messages.append(message)
        self.updated_at = message.timestamp
        if self.created_at is None or message.timestamp < self.created_at:
            self.created_at = message.timestamp
    
    def get_messages_by_date(self, date: datetime) -> List[Message]:
        """获取指定日期的消息"""
        target_date = date.date()
        return [
            msg for msg in self.messages
            if msg.timestamp.date() == target_date
        ]
    
    def get_messages_by_week(self, year: int, week: int) -> List[Message]:
        """获取指定周的消息"""
        return [
            msg for msg in self.messages
            if msg.timestamp.isocalendar()[0] == year and msg.timestamp.isocalendar()[1] == week
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "session_type": self.session_type.value,
            "display_name": self.display_name,
            "participants": self.participants,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class DailySummary:
    """每日总结数据模型"""
    date: datetime
    user_id: str
    total_messages: int
    user_messages: int
    assistant_messages: int
    key_topics: List[str] = field(default_factory=list)
    tasks_mentioned: List[str] = field(default_factory=list)
    decisions_made: List[str] = field(default_factory=list)
    summary_text: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "date": self.date.isoformat(),
            "user_id": self.user_id,
            "total_messages": self.total_messages,
            "user_messages": self.user_messages,
            "assistant_messages": self.assistant_messages,
            "key_topics": self.key_topics,
            "tasks_mentioned": self.tasks_mentioned,
            "decisions_made": self.decisions_made,
            "summary_text": self.summary_text
        }


@dataclass
class WeeklyReport:
    """每周报告数据模型"""
    year: int
    week: int
    start_date: datetime
    end_date: datetime
    total_sessions: int
    total_messages: int
    active_users: List[str] = field(default_factory=list)
    daily_summaries: List[DailySummary] = field(default_factory=list)
    weekly_highlights: List[str] = field(default_factory=list)
    next_week_plan: List[str] = field(default_factory=list)
    report_text: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "year": self.year,
            "week": self.week,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "total_sessions": self.total_sessions,
            "total_messages": self.total_messages,
            "active_users": self.active_users,
            "daily_summaries": [summary.to_dict() for summary in self.daily_summaries],
            "weekly_highlights": self.weekly_highlights,
            "next_week_plan": self.next_week_plan,
            "report_text": self.report_text
        }


@dataclass
class WorkPlan:
    """工作计划数据模型"""
    date: datetime
    user_id: str
    priority_tasks: List[str] = field(default_factory=list)
    follow_up_tasks: List[str] = field(default_factory=list)
    new_tasks: List[str] = field(default_factory=list)
    reminders: List[str] = field(default_factory=list)
    plan_text: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "date": self.date.isoformat(),
            "user_id": self.user_id,
            "priority_tasks": self.priority_tasks,
            "follow_up_tasks": self.follow_up_tasks,
            "new_tasks": self.new_tasks,
            "reminders": self.reminders,
            "plan_text": self.plan_text
        }