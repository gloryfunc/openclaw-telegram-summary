#!/usr/bin/env python3
"""
定时任务调度器
负责调度每日和每周任务
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import json
import yaml

from data_manager import DataManager
from ai_summarizer import AISummarizer
from data_models import DailySummary, WorkPlan, WeeklyReport


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, config_path: str = "../config/config.yaml"):
        """
        初始化任务调度器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.data_manager = DataManager(config_path)
        self.summarizer = AISummarizer(self.config["ai"]["model"])
        
        # 日志配置
        self.log_dir = Path(self.config.get("logging", {}).get("file", "../logs/system.log")).parent
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def run_daily_task(self, target_date: Optional[datetime] = None):
        """
        运行每日任务
        
        Args:
            target_date: 目标日期，默认为昨天
        """
        print(f"{'='*60}")
        print(f"开始执行每日任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            if target_date is None:
                target_date = datetime.now() - timedelta(days=1)
            
            date_str = target_date.strftime("%Y-%m-%d")
            print(f"处理日期: {date_str}")
            
            # 1. 收集每日数据
            print("\n1. 收集每日数据...")
            daily_sessions = self.data_manager.collect_daily_data(target_date)
            
            if not daily_sessions:
                print("当日没有对话数据，任务结束")
                self._log_task_result("daily", target_date, "no_data", "当日没有对话数据")
                return
            
            # 2. 归档原始数据
            print("\n2. 归档原始数据...")
            self.data_manager.archive_raw_data(daily_sessions, "daily")
            
            # 3. 为每个用户生成总结
            print("\n3. 生成用户总结...")
            user_ids = self._extract_user_ids(daily_sessions)
            
            for user_id in user_ids:
                print(f"  处理用户: {user_id}")
                
                # 生成每日总结
                summary = self.data_manager.generate_user_summary(user_id, target_date)
                if summary:
                    # 生成总结文本
                    user_messages = self._get_user_messages(daily_sessions, user_id)
                    summary_text = self.summarizer.generate_daily_summary_text(summary, user_messages)
                    summary.summary_text = summary_text
                    
                    # 保存总结
                    self.data_manager.save_processed_data(summary, "user_summary", user_id)
                    
                    # 生成工作计划
                    print("  生成工作计划...")
                    work_plan = self.summarizer.generate_work_plan(summary)
                    self.data_manager.save_processed_data(work_plan, "work_plan", user_id)
                    
                    # 推送通知
                    if self.config["notification"]["enable_daily"]:
                        self._send_daily_notification(user_id, summary, work_plan)
            
            print("\n每日任务执行完成!")
            self._log_task_result("daily", target_date, "success", f"处理了 {len(user_ids)} 个用户")
            
        except Exception as e:
            error_msg = f"每日任务执行失败: {str(e)}"
            print(f"\n❌ {error_msg}")
            self._log_task_result("daily", target_date, "error", error_msg)
            raise
    
    def run_weekly_task(self, target_year: Optional[int] = None, target_week: Optional[int] = None):
        """
        运行每周任务
        
        Args:
            target_year: 目标年份
            target_week: 目标周数
        """
        print(f"{'='*60}")
        print(f"开始执行每周任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            if target_year is None or target_week is None:
                today = datetime.now()
                target_year, target_week, _ = today.isocalendar()
            
            print(f"处理周数: {target_year}年第{target_week}周")
            
            # 1. 收集每周数据
            print("\n1. 收集每周数据...")
            weekly_sessions = self.data_manager.collect_weekly_data(target_year, target_week)
            
            if not weekly_sessions:
                print("本周没有对话数据，任务结束")
                self._log_task_result("weekly", datetime.now(), "no_data", "本周没有对话数据")
                return
            
            # 2. 归档原始数据
            print("\n2. 归档原始数据...")
            self.data_manager.archive_raw_data(weekly_sessions, "weekly")
            
            # 3. 生成每周报告
            print("\n3. 生成每周报告...")
            user_ids = self._extract_user_ids(weekly_sessions)
            
            for user_id in user_ids:
                print(f"  处理用户: {user_id}")
                
                # 加载本周的每日总结
                daily_summaries = []
                all_messages = []
                
                # 模拟加载每日总结（实际应从存储中加载）
                for session in weekly_sessions:
                    user_messages = [msg for msg in session.messages 
                                   if msg.user_id == user_id or msg.message_type.name == "ASSISTANT"]
                    all_messages.extend(user_messages)
                    
                    # 这里应该从存储加载实际的每日总结
                    # 为了演示，我们创建一个模拟总结
                    if user_messages:
                        summary_date = user_messages[0].timestamp
                        mock_summary = DailySummary(
                            date=summary_date,
                            user_id=user_id,
                            total_messages=len(user_messages),
                            user_messages=len([m for m in user_messages if m.message_type.name == "USER"]),
                            assistant_messages=len([m for m in user_messages if m.message_type.name == "ASSISTANT"]),
                            key_topics=["技术讨论", "系统设计"],
                            tasks_mentioned=["实现功能模块", "测试系统"],
                            decisions_made=["采用当前架构", "继续开发"]
                        )
                        daily_summaries.append(mock_summary)
                
                if daily_summaries:
                    # 生成每周报告
                    weekly_report = self.summarizer.generate_weekly_report(daily_summaries, all_messages)
                    
                    # 保存报告
                    self.data_manager.save_processed_data(weekly_report, "weekly_summary", user_id)
                    
                    # 推送通知
                    if self.config["notification"]["enable_weekly"]:
                        self._send_weekly_notification(user_id, weekly_report)
            
            print("\n每周任务执行完成!")
            self._log_task_result("weekly", datetime.now(), "success", f"处理了 {len(user_ids)} 个用户")
            
        except Exception as e:
            error_msg = f"每周任务执行失败: {str(e)}"
            print(f"\n❌ {error_msg}")
            self._log_task_result("weekly", datetime.now(), "error", error_msg)
            raise
    
    def _extract_user_ids(self, sessions) -> list:
        """从会话中提取用户ID列表"""
        user_ids = set()
        for session in sessions:
            for msg in session.messages:
                if msg.user_id and msg.user_id != "assistant":
                    user_ids.add(msg.user_id)
        return list(user_ids)
    
    def _get_user_messages(self, sessions, user_id: str):
        """获取指定用户的消息"""
        messages = []
        for session in sessions:
            for msg in session.messages:
                if msg.user_id == user_id or msg.message_type.name == "ASSISTANT":
                    messages.append(msg)
        return messages
    
    def _send_daily_notification(self, user_id: str, summary: DailySummary, work_plan: WorkPlan):
        """发送每日通知"""
        # 这里应该使用 OpenClaw 的 message 工具发送 Telegram 消息
        # 为了演示，我们只打印日志
        
        notification = f"""
📅 每日总结通知 - {summary.date.strftime('%Y年%m月%d日')}

📊 对话统计:
- 总消息数: {summary.total_messages}
- 你的消息: {summary.user_messages}
- 助手消息: {summary.assistant_messages}

🎯 关键话题: {', '.join(summary.key_topics[:3])}

📋 明日计划已生成，请查看工作系统。

完整总结和工作计划已保存到本地。
"""
        
        print(f"\n📨 发送每日通知给用户 {user_id}:")
        print(notification)
        
        # 实际应该调用: message.send(to=user_id, message=notification)
    
    def _send_weekly_notification(self, user_id: str, weekly_report: WeeklyReport):
        """发送每周通知"""
        # 这里应该使用 OpenClaw 的 message 工具发送 Telegram 消息
        
        notification = f"""
📊 每周报告通知 - {weekly_report.year}年第{weekly_report.week}周

📈 本周概览:
- 活跃天数: {len(weekly_report.daily_summaries)}
- 总消息数: {weekly_report.total_messages}
- 主要亮点: {len(weekly_report.weekly_highlights)} 项

🏆 本周成就已汇总，下周计划已制定。

完整周报已保存到本地，请查看工作系统。
"""
        
        print(f"\n📨 发送每周通知给用户 {user_id}:")
        print(notification)
        
        # 实际应该调用: message.send(to=user_id, message=notification)
    
    def _log_task_result(self, task_type: str, date: datetime, status: str, message: str):
        """记录任务执行结果"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "target_date": date.isoformat() if date else None,
            "status": status,
            "message": message
        }
        
        log_file = self.log_dir / f"task_log_{datetime.now().strftime('%Y-%m-%d')}.json"
        
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
        
        print(f"📝 任务日志已记录: {status} - {message}")


def test_scheduler():
    """测试任务调度器"""
    try:
        print("初始化任务调度器...")
        scheduler = TaskScheduler("../config/config.yaml")
        
        print("\n测试每日任务...")
        test_date = datetime.now() - timedelta(days=1)
        scheduler.run_daily_task(test_date)
        
        print("\n" + "="*60)
        print("测试每周任务...")
        scheduler.run_weekly_task()
        
        print("\n所有测试完成!")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_scheduler()