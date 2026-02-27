#!/usr/bin/env python3
"""
Telegram 群组聊天记录总结系统 - 主入口
专门处理群组聊天记录
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from group_data_manager import GroupDataManager
from ai_summarizer import AISummarizer


class TelegramGroupSummarySystem:
    """Telegram 群组聊天记录总结系统"""
    
    def __init__(self, config_path: str = "../config/config.yaml"):
        """
        初始化群组总结系统
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.group_manager = None
        self.summarizer = None
        self._init_system()
    
    def _init_system(self):
        """初始化系统组件"""
        print("初始化 Telegram 群组聊天记录总结系统...")
        
        try:
            self.group_manager = GroupDataManager(self.config_path)
            self.summarizer = AISummarizer()
            print("✅ 群组系统初始化成功")
        except Exception as e:
            print(f"❌ 群组系统初始化失败: {e}")
            raise
    
    def run_group_daily_summary(self, target_date: datetime = None):
        """
        运行群组每日总结任务
        
        Args:
            target_date: 目标日期，默认为昨天
        """
        print(f"\n{'='*60}")
        print(f"执行群组每日总结任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        if target_date is None:
            target_date = datetime.now() - timedelta(days=1)
        
        date_str = target_date.strftime("%Y-%m-%d")
        print(f"📅 处理日期: {date_str}")
        
        try:
            # 1. 查找目标群组
            print("\n1. 🔍 查找目标群组...")
            target_group = self.group_manager.find_target_group()
            
            if not target_group:
                print("   ❌ 未找到目标群组")
                self.group_manager.log_group_activity(
                    "daily_summary", 
                    self.group_manager.target_group,
                    f"未找到目标群组: {self.group_manager.target_group}"
                )
                return
            
            print(f"   ✅ 找到目标群组: {target_group.display_name}")
            print(f"     参与者: {len(target_group.participants)} 人")
            print(f"     消息总数: {len(target_group.messages)} 条")
            
            # 2. 收集群组每日数据
            print("\n2. 📊 收集群组每日数据...")
            daily_session = self.group_manager.collect_group_daily_data(target_group, target_date)
            
            if not daily_session:
                print(f"   ℹ️ 群组在 {date_str} 没有消息")
                self.group_manager.log_group_activity(
                    "daily_summary",
                    target_group.display_name,
                    f"群组在 {date_str} 没有消息"
                )
                return
            
            print(f"   ✅ 收集到 {len(daily_session.messages)} 条当日消息")
            
            # 3. 归档群组数据
            print("\n3. 📁 归档群组数据...")
            self.group_manager.archive_group_data(daily_session, "daily")
            print("   ✅ 群组数据归档完成")
            
            # 4. 分析群组活动
            print("\n4. 📈 分析群组活动...")
            analysis = self.group_manager.analyze_group_daily_activity(daily_session)
            print(f"   ✅ 群组活动分析完成")
            print(f"     活跃用户: {analysis.get('total_participants', 0)} 人")
            
            # 5. 生成群组总结
            print("\n5. 📝 生成群组总结...")
            summary = self.group_manager.generate_group_daily_summary(daily_session, analysis)
            
            # 生成总结文本
            summary_text = self.summarizer.generate_daily_summary_text(summary, daily_session.messages)
            summary.summary_text = summary_text
            
            # 保存群组总结
            self.group_manager.save_group_summary(summary, "daily")
            print("   ✅ 群组总结保存完成")
            
            # 6. 发送通知
            print("\n6. 📨 准备发送通知...")
            self._send_group_notification(summary, analysis)
            
            # 记录成功日志
            self.group_manager.log_group_activity(
                "daily_summary",
                target_group.display_name,
                f"成功生成 {date_str} 群组总结，{len(daily_session.messages)} 条消息"
            )
            
            print(f"\n🎉 群组每日总结任务完成! 处理了 {target_group.display_name}")
            
        except Exception as e:
            error_msg = f"群组每日总结任务失败: {str(e)}"
            print(f"\n❌ {error_msg}")
            
            # 记录错误日志
            self.group_manager.log_group_activity(
                "daily_summary_error",
                self.group_manager.target_group,
                error_msg
            )
            raise
    
    def run_group_weekly_report(self, target_year: int = None, target_week: int = None):
        """
        运行群组每周报告任务
        
        Args:
            target_year: 目标年份
            target_week: 目标周数
        """
        print(f"\n{'='*60}")
        print(f"执行群组每周报告任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        if target_year is None or target_week is None:
            today = datetime.now()
            target_year, target_week, _ = today.isocalendar()
        
        print(f"📅 处理周数: {target_year}年第{target_week}周")
        
        try:
            # 1. 查找目标群组
            print("\n1. 🔍 查找目标群组...")
            target_group = self.group_manager.find_target_group()
            
            if not target_group:
                print("   ❌ 未找到目标群组")
                return
            
            # 2. 收集群组每周数据
            print("\n2. 📊 收集群组每周数据...")
            weekly_session = self.group_manager.collect_group_weekly_data(target_group, target_year, target_week)
            
            if not weekly_session:
                print(f"   ℹ️ 群组在 {target_year}年第{target_week}周没有消息")
                return
            
            print(f"   ✅ 收集到 {len(weekly_session.messages)} 条当周消息")
            
            # 3. 归档群组数据
            print("\n3. 📁 归档群组数据...")
            self.group_manager.archive_group_data(weekly_session, "weekly")
            print("   ✅ 群组数据归档完成")
            
            # 4. 生成群组周报
            print("\n4. 📊 生成群组周报...")
            
            # 这里应该从存储加载本周的每日总结
            # 为了演示，我们创建模拟数据
            mock_summaries = []
            all_messages = weekly_session.messages
            
            if all_messages:
                # 创建模拟的每日总结
                from data_models import DailySummary
                
                # 按日期分组消息
                messages_by_date = {}
                for msg in all_messages:
                    date_key = msg.timestamp.date()
                    if date_key not in messages_by_date:
                        messages_by_date[date_key] = []
                    messages_by_date[date_key].append(msg)
                
                # 为每天创建总结
                for date_key, date_messages in messages_by_date.items():
                    mock_summary = DailySummary(
                        date=datetime.combine(date_key, datetime.min.time()),
                        user_id="group",
                        total_messages=len(date_messages),
                        user_messages=len(date_messages),
                        assistant_messages=0,
                        key_topics=["群组讨论", "项目进展"],
                        tasks_mentioned=["任务分配", "进度跟踪"],
                        decisions_made=["技术决策", "项目规划"]
                    )
                    mock_summaries.append(mock_summary)
                
                # 生成每周报告
                weekly_report = self.summarizer.generate_weekly_report(mock_summaries, all_messages)
                
                # 保存群组周报
                self.group_manager.save_group_summary(weekly_report, "weekly")
                print("   ✅ 群组周报保存完成")
                
                # 5. 发送通知
                print("\n5. 📨 准备发送周报通知...")
                self._send_weekly_notification(weekly_report)
            
            # 记录成功日志
            self.group_manager.log_group_activity(
                "weekly_report",
                target_group.display_name,
                f"成功生成 {target_year}年第{target_week}周群组周报"
            )
            
            print(f"\n🎉 群组每周报告任务完成! 处理了 {target_group.display_name}")
            
        except Exception as e:
            error_msg = f"群组每周报告任务失败: {str(e)}"
            print(f"\n❌ {error_msg}")
            
            # 记录错误日志
            self.group_manager.log_group_activity(
                "weekly_report_error",
                self.group_manager.target_group,
                error_msg
            )
            raise
    
    def _send_group_notification(self, summary, analysis):
        """发送群组通知"""
        try:
            # 构建群组通知消息
            notification = f"""
👥 群组每日总结通知 - {summary.date.strftime('%Y年%m月%d日')}

🏢 群组: {summary.metadata.get('group_name', '未知群组')}

📊 群组活动统计:
• 总消息数: {summary.total_messages}
• 活跃用户: {summary.metadata.get('participant_count', 0)} 人
• 关键话题: {', '.join(summary.key_topics[:3]) if summary.key_topics else '无'}

👤 用户活跃度排名:"""
            
            # 添加用户排名
            user_stats = summary.metadata.get('user_statistics', [])
            if user_stats:
                sorted_users = sorted(user_stats, key=lambda x: x['count'], reverse=True)
                for i, user in enumerate(sorted_users[:3], 1):
                    notification += f"\n  {i}. {user.get('user_name', '未知用户')}: {user['count']} 条"
            
            notification += f"""

📋 群组讨论摘要已生成，详细总结已保存到系统。
"""
            
            print(f"\n     📨 群组通知内容:")
            print(f"     {notification[:150]}...")
            
            # 实际应该使用 OpenClaw 的 message 工具发送
            # 这里只打印演示
            
        except Exception as e:
            print(f"     ❌ 构建群组通知失败: {e}")
    
    def _send_weekly_notification(self, weekly_report):
        """发送群组周报通知"""
        try:
            notification = f"""
👥 群组每周报告通知 - {weekly_report.year}年第{weekly_report.week}周

📈 本周群组概览:
• 活跃天数: {len(weekly_report.daily_summaries)}
• 总消息数: {weekly_report.total_messages}
• 活跃用户: {len(weekly_report.active_users)} 人

🏆 本周群组工作已汇总，下周计划已制定。

完整群组周报已保存到系统，请查看详细内容。
"""
            
            print(f"\n     📨 群组周报通知:")
            print(f"     {notification[:100]}...")
            
        except Exception as e:
            print(f"     ❌ 构建群组周报通知失败: {e}")
    
    def show_system_status(self):
        """显示群组系统状态"""
        print(f"\n{'='*60}")
        print("群组系统状态检查")
        print(f"{'='*60}")
        
        # 检查目录
        base_dir = Path("../")
        group_dirs = [
            "data/group",
            "data/group/raw",
            "data/group/processed",
            "data/group/summaries",
            "data/group/logs"
        ]
        
        print("\n📁 群组目录结构检查:")
        for dir_path in group_dirs:
            full_path = base_dir / dir_path
            if full_path.exists():
                print(f"   ✅ {dir_path}/")
            else:
                print(f"   ❌ {dir_path}/ (缺失)")
        
        # 检查配置文件
        config_file = base_dir / "config/config.yaml"
        if config_file.exists():
            print(f"\n✅ 配置文件: {config_file}")
            
            # 检查群组配置
            import yaml
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            target_group = config.get("group", {}).get("target_group", "未设置")
            print(f"✅ 目标群组配置: {target_group}")
        else:
            print(f"\n❌ 配置文件不存在: {config_file}")
        
        # 检查数据
        group_data_dir = base_dir / "data/group/raw/daily"
        if group_data_dir.exists():
            daily_folders = list(group_data_dir.glob("*"))
            print(f"\n📊 群组数据归档: {len(daily_folders)} 天的数据")
        else:
            print(f"\n📊 群组数据归档: 暂无数据")
        
        print(f"\n🕒 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 时区: UTC")
        
        year, week, weekday = datetime.now().isocalendar()
        print(f"📅 当前周数: {year}年第{week}周 (星期{weekday})")
        
        print(f"\n🎯 目标群组: {self.group_manager.target_group}")


def main():
    """主函数"""
    print("="*70)
    print("Telegram 群组聊天记录总结系统")
    print("="*70)
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description="Telegram 群组聊天记录总结系统")
    parser.add_argument("--daily", action="store_true", help="运行群组每日总结任务")
    parser.add_argument("--weekly", action="store_true", help="运行群组每周报告任务")
    parser.add_argument("--status", action="store_true", help="显示群组系统状态")
    parser.add_argument("--date", type=str, help="指定日期 (格式: YYYY-MM-DD)")
    parser.add_argument("--year", type=int, help="指定年份")
    parser.add_argument("--week", type=int, help="指定周数")
    
    args = parser.parse_args()
    
    try:
        # 初始化系统
        system = TelegramGroupSummarySystem()
        
        if args.status:
            # 显示系统状态
            system.show_system_status()
        
        elif args.daily:
            # 运行群组每日任务
            target_date = None
            if args.date:
                try:
                    target_date = datetime.strptime(args.date, "%Y-%m-%d")
                except ValueError:
                    print(f"❌ 日期格式错误，请使用 YYYY-MM-DD 格式")
                    return
            
            system.run_group_daily_summary(target_date)
        
        elif args.weekly:
            # 运行群组每周任务
            system.run_group_weekly_report(args.year, args.week)
        
        else:
            # 默认显示帮助
            print("\n使用方法:")
            print("  python main_group.py --daily           # 运行群组每日总结")
            print("  python main_group.py --weekly          # 运行群组每周报告")
            print("  python main_group.py --status          # 显示群组系统状态")
            print("  python main_group.py --date 2024-01-01 # 指定日期运行")
            print("\n示例:")
            print("  python main_group.py --daily --date 2026-02-23")
            print("  python main_group.py --weekly --year 2026 --week 9")
            print("\n注意: 需要将bot添加到目标群组并确保有消息记录")
    
    except Exception as e:
        print(f"\n❌ 群组系统错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()