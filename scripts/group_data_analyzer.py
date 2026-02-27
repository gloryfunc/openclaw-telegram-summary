#!/usr/bin/env python3
"""
群组数据解析器 - 专门处理群组聊天记录
"""

import sys
import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_models import Message, Session, SessionType


class GroupDataAnalyzer:
    """群组数据解析器"""
    
    def __init__(self, sessions_path: str = "/root/.openclaw/agents/main/sessions"):
        """
        初始化群组数据解析器
        
        Args:
            sessions_path: 会话文件目录路径
        """
        self.sessions_path = Path(sessions_path)
        
    def find_group_sessions(self) -> List[Path]:
        """
        查找群组会话文件
        
        Returns:
            群组会话文件路径列表
        """
        session_files = []
        
        if not self.sessions_path.exists():
            print(f"警告: 会话目录不存在: {self.sessions_path}")
            return session_files
        
        # 查找所有会话文件
        for file_path in self.sessions_path.glob("*.jsonl"):
            try:
                # 快速检查文件内容，判断是否为群组会话
                if self._is_group_session(file_path):
                    session_files.append(file_path)
            except Exception as e:
                print(f"警告: 检查文件 {file_path} 时出错: {e}")
                continue
        
        return session_files
    
    def _is_group_session(self, file_path: Path) -> bool:
        """
        判断是否为群组会话
        
        Args:
            file_path: 会话文件路径
            
        Returns:
            是否为群组会话
        """
        # 从文件名或内容判断
        filename = file_path.name
        
        # 检查文件名是否包含群组标识
        # 群组会话通常有特定的命名模式
        if "group" in filename.lower() or "chat" in filename.lower():
            return True
        
        # 检查文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 读取前几行进行快速判断
                for _ in range(10):
                    line = f.readline()
                    if not line:
                        break
                    
                    try:
                        data = json.loads(line.strip())
                        # 检查消息中是否包含多个用户
                        if data.get("type") == "message":
                            message_data = data.get("message", {})
                            content = message_data.get("content", [])
                            
                            # 检查是否为群组格式的消息
                            for part in content:
                                if isinstance(part, dict) and part.get("type") == "text":
                                    text = part.get("text", "")
                                    # 群组消息通常有 [Telegram group ...] 格式
                                    if "Telegram" in text and ("group" in text.lower() or "chat" in text.lower()):
                                        return True
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
        
        return False
    
    def parse_group_session(self, file_path: Path) -> Optional[Session]:
        """
        解析群组会话文件
        
        Args:
            file_path: 群组会话文件路径
            
        Returns:
            Session 对象或 None
        """
        session_id = file_path.stem
        messages = []
        participants = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        message = self._parse_group_message(data, session_id, line_num)
                        if message:
                            messages.append(message)
                            if message.user_id:
                                participants.add(message.user_id)
                    except json.JSONDecodeError as e:
                        print(f"警告: 文件 {file_path} 第 {line_num} 行 JSON 解析错误: {e}")
                        continue
                    except Exception as e:
                        print(f"警告: 文件 {file_path} 第 {line_num} 行解析错误: {e}")
                        continue
            
            if not messages:
                return None
            
            # 确定群组名称
            group_name = self._extract_group_name(messages, session_id)
            
            # 创建会话对象
            session = Session(
                session_id=session_id,
                session_type=SessionType.GROUP,
                display_name=group_name,
                participants=list(participants),
                messages=sorted(messages, key=lambda x: x.timestamp)
            )
            
            return session
            
        except Exception as e:
            print(f"解析群组会话文件 {file_path} 时出错: {e}")
            return None
    
    def _parse_group_message(self, data: Dict[str, Any], session_id: str, line_num: int) -> Optional[Message]:
        """
        解析群组消息
        
        Args:
            data: JSON 数据
            session_id: 会话ID
            line_num: 行号
            
        Returns:
            Message 对象或 None
        """
        try:
            record_type = data.get("type")
            
            if record_type == "message":
                return self._parse_group_message_record(data, session_id)
            else:
                return None
                
        except Exception as e:
            print(f"警告: 解析群组记录时出错 (行 {line_num}): {e}")
            return None
    
    def _parse_group_message_record(self, data: Dict[str, Any], session_id: str) -> Optional[Message]:
        """解析群组消息记录"""
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
            try:
                timestamp = datetime.fromtimestamp(int(timestamp_str) / 1000)
            except:
                return None
        
        # 提取角色和内容
        role = message_data.get("role")
        content_parts = message_data.get("content", [])
        
        if not role or not content_parts:
            return None
        
        # 群组消息解析
        user_id = None
        user_name = None
        content = ""
        
        for part in content_parts:
            if part.get("type") == "text":
                text = part.get("text", "")
                
                # 解析群组消息格式
                # 格式: [Telegram group develop group id:-1001234567890 user:gray id:8721157770 ...]
                group_match = re.search(r'\[Telegram\s+(?:group|chat)\s+([^]]+)\]', text)
                if group_match:
                    group_info = group_match.group(1)
                    
                    # 提取用户信息
                    user_match = re.search(r'user:(\w+)\s+id:(\d+)', group_info)
                    if user_match:
                        user_name = user_match.group(1)
                        user_id = user_match.group(2)
                    
                    # 提取消息内容
                    content_match = re.search(r'\]\s*(.+)$', text)
                    if content_match:
                        content = content_match.group(1)
                    else:
                        # 如果没有明确的内容分隔，尝试提取
                        content = text.replace(group_match.group(0), "").strip()
                else:
                    # 如果不是标准格式，使用整个文本
                    content = text
        
        # 确定消息类型
        from data_models import MessageType
        if role == "user":
            message_type = MessageType.USER
        elif role == "assistant":
            message_type = MessageType.ASSISTANT
            user_id = "assistant"
            user_name = "助手"
        else:
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
                "original_data": message_data,
                "is_group_message": True
            }
        )
    
    def _extract_group_name(self, messages: List[Message], session_id: str) -> str:
        """
        提取群组名称
        
        Args:
            messages: 消息列表
            session_id: 会话ID
            
        Returns:
            群组名称
        """
        # 从消息中提取群组名称
        for msg in messages:
            if msg.content:
                # 尝试从消息内容中提取群组名称
                match = re.search(r'\[Telegram\s+(?:group|chat)\s+([^\s]+)', msg.content)
                if match:
                    group_name = match.group(1)
                    return f"群组: {group_name}"
        
        # 回退到会话ID
        return f"群组会话 {session_id}"
    
    def analyze_group_activity(self, session: Session) -> Dict[str, Any]:
        """
        分析群组活动
        
        Args:
            session: 群组会话对象
            
        Returns:
            分析结果
        """
        if not session.messages:
            return {}
        
        # 按用户统计
        user_stats = {}
        for msg in session.messages:
            if msg.user_id and msg.user_id != "assistant":
                if msg.user_id not in user_stats:
                    user_stats[msg.user_id] = {
                        "user_id": msg.user_id,
                        "user_name": msg.user_name,
                        "message_count": 0,
                        "first_message": msg.timestamp,
                        "last_message": msg.timestamp
                    }
                
                stats = user_stats[msg.user_id]
                stats["message_count"] += 1
                if msg.timestamp < stats["first_message"]:
                    stats["first_message"] = msg.timestamp
                if msg.timestamp > stats["last_message"]:
                    stats["last_message"] = msg.timestamp
        
        # 按日期统计
        date_stats = {}
        for msg in session.messages:
            date_key = msg.timestamp.date().isoformat()
            if date_key not in date_stats:
                date_stats[date_key] = {
                    "date": date_key,
                    "message_count": 0,
                    "user_count": set()
                }
            
            stats = date_stats[date_key]
            stats["message_count"] += 1
            if msg.user_id:
                stats["user_count"].add(msg.user_id)
        
        # 转换日期统计
        for date_key in date_stats:
            date_stats[date_key]["user_count"] = len(date_stats[date_key]["user_count"])
        
        return {
            "session_id": session.session_id,
            "group_name": session.display_name,
            "total_messages": len(session.messages),
            "total_participants": len(session.participants),
            "time_range": {
                "start": min(msg.timestamp for msg in session.messages).isoformat(),
                "end": max(msg.timestamp for msg in session.messages).isoformat()
            },
            "user_statistics": list(user_stats.values()),
            "date_statistics": list(date_stats.values())
        }


def test_group_analyzer():
    """测试群组分析器"""
    print("测试群组数据解析器...")
    
    analyzer = GroupDataAnalyzer()
    
    # 查找群组会话
    print("\n1. 查找群组会话...")
    group_files = analyzer.find_group_sessions()
    
    if group_files:
        print(f"找到 {len(group_files)} 个群组会话文件:")
        for file_path in group_files:
            print(f"  • {file_path.name}")
        
        # 解析第一个群组会话
        print("\n2. 解析群组会话...")
        session = analyzer.parse_group_session(group_files[0])
        
        if session:
            print(f"群组名称: {session.display_name}")
            print(f"参与者数量: {len(session.participants)}")
            print(f"消息数量: {len(session.messages)}")
            
            # 分析群组活动
            print("\n3. 分析群组活动...")
            analysis = analyzer.analyze_group_activity(session)
            
            print(f"总消息数: {analysis.get('total_messages', 0)}")
            print(f"总参与者: {analysis.get('total_participants', 0)}")
            
            # 显示用户统计
            user_stats = analysis.get('user_statistics', [])
            if user_stats:
                print("\n用户活跃度排名:")
                sorted_users = sorted(user_stats, key=lambda x: x['message_count'], reverse=True)
                for i, user in enumerate(sorted_users[:5], 1):
                    print(f"  {i}. {user.get('user_name', '未知')}: {user['message_count']} 条消息")
        else:
            print("无法解析群组会话")
    else:
        print("未找到群组会话文件")
        print("\n注意: 需要将bot添加到'develop group'群组并确保有消息记录")
    
    print("\n测试完成!")


if __name__ == "__main__":
    test_group_analyzer()