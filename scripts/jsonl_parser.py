#!/usr/bin/env python3
"""
JSONL 文件解析器
用于解析 OpenClaw 会话文件
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator
import re

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_models import Message, MessageType, Session, SessionType


class JSONLParser:
    """JSONL 文件解析器"""
    
    def __init__(self, sessions_path: str):
        """
        初始化解析器
        
        Args:
            sessions_path: 会话文件目录路径
        """
        self.sessions_path = Path(sessions_path)
        if not self.sessions_path.exists():
            raise FileNotFoundError(f"会话目录不存在: {sessions_path}")
    
    def list_session_files(self) -> List[Path]:
        """列出所有会话文件"""
        return list(self.sessions_path.glob("*.jsonl"))
    
    def parse_session_file(self, file_path: Path) -> Session:
        """
        解析单个会话文件
        
        Args:
            file_path: JSONL 文件路径
            
        Returns:
            Session 对象
        """
        session_id = file_path.stem
        messages = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    message = self._parse_jsonl_line(data, session_id, line_num)
                    if message:
                        messages.append(message)
                except json.JSONDecodeError as e:
                    print(f"警告: 文件 {file_path} 第 {line_num} 行 JSON 解析错误: {e}")
                    continue
                except Exception as e:
                    print(f"警告: 文件 {file_path} 第 {line_num} 行解析错误: {e}")
                    continue
        
        # 确定会话类型
        session_type = self._determine_session_type(messages)
        
        # 提取参与者
        participants = self._extract_participants(messages)
        
        # 创建会话对象
        session = Session(
            session_id=session_id,
            session_type=session_type,
            display_name=self._get_display_name(session_id, messages),
            participants=participants,
            messages=sorted(messages, key=lambda x: x.timestamp)
        )
        
        return session
    
    def _parse_jsonl_line(self, data: Dict[str, Any], session_id: str, line_num: int) -> Optional[Message]:
        """
        解析单行 JSONL 数据
        
        Args:
            data: JSON 数据
            session_id: 会话ID
            line_num: 行号（用于错误报告）
            
        Returns:
            Message 对象或 None（如果无法解析）
        """
        try:
            record_type = data.get("type")
            
            if record_type == "message":
                return self._parse_message_record(data, session_id)
            elif record_type == "session":
                # 会话元数据，跳过
                return None
            else:
                # 其他类型的记录，跳过
                return None
                
        except Exception as e:
            print(f"警告: 解析记录时出错 (行 {line_num}): {e}")
            return None
    
    def _parse_message_record(self, data: Dict[str, Any], session_id: str) -> Optional[Message]:
        """解析消息记录"""
        message_data = data.get("message")
        if not message_data:
            return None
        
        # 提取时间戳
        timestamp_str = data.get("timestamp")
        if not timestamp_str:
            return None
        
        try:
            # 转换时间戳
            if timestamp_str.endswith("Z"):
                timestamp_str = timestamp_str[:-1] + "+00:00"
            timestamp = datetime.fromisoformat(timestamp_str)
        except (ValueError, TypeError):
            # 尝试其他格式
            try:
                timestamp = datetime.fromtimestamp(int(timestamp_str) / 1000)
            except:
                return None
        
        # 提取角色和内容
        role = message_data.get("role")
        content_parts = message_data.get("content", [])
        
        if not role or not content_parts:
            return None
        
        # 确定消息类型
        if role == "user":
            message_type = MessageType.USER
            # 从用户消息中提取用户ID和名称
            user_id, user_name = self._extract_user_info(content_parts)
            content = self._extract_user_content(content_parts)
        elif role == "assistant":
            message_type = MessageType.ASSISTANT
            user_id = "assistant"
            user_name = "助手"
            content = self._extract_assistant_content(content_parts)
        else:
            # 其他角色，跳过
            return None
        
        # 创建消息对象
        return Message(
            id=data.get("id", ""),
            timestamp=timestamp,
            message_type=message_type,
            content=content,
            user_id=user_id,
            user_name=user_name,
            session_id=session_id,
            metadata={
                "role": role,
                "original_data": message_data
            }
        )
    
    def _extract_user_info(self, content_parts: List[Dict[str, Any]]) -> tuple[Optional[str], Optional[str]]:
        """从用户消息中提取用户ID和名称"""
        user_id = None
        user_name = None
        
        for part in content_parts:
            if part.get("type") == "text":
                text = part.get("text", "")
                # 尝试从文本中提取用户信息
                # 格式: [Telegram gray id:8721157770 ...]
                match = re.search(r'\[Telegram\s+(\w+)\s+id:(\d+)', text)
                if match:
                    user_name = match.group(1)
                    user_id = match.group(2)
                    break
        
        return user_id, user_name
    
    def _extract_user_content(self, content_parts: List[Dict[str, Any]]) -> str:
        """提取用户消息内容"""
        content_texts = []
        
        for part in content_parts:
            if part.get("type") == "text":
                text = part.get("text", "")
                # 移除 Telegram 元数据前缀
                # 格式: [Telegram gray id:8721157770 +9m Tue 2026-02-24 02:45 GMT+8] 实际消息内容
                match = re.search(r'\]\s*(.+)$', text)
                if match:
                    content_texts.append(match.group(1))
                else:
                    # 如果没有元数据前缀，使用整个文本
                    content_texts.append(text)
        
        return " ".join(content_texts).strip()
    
    def _extract_assistant_content(self, content_parts: List[Dict[str, Any]]) -> str:
        """提取助手消息内容"""
        content_texts = []
        
        for part in content_parts:
            if part.get("type") == "text":
                text = part.get("text", "")
                content_texts.append(text)
        
        return " ".join(content_texts).strip()
    
    def _determine_session_type(self, messages: List[Message]) -> SessionType:
        """确定会话类型"""
        # 基于消息中的用户数量判断
        user_ids = set(msg.user_id for msg in messages if msg.user_id)
        
        if len(user_ids) <= 2:
            return SessionType.DIRECT
        else:
            return SessionType.GROUP
    
    def _extract_participants(self, messages: List[Message]) -> List[str]:
        """提取参与者列表"""
        participants = set()
        
        for msg in messages:
            if msg.user_id and msg.user_id != "assistant":
                participants.add(msg.user_id)
        
        return list(participants)
    
    def _get_display_name(self, session_id: str, messages: List[Message]) -> str:
        """获取会话显示名称"""
        # 尝试从消息中提取
        for msg in messages:
            if msg.user_name and msg.user_name != "助手":
                return f"与 {msg.user_name} 的对话"
        
        # 回退到会话ID
        return f"会话 {session_id}"
    
    def parse_all_sessions(self) -> List[Session]:
        """解析所有会话文件"""
        sessions = []
        session_files = self.list_session_files()
        
        print(f"找到 {len(session_files)} 个会话文件")
        
        for file_path in session_files:
            try:
                session = self.parse_session_file(file_path)
                if session.messages:
                    sessions.append(session)
                    print(f"解析会话: {session.display_name} ({len(session.messages)} 条消息)")
            except Exception as e:
                print(f"解析文件 {file_path} 时出错: {e}")
                continue
        
        return sessions


def test_parser():
    """测试解析器"""
    parser = JSONLParser("/root/.openclaw/agents/main/sessions")
    
    try:
        sessions = parser.parse_all_sessions()
        
        if sessions:
            print(f"\n成功解析 {len(sessions)} 个会话:")
            for session in sessions:
                print(f"- {session.display_name}: {len(session.messages)} 条消息")
                
                # 显示最近的消息
                recent_messages = session.messages[-3:] if session.messages else []
                for msg in recent_messages:
                    print(f"  [{msg.timestamp}] {msg.user_name}: {msg.content[:50]}...")
                print()
        else:
            print("未找到有效的会话数据")
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_parser()