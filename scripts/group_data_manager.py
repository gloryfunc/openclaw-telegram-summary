#!/usr/bin/env python3
"""
群组数据管理器
专门处理群组聊天记录
"""

import sys
import os
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_models import Session, DailySummary, WeeklyReport, WorkPlan
from group_data_analyzer import GroupDataAnalyzer


class GroupDataManager:
    """群组数据管理器"""
    
    def __init__(self, config_path: str = "../config/config.yaml"):
        """
        初始化群组数据管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.base_path = Path(self.config["storage"]["base_path"])
        self.group_data_path = self.base_path / self.config["storage"].get("group_data", "group")
        
        # 创建目录结构
        self._create_directories()
        
        # 初始化分析器
        self.analyzer = GroupDataAnalyzer(self.config["data_source"]["sessions_path"])
        
        # 目标群组
        self.target_group = self.config["group"]["target_group"]
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _create_directories(self):
        """创建群组数据目录"""
        directories = [
            self.group_data_path,
            self.group_data_path / "raw",
            self.group_data_path / "processed",
            self.group_data_path / "summaries",
            self.group_data_path / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def find_target_group(self) -> Optional[Session]:
        """
        查找目标群组
        
        Returns:
            目标群组会话对象
        """
        print(f"查找目标群组: {self.target_group}")
        
        # 查找所有群组会话
        group_files = self.analyzer.find_group_sessions()
        
        if not group_files:
            print("未找到任何群组会话文件")
            return None
        
        print(f"找到 {len(group_files)} 个群组会话文件")
        
        # 解析每个群组会话，查找目标群组
        for file_path in group_files:
            session = self.analyzer.parse_group_session(file_path)
            if session:
                # 检查是否为目标群组
                if self.target_group.lower() in session.display_name.lower():
                    print(f"找到目标群组: {session.display_name}")
                    return session
                else:
                    print(f"跳过群组: {session.display_name}")
        
        print(f"未找到目标群组: {self.target_group}")
        return None
    
    def collect_group_daily_data(self, target_group: Session, date: Optional[datetime] = None) -> Session:
        """
        收集群组每日数据
        
        Args:
            target_group: 目标群组会话
            date: 目标日期，默认为昨天
            
        Returns:
            包含当日消息的群组会话
        """
        if date is None:
            date = datetime.now() - timedelta(days=1)
        
        target_date = date.date()
        print(f"收集群组 {target_group.display_name} 在 {target_date} 的数据...")
        
        # 过滤出当日的消息
        daily_messages = []
        for msg in target_group.messages:
            if msg.timestamp.date() == target_date:
                daily_messages.append(msg)
        
        if not daily_messages:
            print(f"群组在 {target_date} 没有消息")
            return None
        
        # 创建只包含当日消息的会话
        daily_session = Session(
            session_id=target_group.session_id,
            session_type=target_group.session_type,
            display_name=target_group.display_name,
            participants=target_group.participants,
            messages=daily_messages,
            created_at=min(msg.timestamp for msg in daily_messages),
            updated_at=max(msg.timestamp for msg in daily_messages)
        )
        
        print(f"找到 {len(daily_messages)} 条群组消息在 {target_date}")
        return daily_session
    
    def collect_group_weekly_data(self, target_group: Session, year: Optional[int] = None, week: Optional[int] = None) -> Session:
        """
        收集群组每周数据
        
        Args:
            target_group: 目标群组会话
            year: 目标年份
            week: 目标周数
            
        Returns:
            包含当周消息的群组会话
        """
        if year is None or week is None:
            today = datetime.now()
            year, week, _ = today.isocalendar()
        
        print(f"收集群组 {target_group.display_name} 在 {year}年第{week}周的数据...")
        
        # 过滤出当周的消息
        weekly_messages = []
        for msg in target_group.messages:
            msg_year, msg_week, _ = msg.timestamp.isocalendar()
            if msg_year == year and msg_week == week:
                weekly_messages.append(msg)
        
        if not weekly_messages:
            print(f"群组在 {year}年第{week}周没有消息")
            return None
        
        # 创建只包含当周消息的会话
        weekly_session = Session(
            session_id=target_group.session_id,
            session_type=target_group.session_type,
            display_name=target_group.display_name,
            participants=target_group.participants,
            messages=weekly_messages,
            created_at=min(msg.timestamp for msg in weekly_messages),
            updated_at=max(msg.timestamp for msg in weekly_messages)
        )
        
        print(f"找到 {len(weekly_messages)} 条群组消息在 {year}年第{week}周")
        return weekly_session
    
    def archive_group_data(self, session: Session, archive_type: str = "daily"):
        """
        归档群组数据
        
        Args:
            session: 群组会话
            archive_type: 归档类型 ("daily" 或 "weekly")
        """
        if archive_type not in ["daily", "weekly"]:
            raise ValueError("archive_type 必须是 'daily' 或 'weekly'")
        
        archive_date = datetime.now()
        
        if archive_type == "daily":
            archive_dir = self.group_data_path / "raw" / "daily" / archive_date.strftime("%Y-%m-%d")
        else:
            year, week, _ = archive_date.isocalendar()
            archive_dir = self.group_data_path / "raw" / "weekly" / f"{year}-W{week:02d}"
        
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        archive_file = archive_dir / f"{session.session_id}.json"
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
        
        print(f"已归档群组数据到 {archive_file}")
    
    def analyze_group_daily_activity(self, daily_session: Session) -> Dict[str, Any]:
        """
        分析群组每日活动
        
        Args:
            daily_session: 每日群组会话
            
        Returns:
            分析结果
        """
        return self.analyzer.analyze_group_activity(daily_session)
    
    def generate_group_daily_summary(self, daily_session: Session, analysis: Dict[str, Any]) -> DailySummary:
        """
        生成群组每日总结
        
        Args:
            daily_session: 每日群组会话
            analysis: 分析结果
            
        Returns:
            每日总结对象
        """
        date = daily_session.created_at.date()
        
        # 统计消息数量
        total_messages = len(daily_session.messages)
        
        # 按用户统计
        user_messages = {}
        for msg in daily_session.messages:
            if msg.user_id and msg.user_id != "assistant":
                if msg.user_id not in user_messages:
                    user_messages[msg.user_id] = {
                        "user_id": msg.user_id,
                        "user_name": msg.user_name,
                        "count": 0
                    }
                user_messages[msg.user_id]["count"] += 1
        
        # 提取关键话题（简化实现）
        key_topics = self._extract_group_topics(daily_session.messages)
        
        # 提取任务和决定
        tasks_mentioned = self._extract_group_tasks(daily_session.messages)
        decisions_made = self._extract_group_decisions(daily_session.messages)
        
        # 创建总结对象
        summary = DailySummary(
            date=datetime.combine(date, datetime.min.time()),
            user_id="group",  # 群组ID
            total_messages=total_messages,
            user_messages=total_messages,  # 群组中所有消息都算作用户消息
            assistant_messages=0,  # 群组中助手消息可能较少
            key_topics=key_topics,
            tasks_mentioned=tasks_mentioned,
            decisions_made=decisions_made,
            summary_text=None
        )
        
        # 添加元数据
        summary.metadata = {
            "group_name": daily_session.display_name,
            "participant_count": len(daily_session.participants),
            "user_statistics": list(user_messages.values()),
            "analysis": analysis
        }
        
        return summary
    
    def _extract_group_topics(self, messages: List) -> List[str]:
        """提取群组关键话题"""
        topics = set()
        
        # 常见群组话题关键词
        topic_keywords = {
            "开发": ["开发", "代码", "编程", "实现", "功能"],
            "设计": ["设计", "UI", "UX", "界面", "原型"],
            "测试": ["测试", "bug", "问题", "修复", "验证"],
            "部署": ["部署", "发布", "上线", "服务器", "配置"],
            "会议": ["会议", "讨论", "评审", "同步", "计划"],
            "文档": ["文档", "说明", "指南", "API", "注释"]
        }
        
        for msg in messages:
            content = msg.content.lower()
            for topic, keywords in topic_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in content:
                        topics.add(topic)
                        break
        
        return list(topics)
    
    def _extract_group_tasks(self, messages: List) -> List[str]:
        """提取群组提到的任务"""
        tasks = []
        task_keywords = ["任务", "todo", "待办", "需要", "完成", "实现", "开发"]
        
        for msg in messages:
            content = msg.content
            for keyword in task_keywords:
                if keyword in content:
                    # 提取包含关键字的句子
                    sentences = content.split('。')
                    for sentence in sentences:
                        if keyword in sentence and len(sentence.strip()) > 5:
                            tasks.append(f"{msg.user_name}: {sentence.strip()}")
                            break
        
        return tasks[:5]  # 只返回前5个任务
    
    def _extract_group_decisions(self, messages: List) -> List[str]:
        """提取群组做出的决定"""
        decisions = []
        decision_keywords = ["决定", "选择", "采用", "使用", "同意", "通过", "确定"]
        
        for msg in messages:
            content = msg.content
            for keyword in decision_keywords:
                if keyword in content:
                    sentences = content.split('。')
                    for sentence in sentences:
                        if keyword in sentence and len(sentence.strip()) > 5:
                            decisions.append(f"{msg.user_name}: {sentence.strip()}")
                            break
        
        return decisions[:3]  # 只返回前3个决定
    
    def save_group_summary(self, summary: DailySummary, summary_type: str = "daily"):
        """
        保存群组总结
        
        Args:
            summary: 总结对象
            summary_type: 总结类型 ("daily" 或 "weekly")
        """
        save_dir = self.group_data_path / "summaries" / summary_type
        save_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"group_{summary_type}_summary_{summary.date.strftime('%Y-%m-%d')}.json"
        save_path = save_dir / filename
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(summary.to_dict(), f, ensure_ascii=False, indent=2)
        
        print(f"已保存群组总结到 {save_path}")
    
    def log_group_activity(self, activity_type: str, group_name: str, message: str):
        """
        记录群组活动日志
        
        Args:
            activity_type: 活动类型
            group_name: 群组名称
            message: 日志消息
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "activity_type": activity_type,
            "group_name": group_name,
            "message": message
        }
        
        log_file = self.group_data_path / "logs" / f"group_activity_{datetime.now().strftime('%Y-%m-%d')}.json"
        
        # 读取现有日志
        logs = []
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line))
        
        # 添加新日志
        logs.append(log_entry)
        
        # 写入日志
        with open(log_file, 'w', encoding='utf-8') as f:
            for log in logs:
                f.write(json.dumps(log, ensure_ascii=False) + "\n")
        
        print(f"📝 群组活动日志已记录: {activity_type} - {message}")


def test_group_data_manager():
    """测试群组数据管理器"""
    print("测试群组数据管理器...")
    
    try:
        manager = GroupDataManager("../config/config.yaml")
        
        print(f"\n1. 查找目标群组: {manager.target_group}")
        target_group = manager.find_target_group()
        
        if target_group:
            print(f"✅ 找到目标群组: {target_group.display_name}")
            print(f"   参与者: {len(target_group.participants)} 人")
            print(f"   消息总数: {len(target_group.messages)} 条")
            
            # 测试收集每日数据
            print("\n2. 测试收集群组每日数据...")
            daily_session = manager.collect_group_daily_data(target_group)
            
            if daily_session:
                print(f"✅ 收集到 {len(daily_session.messages)} 条当日消息")
                
                # 测试分析群组活动
                print("\n3. 测试分析群组活动...")
                analysis = manager.analyze_group_daily_activity(daily_session)
                print(f"✅ 群组活动分析完成")
                print(f"   总消息数: {analysis.get('total_messages', 0)}")
                print(f"   总参与者: {analysis.get('total_participants', 0)}")
                
                # 测试生成群组总结
                print("\n4. 测试生成群组总结...")
                summary = manager.generate_group_daily_summary(daily_session, analysis)
                print(f"✅ 群组总结生成成功")
                print(f"   日期: {summary.date.date()}")
                print(f"   关键话题: {summary.key_topics}")
                
                # 测试保存群组总结
                print("\n5. 测试保存群组总结...")
                manager.save_group_summary(summary, "daily")
                print("✅ 群组总结保存成功")
                
                # 测试归档数据
                print("\n6. 测试归档群组数据...")
                manager.archive_group_data(daily_session, "daily")
                print("✅ 群组数据归档成功")
            
            # 测试收集每周数据
            print("\n7. 测试收集群组每周数据...")
            weekly_session = manager.collect_group_weekly_data(target_group)
            
            if weekly_session:
                print(f"✅ 收集到 {len(weekly_session.messages)} 条当周消息")
        
        else:
            print("❌ 未找到目标群组")
            print("\n注意: 需要将bot添加到'develop group'群组并确保有消息记录")
            print("当前配置的目标群组: develop group")
        
        print("\n测试完成!")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_group_data_manager()