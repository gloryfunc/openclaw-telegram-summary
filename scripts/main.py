#!/usr/bin/env python3
"""
Telegram 聊天记录总结系统 - 主入口
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_manager import DataManager
from ai_summarizer import AISummarizer


class TelegramSummarySystem:
    """Telegram 聊天记录总结系统"""
    
    def __init__(self, config_path: str = "../config/config.yaml"):
        """
        初始化系统
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.data_manager = None
        self.summarizer = None
        self._init_system()
    
    def _init_system(self):
        """初始化系统组件"""
        print("初始化 Telegram 聊天记录总结系统...")
        
        try:
            self.data_manager = DataManager(self.config_path)
            self.summarizer = AISummarizer()
            print("✅ 系统初始化成功")
        except Exception as e:
            print(f"❌ 系统初始化失败: {e}")
            raise
    
    def run_daily_summary(self, target_date: datetime = None):
        """
        运行每日总结任务
        
        Args:
            target_date: 目标日期，默认为昨天
        """
        print(f"\n{'='*60}")
        print(f"执行每日总结任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        if target_date is None:
            target_date = datetime.now() - timedelta(days=1)
        
        date_str = target_date.strftime("%Y-%m-%d")
        print(f"📅 处理日期: {date_str}")
        
        try:
            # 1. 收集每日数据
            print("\n1. 📊 收集每日数据...")
            daily_sessions = self.data_manager.collect_daily_data(target_date)
            
            if not daily_sessions:
                print("   ℹ️ 当日没有对话数据")
                return
            
            print(f"   ✅ 找到 {len(daily_sessions)} 个会话")
            
            # 2. 归档原始数据
            print("\n2. 📁 归档原始数据...")
            self.data_manager.archive_raw_data(daily_sessions, "daily")
            print("   ✅ 数据归档完成")
            
            # 3. 处理每个用户
            print("\n3. 👤 处理用户数据...")
            user_ids = self._extract_user_ids(daily_sessions)
            
            for user_id in user_ids:
                print(f"   👤 处理用户: {user_id}")
                
                # 生成每日总结
                summary = self.data_manager.generate_user_summary(user_id, target_date)
                if summary:
                    # 获取用户消息
                    user_messages = self._get_user_messages(daily_sessions, user_id)
                    
                    # 生成总结文本
                    summary_text = self.summarizer.generate_daily_summary_text(summary, user_messages)
                    summary.summary_text = summary_text
                    
                    # 保存总结
                    self.data_manager.save_processed_data(summary, "user_summary", user_id)
                    print(f"     ✅ 每日总结已保存")
                    
                    # 生成工作计划
                    work_plan = self.summarizer.generate_work_plan(summary)
                    self.data_manager.save_processed_data(work_plan, "work_plan", user_id)
                    print(f"     ✅ 工作计划已保存")
                    
                    # 发送通知
                    self._send_telegram_notification(user_id, summary, work_plan)
                    
                    # 输出每日总结摘要
                    daily_summary = self._generate_daily_summary_text(summary)
                    print(f"\n📅 每日总结摘要:\n{daily_summary}")
                else:
                    print(f"     ℹ️ 用户 {user_id} 没有生成总结")
            
            print(f"\n🎉 每日总结任务完成! 处理了 {len(user_ids)} 个用户")
            
        except Exception as e:
            print(f"\n❌ 每日总结任务失败: {e}")
            import traceback
            traceback.print_exc()
    
    def run_weekly_report(self, target_year: int = None, target_week: int = None):
        """
        运行每周报告任务
        
        Args:
            target_year: 目标年份
            target_week: 目标周数
        """
        print(f"\n{'='*60}")
        print(f"执行每周报告任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        if target_year is None or target_week is None:
            today = datetime.now()
            target_year, target_week, _ = today.isocalendar()
        
        print(f"📅 处理周数: {target_year}年第{target_week}周")
        
        try:
            # 1. 收集每周数据
            print("\n1. 📊 收集每周数据...")
            weekly_sessions = self.data_manager.collect_weekly_data(target_year, target_week)
            
            if not weekly_sessions:
                print("   ℹ️ 本周没有对话数据")
                return
            
            print(f"   ✅ 找到 {len(weekly_sessions)} 个会话")
            
            # 2. 归档原始数据
            print("\n2. 📁 归档原始数据...")
            self.data_manager.archive_raw_data(weekly_sessions, "weekly")
            print("   ✅ 数据归档完成")
            
            # 3. 处理每个用户
            print("\n3. 👤 处理用户数据...")
            user_ids = self._extract_user_ids(weekly_sessions)
            
            for user_id in user_ids:
                print(f"   👤 处理用户: {user_id}")
                
                # 这里应该从存储加载本周的每日总结
                # 为了演示，我们使用模拟数据
                user_messages = self._get_user_messages(weekly_sessions, user_id)
                
                if user_messages:
                    # 创建模拟的每日总结
                    mock_summaries = self._create_mock_daily_summaries(user_id, user_messages)
                    
                    # 生成每周报告
                    weekly_report = self.summarizer.generate_weekly_report(mock_summaries, user_messages)
                    
                    # 保存报告
                    self.data_manager.save_processed_data(weekly_report, "weekly_summary", user_id)
                    print(f"     ✅ 每周报告已保存")
                    
                    # 发送通知
                    self._send_weekly_notification(user_id, weekly_report)
                else:
                    print(f"     ℹ️ 用户 {user_id} 没有消息数据")
            
            # 生成详细的周报摘要用于通知
            if user_messages and weekly_report:
                summary_text = self._generate_weekly_summary_text(weekly_report)
                print(f"\n📊 周报摘要:\n{summary_text}")
            
            print(f"\n🎉 每周报告任务完成! 处理了 {len(user_ids)} 个用户")
            
        except Exception as e:
            print(f"\n❌ 每周报告任务失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _extract_user_ids(self, sessions):
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
                if msg.user_id == user_id or msg.user_id == "assistant":
                    messages.append(msg)
        return messages
    
    def _create_mock_daily_summaries(self, user_id: str, messages):
        """创建模拟的每日总结（实际应从存储加载）"""
        from data_models import DailySummary
        
        if not messages:
            return []
        
        # 按日期分组消息
        messages_by_date = {}
        for msg in messages:
            date_key = msg.timestamp.date()
            if date_key not in messages_by_date:
                messages_by_date[date_key] = []
            messages_by_date[date_key].append(msg)
        
        # 为每天创建总结
        summaries = []
        for date_key, date_messages in messages_by_date.items():
            user_msg_count = len([m for m in date_messages if m.user_id == user_id])
            assistant_msg_count = len([m for m in date_messages if m.user_id == "assistant"])
            
            summary = DailySummary(
                date=datetime.combine(date_key, datetime.min.time()),
                user_id=user_id,
                total_messages=len(date_messages),
                user_messages=user_msg_count,
                assistant_messages=assistant_msg_count,
                key_topics=["技术讨论", "项目开发"],
                tasks_mentioned=["功能实现", "系统测试"],
                decisions_made=["技术方案选择", "项目规划"]
            )
            summaries.append(summary)
        
        return summaries
    
    def _send_telegram_notification(self, user_id: str, summary, work_plan):
        """发送 Telegram 通知"""
        try:
            # 构建通知消息
            notification = f"""
📅 每日总结通知 - {summary.date.strftime('%Y年%m月%d日')}

📊 对话统计:
• 总消息数: {summary.total_messages}
• 你的消息: {summary.user_messages}
• 助手消息: {summary.assistant_messages}

🎯 关键话题: {', '.join(summary.key_topics[:3]) if summary.key_topics else '无'}

📋 明日计划已生成，包含:
• {len(work_plan.priority_tasks)} 个优先任务
• {len(work_plan.follow_up_tasks)} 个跟进任务
• {len(work_plan.new_tasks)} 个新任务

完整总结和工作计划已保存到系统。
"""
            
            # 这里应该使用 OpenClaw 的 message 工具发送
            # 暂时打印到控制台
            print(f"\n     📨 发送通知给用户 {user_id}:")
            print(f"     {notification[:100]}...")
            
            # 实际发送代码:
            # from openclaw_tools import send_message
            # send_message(to=user_id, message=notification)
            
        except Exception as e:
            print(f"     ❌ 发送通知失败: {e}")
    
    def _generate_daily_summary_text(self, daily_summary):
        """生成每日总结摘要文本"""
        try:
            date_str = daily_summary.date.strftime('%Y年%m月%d日') if hasattr(daily_summary.date, 'strftime') else str(daily_summary.date)
            
            summary = f"""
📅 {date_str} 每日总结

📊 对话统计:
• 总消息数: {daily_summary.total_messages}
• 你的消息: {daily_summary.user_messages}
• 助手消息: {daily_summary.assistant_messages}

🎯 关键话题:
{chr(10).join(f'• {topic}' for topic in daily_summary.key_topics[:3]) if daily_summary.key_topics else '• 无'}

📋 提到任务:
{chr(10).join(f'• {task}' for task in daily_summary.tasks_mentioned[:3]) if daily_summary.tasks_mentioned else '• 无'}

完整总结已保存到系统。
"""
            return summary
        except Exception as e:
            return f"每日总结生成完成，但生成摘要时出错: {e}"
    
    def _generate_weekly_summary_text(self, weekly_report):
        """生成周报摘要文本"""
        try:
            total_messages = weekly_report.total_messages
            active_days = len([s for s in weekly_report.daily_summaries if s.total_messages > 0])
            
            summary = f"""
📊 {weekly_report.year}年第{weekly_report.week}周报告摘要

📈 数据统计:
• 总消息数: {total_messages}
• 活跃天数: {active_days}天
• 处理会话: {weekly_report.total_sessions}个

🎯 本周重点:
{chr(10).join(f'• {topic}' for topic in weekly_report.weekly_highlights[:5])}

📅 活跃日期:
"""
            # 添加每日统计
            for daily in weekly_report.daily_summaries[:3]:  # 只显示前3天
                if daily.total_messages > 0:
                    date_str = daily.date.strftime('%m月%d日') if hasattr(daily.date, 'strftime') else str(daily.date)[5:10]
                    summary += f"• {date_str}: {daily.total_messages}条消息\n"
            
            summary += f"""
📋 下周计划:
{chr(10).join(f'• {task}' for task in weekly_report.next_week_plan[:3])}

完整报告已保存到系统。
"""
            return summary
        except Exception as e:
            return f"周报生成完成，但生成摘要时出错: {e}"
    
    def _send_weekly_notification(self, user_id: str, weekly_report):
        """发送每周通知"""
        try:
            notification = f"""
📊 每周报告通知 - {weekly_report.year}年第{weekly_report.week}周

📈 本周概览:
• 活跃天数: {len(weekly_report.daily_summaries)}
• 总消息数: {weekly_report.total_messages}
• 主要亮点: {len(weekly_report.weekly_highlights)} 项

🏆 本周工作已汇总，下周计划已制定。

完整周报已保存到系统，请查看详细内容。
"""
            
            print(f"\n     📨 发送周报通知给用户 {user_id}:")
            print(f"     {notification[:100]}...")
            
        except Exception as e:
            print(f"     ❌ 发送周报通知失败: {e}")
    
    def show_system_status(self):
        """显示系统状态"""
        print(f"\n{'='*60}")
        print("系统状态检查")
        print(f"{'='*60}")
        
        # 检查目录
        base_dir = Path("../")
        dirs_to_check = [
            "config",
            "scripts", 
            "data",
            "data/raw",
            "data/processed",
            "summaries",
            "logs"
        ]
        
        print("\n📁 目录结构检查:")
        for dir_path in dirs_to_check:
            full_path = base_dir / dir_path
            if full_path.exists():
                print(f"   ✅ {dir_path}/")
            else:
                print(f"   ❌ {dir_path}/ (不存在)")
        
        # 检查配置文件
        config_file = base_dir / "config/config.yaml"
        if config_file.exists():
            print(f"\n✅ 配置文件: {config_file}")
        else:
            print(f"\n❌ 配置文件不存在: {config_file}")
        
        # 检查数据
        data_dir = base_dir / "data/raw/daily"
        if data_dir.exists():
            daily_folders = list(data_dir.glob("*"))
            print(f"\n📊 数据归档: {len(daily_folders)} 天的数据")
            for folder in daily_folders[-3:]:  # 显示最近3天
                print(f"   • {folder.name}")
        else:
            print(f"\n📊 数据归档: 暂无数据")
        
        print(f"\n🕒 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 时区: UTC")
        
        year, week, weekday = datetime.now().isocalendar()
        print(f"📅 当前周数: {year}年第{week}周 (星期{weekday})")


def main():
    """主函数"""
    print("="*70)
    print("Telegram 聊天记录总结系统")
    print("="*70)
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description="Telegram 聊天记录总结系统")
    parser.add_argument("--daily", action="store_true", help="运行每日总结任务")
    parser.add_argument("--weekly", action="store_true", help="运行每周报告任务")
    parser.add_argument("--status", action="store_true", help="显示系统状态")
    parser.add_argument("--date", type=str, help="指定日期 (格式: YYYY-MM-DD)")
    parser.add_argument("--year", type=int, help="指定年份")
    parser.add_argument("--week", type=int, help="指定周数")
    
    args = parser.parse_args()
    
    try:
        # 初始化系统
        system = TelegramSummarySystem()
        
        if args.status:
            # 显示系统状态
            system.show_system_status()
        
        elif args.daily:
            # 运行每日任务
            target_date = None
            if args.date:
                try:
                    target_date = datetime.strptime(args.date, "%Y-%m-%d")
                except ValueError:
                    print(f"❌ 日期格式错误，请使用 YYYY-MM-DD 格式")
                    return
            
            system.run_daily_summary(target_date)
        
        elif args.weekly:
            # 运行每周任务
            system.run_weekly_report(args.year, args.week)
        
        else:
            # 默认显示帮助
            print("\n使用方法:")
            print("  python main.py --daily           # 运行每日总结")
            print("  python main.py --weekly          # 运行每周报告")
            print("  python main.py --status          # 显示系统状态")
            print("  python main.py --date 2024-01-01 # 指定日期运行")
            print("\n示例:")
            print("  python main.py --daily --date 2026-02-23")
            print("  python main.py --weekly --year 2026 --week 9")
    
    except Exception as e:
        print(f"\n❌ 系统错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()