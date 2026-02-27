#!/usr/bin/env python3
"""
数据管理器
负责数据的存储、检索和归档
"""

import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_models import Session, DailySummary, WeeklyReport, WorkPlan, Message
from jsonl_parser import JSONLParser


class DataManager:
    """数据管理器"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化数据管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.base_path = Path(self.config["storage"]["base_path"])
        self.raw_path = self.base_path / self.config["storage"]["raw_data"]
        self.processed_path = self.base_path / self.config["storage"]["processed_data"]
        self.summaries_path = self.base_path / self.config["storage"]["summaries"]
        
        # 创建目录结构
        self._create_directories()
        
        # 初始化解析器
        self.parser = JSONLParser(self.config["data_source"]["sessions_path"])
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            self.base_path,
            self.raw_path,
            self.processed_path,
            self.summaries_path,
            self.raw_path / "weekly",
            self.raw_path / "daily",
            self.processed_path / "by_user",
            self.processed_path / "by_week",
            self.summaries_path / "daily",
            self.summaries_path / "weekly",
            self.summaries_path / "plans"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def collect_daily_data(self, date: Optional[datetime] = None) -> List[Session]:
        """
        收集每日数据
        
        Args:
            date: 目标日期，默认为昨天
            
        Returns:
            包含当日消息的会话列表
        """
        if date is None:
            date = datetime.now() - timedelta(days=1)
        
        target_date = date.date()
        print(f"收集 {target_date} 的数据...")
        
        # 解析所有会话
        all_sessions = self.parser.parse_all_sessions()
        
        # 过滤出当日的消息
        daily_sessions = []
        for session in all_sessions:
            daily_messages = session.get_messages_by_date(date)
            if daily_messages:
                # 创建只包含当日消息的新会话
                daily_session = Session(
                    session_id=session.session_id,
                    session_type=session.session_type,
                    display_name=session.display_name,
                    participants=session.participants,
                    messages=daily_messages,
                    created_at=min(msg.timestamp for msg in daily_messages),
                    updated_at=max(msg.timestamp for msg in daily_messages)
                )
                daily_sessions.append(daily_session)
        
        print(f"找到 {len(daily_sessions)} 个会话在 {target_date} 有活动")
        return daily_sessions
    
    def collect_weekly_data(self, year: Optional[int] = None, week: Optional[int] = None) -> List[Session]:
        """
        收集每周数据
        
        Args:
            year: 目标年份，默认为当前年
            week: 目标周数，默认为当前周
            
        Returns:
            包含当周消息的会话列表
        """
        if year is None or week is None:
            today = datetime.now()
            year, week, _ = today.isocalendar()
        
        print(f"收集 {year}年第{week}周的数据...")
        
        # 解析所有会话
        all_sessions = self.parser.parse_all_sessions()
        
        # 过滤出当周的消息
        weekly_sessions = []
        for session in all_sessions:
            weekly_messages = session.get_messages_by_week(year, week)
            if weekly_messages:
                # 创建只包含当周消息的新会话
                weekly_session = Session(
                    session_id=session.session_id,
                    session_type=session.session_type,
                    display_name=session.display_name,
                    participants=session.participants,
                    messages=weekly_messages,
                    created_at=min(msg.timestamp for msg in weekly_messages),
                    updated_at=max(msg.timestamp for msg in weekly_messages)
                )
                weekly_sessions.append(weekly_session)
        
        print(f"找到 {len(weekly_sessions)} 个会话在 {year}年第{week}周有活动")
        return weekly_sessions
    
    def archive_raw_data(self, sessions: List[Session], archive_type: str = "daily"):
        """
        归档原始数据
        
        Args:
            sessions: 会话列表
            archive_type: 归档类型 ("daily" 或 "weekly")
        """
        if archive_type not in ["daily", "weekly"]:
            raise ValueError("archive_type 必须是 'daily' 或 'weekly'")
        
        archive_date = datetime.now()
        
        if archive_type == "daily":
            archive_dir = self.raw_path / "daily" / archive_date.strftime("%Y-%m-%d")
        else:
            year, week, _ = archive_date.isocalendar()
            archive_dir = self.raw_path / "weekly" / f"{year}-W{week:02d}"
        
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        for session in sessions:
            archive_file = archive_dir / f"{session.session_id}.json"
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
        
        print(f"已归档 {len(sessions)} 个会话到 {archive_dir}")
    
    def save_processed_data(self, data: Any, data_type: str, identifier: str):
        """
        保存处理后的数据
        
        Args:
            data: 要保存的数据
            data_type: 数据类型 ("user_summary", "weekly_summary", "work_plan")
            identifier: 标识符（如用户ID、日期等）
        """
        if data_type == "user_summary":
            save_dir = self.processed_path / "by_user" / identifier
        elif data_type == "weekly_summary":
            save_dir = self.processed_path / "by_week" / identifier
        elif data_type == "work_plan":
            save_dir = self.summaries_path / "plans" / identifier
        else:
            raise ValueError(f"未知的数据类型: {data_type}")
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 根据数据类型确定文件名
        if isinstance(data, DailySummary):
            filename = f"daily_summary_{data.date.strftime('%Y-%m-%d')}.json"
            data_dict = data.to_dict()
        elif isinstance(data, WeeklyReport):
            filename = f"weekly_report_{data.year}_W{data.week:02d}.json"
            data_dict = data.to_dict()
        elif isinstance(data, WorkPlan):
            filename = f"work_plan_{data.date.strftime('%Y-%m-%d')}.json"
            data_dict = data.to_dict()
        elif isinstance(data, dict):
            filename = f"{data_type}_{identifier}.json"
            data_dict = data
        else:
            raise ValueError(f"不支持的数据类型: {type(data)}")
        
        save_path = save_dir / filename
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=2)
        
        print(f"已保存 {data_type} 到 {save_path}")
    
    def load_processed_data(self, data_type: str, identifier: str, date: Optional[datetime] = None):
        """
        加载处理后的数据
        
        Args:
            data_type: 数据类型
            identifier: 标识符
            date: 日期（用于 DailySummary 或 WorkPlan）
            
        Returns:
            加载的数据
        """
        if data_type == "user_summary":
            load_dir = self.processed_path / "by_user" / identifier
        elif data_type == "weekly_summary":
            load_dir = self.processed_path / "by_week" / identifier
        elif data_type == "work_plan":
            load_dir = self.summaries_path / "plans" / identifier
        else:
            raise ValueError(f"未知的数据类型: {data_type}")
        
        if not load_dir.exists():
            return None
        
        # 根据数据类型确定文件名
        if data_type in ["user_summary", "work_plan"] and date:
            filename = f"{data_type}_{date.strftime('%Y-%m-%d')}.json"
        elif data_type == "weekly_summary":
            year, week, _ = datetime.now().isocalendar()
            filename = f"weekly_report_{year}_W{week:02d}.json"
        else:
            # 加载最新的文件
            files = list(load_dir.glob("*.json"))
            if not files:
                return None
            filename = max(files, key=lambda x: x.stat().st_mtime).name
        
        load_path = load_dir / filename
        if not load_path.exists():
            return None
        
        with open(load_path, 'r', encoding='utf-8') as f:
            data_dict = json.load(f)
        
        # 根据数据类型转换为对象
        if "daily_summary" in filename:
            return DailySummary.from_dict(data_dict)
        elif "weekly_report" in filename:
            return WeeklyReport.from_dict(data_dict)
        elif "work_plan" in filename:
            return WorkPlan.from_dict(data_dict)
        else:
            return data_dict
    
    def generate_user_summary(self, user_id: str, date: Optional[datetime] = None) -> Optional[DailySummary]:
        """
        生成用户每日总结
        
        Args:
            user_id: 用户ID
            date: 目标日期
            
        Returns:
            DailySummary 对象
        """
        if date is None:
            date = datetime.now() - timedelta(days=1)
        
        # 收集当日数据
        daily_sessions = self.collect_daily_data(date)
        
        # 过滤出该用户的消息
        user_messages = []
        for session in daily_sessions:
            for msg in session.messages:
                if msg.user_id == user_id or msg.user_id == "assistant":
                    user_messages.append(msg)
        
        if not user_messages:
            print(f"用户 {user_id} 在 {date.date()} 没有消息")
            return None
        
        # 统计消息数量
        total_messages = len(user_messages)
        user_msg_count = len([m for m in user_messages if m.user_id == user_id])
        assistant_msg_count = len([m for m in user_messages if m.user_id == "assistant"])
        
        # 提取关键信息（简化版本，实际应该使用AI分析）
        key_topics = self._extract_key_topics(user_messages)
        tasks_mentioned = self._extract_tasks(user_messages)
        decisions_made = self._extract_decisions(user_messages)
        
        # 创建总结对象
        summary = DailySummary(
            date=date,
            user_id=user_id,
            total_messages=total_messages,
            user_messages=user_msg_count,
            assistant_messages=assistant_msg_count,
            key_topics=key_topics,
            tasks_mentioned=tasks_mentioned,
            decisions_made=decisions_made
        )
        
        return summary
    
    def _extract_key_topics(self, messages: List[Message]) -> List[str]:
        """提取关键话题（简化实现）"""
        topics = set()
        for msg in messages:
            content_lower = msg.content.lower()
            if "leetcode" in content_lower:
                topics.add("LeetCode 编程题")
            if "python" in content_lower:
                topics.add("Python 编程")
            if "环境" in content_lower or "安装" in content_lower:
                topics.add("环境配置")
            if "测试" in content_lower:
                topics.add("测试")
        
        return list(topics)
    
    def _extract_tasks(self, messages: List[Message]) -> List[str]:
        """提取提到的任务（简化实现）"""
        tasks = []
        for msg in messages:
            content = msg.content
            # 简单的任务识别
            if "实现" in content or "完成" in content or "编写" in content:
                # 提取任务描述
                lines = content.split('\n')
                for line in lines:
                    if any(keyword in line for keyword in ["实现", "完成", "编写", "创建"]):
                        tasks.append(line.strip())
        
        return tasks[:5]  # 只返回前5个任务
    
    def _extract_decisions(self, messages: List[Message]) -> List[str]:
        """提取做出的决定（简化实现）"""
        decisions = []
        decision_keywords = ["决定", "选择", "采用", "使用", "配置", "设置"]
        
        for msg in messages:
            content = msg.content
            for keyword in decision_keywords:
                if keyword in content:
                    # 找到包含关键字的句子
                    sentences = content.split('。')
                    for sentence in sentences:
                        if keyword in sentence:
                            decisions.append(sentence.strip() + "。")
        
        return decisions[:3]  # 只返回前3个决定


def test_data_manager():
    """测试数据管理器"""
    try:
        manager = DataManager("../config/config.yaml")
        
        # 测试收集每日数据
        print("测试收集每日数据...")
        daily_sessions = manager.collect_daily_data()
        print(f"找到 {len(daily_sessions)} 个当日会话")
        
        if daily_sessions:
            # 测试归档
            print("\n测试归档原始数据...")
            manager.archive_raw_data(daily_sessions, "daily")
            
            # 测试生成用户总结
            print("\n测试生成用户总结...")
            summary = manager.generate_user_summary("8721157770")
            if summary:
                print(f"用户总结生成成功:")
                print(f"- 日期: {summary.date.date()}")
                print(f"- 总消息数: {summary.total_messages}")
                print(f"- 用户消息: {summary.user_messages}")
                print(f"- 助手消息: {summary.assistant_messages}")
                print(f"- 关键话题: {summary.key_topics}")
                
                # 测试保存
                print("\n测试保存处理后的数据...")
                manager.save_processed_data(summary, "user_summary", "8721157770")
        
        # 测试收集每周数据
        print("\n测试收集每周数据...")
        weekly_sessions = manager.collect_weekly_data()
        print(f"找到 {len(weekly_sessions)} 个当周会话")
        
        if weekly_sessions:
            # 测试归档
            print("\n测试归档周数据...")
            manager.archive_raw_data(weekly_sessions, "weekly")
        
        print("\n所有测试完成!")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_data_manager()