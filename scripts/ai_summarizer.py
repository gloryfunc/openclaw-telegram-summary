#!/usr/bin/env python3
"""
AI 总结生成器
基于现有对话生成总结和计划
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import asdict

from data_models import DailySummary, WeeklyReport, WorkPlan, Message, MessageType


class AISummarizer:
    """AI 总结生成器"""
    
    def __init__(self, model: str = "deepseek/deepseek-chat"):
        """
        初始化 AI 总结器
        
        Args:
            model: 使用的 AI 模型
        """
        self.model = model
    
    def generate_daily_summary_text(self, summary: DailySummary, messages: List[Message]) -> str:
        """
        生成每日总结文本
        
        Args:
            summary: 每日总结数据
            messages: 当日消息列表
            
        Returns:
            总结文本
        """
        # 构建提示词
        prompt = self._build_daily_summary_prompt(summary, messages)
        
        # 这里应该调用 AI API，但为了演示，我们生成一个模拟响应
        # 实际实现应该使用 OpenClaw 的 AI 工具
        
        return self._simulate_ai_response(prompt, "daily_summary")
    
    def generate_work_plan(self, summary: DailySummary, previous_plan: Optional[WorkPlan] = None) -> WorkPlan:
        """
        生成工作计划
        
        Args:
            summary: 每日总结
            previous_plan: 前一天的计划（可选）
            
        Returns:
            工作计划
        """
        # 基于总结内容生成计划
        plan_date = summary.date + timedelta(days=1)  # 第二天的计划
        
        # 从总结中提取任务
        priority_tasks = []
        follow_up_tasks = []
        new_tasks = []
        reminders = []
        
        # 分析总结内容生成任务
        if summary.tasks_mentioned:
            priority_tasks = summary.tasks_mentioned[:3]
        
        if summary.decisions_made:
            follow_up_tasks = [f"跟进: {decision}" for decision in summary.decisions_made[:2]]
        
        if summary.key_topics:
            new_tasks = [f"深入研究: {topic}" for topic in summary.key_topics[:2]]
        
        # 生成计划文本
        plan_text = self._generate_plan_text(plan_date, priority_tasks, follow_up_tasks, new_tasks)
        
        # 创建工作计划对象
        work_plan = WorkPlan(
            date=plan_date,
            user_id=summary.user_id,
            priority_tasks=priority_tasks,
            follow_up_tasks=follow_up_tasks,
            new_tasks=new_tasks,
            reminders=reminders,
            plan_text=plan_text
        )
        
        return work_plan
    
    def generate_weekly_report(self, daily_summaries: List[DailySummary], messages: List[Message]) -> WeeklyReport:
        """
        生成每周报告
        
        Args:
            daily_summaries: 本周的每日总结列表
            messages: 本周的所有消息
            
        Returns:
            每周报告
        """
        if not daily_summaries:
            raise ValueError("没有每日总结数据")
        
        # 使用第一个总结的日期确定周数
        first_date = daily_summaries[0].date
        year, week, _ = first_date.isocalendar()
        
        # 计算开始和结束日期
        start_date = first_date - timedelta(days=first_date.weekday())
        end_date = start_date + timedelta(days=6)
        
        # 统计信息
        total_messages = sum(s.total_messages for s in daily_summaries)
        total_sessions = len(set(s.user_id for s in daily_summaries))
        
        # 提取活跃用户
        active_users = list(set(s.user_id for s in daily_summaries))
        
        # 提取每周亮点
        weekly_highlights = self._extract_weekly_highlights(daily_summaries)
        
        # 生成下周计划
        next_week_plan = self._generate_next_week_plan(daily_summaries)
        
        # 生成报告文本
        report_text = self._generate_weekly_report_text(
            year, week, daily_summaries, weekly_highlights, next_week_plan
        )
        
        # 创建每周报告对象
        weekly_report = WeeklyReport(
            year=year,
            week=week,
            start_date=start_date,
            end_date=end_date,
            total_sessions=total_sessions,
            total_messages=total_messages,
            active_users=active_users,
            daily_summaries=daily_summaries,
            weekly_highlights=weekly_highlights,
            next_week_plan=next_week_plan,
            report_text=report_text
        )
        
        return weekly_report
    
    def _build_daily_summary_prompt(self, summary: DailySummary, messages: List[Message]) -> str:
        """构建每日总结提示词"""
        # 检查是否为群组总结
        is_group = hasattr(summary, 'metadata') and summary.metadata.get('is_group', False)
        
        if is_group:
            return self._build_group_daily_summary_prompt(summary, messages)
        
        # 私聊总结提示词
        conversation_text = "\n".join([
            f"{msg.user_name} ({msg.timestamp.strftime('%H:%M')}): {msg.content[:100]}..."
            for msg in messages[-10:]  # 只使用最后10条消息
        ])
        
        prompt = f"""基于以下对话记录，生成一份简洁的每日总结：

对话记录：
{conversation_text}

统计信息：
- 总消息数: {summary.total_messages}
- 用户消息: {summary.user_messages}
- 助手消息: {summary.assistant_messages}
- 关键话题: {', '.join(summary.key_topics)}
- 提到的任务: {', '.join(summary.tasks_mentioned[:3])}
- 做出的决定: {', '.join(summary.decisions_made[:2])}

请生成一份包含以下部分的总结：
1. 主要讨论内容
2. 完成的工作
3. 提出的问题
4. 达成的共识
5. 下一步建议

总结语言：中文，简洁明了，突出重点。"""
        
        return prompt
    
    def _build_group_daily_summary_prompt(self, summary: DailySummary, messages: List[Message]) -> str:
        """构建群组每日总结提示词"""
        # 提取群组对话内容
        conversation_text = "\n".join([
            f"{msg.user_name} ({msg.timestamp.strftime('%H:%M')}): {msg.content[:80]}..."
            for msg in messages[-15:]  # 群组使用更多消息
        ])
        
        # 提取用户活跃度
        user_stats = summary.metadata.get('user_statistics', [])
        active_users = sorted(user_stats, key=lambda x: x['count'], reverse=True)[:5]
        
        active_users_text = "\n".join([
            f"  {i}. {user.get('user_name', '未知用户')}: {user['count']} 条消息"
            for i, user in enumerate(active_users, 1)
        ])
        
        group_name = summary.metadata.get('group_name', '未知群组')
        participant_count = summary.metadata.get('participant_count', 0)
        
        prompt = f"""基于以下群组对话记录，生成一份简洁的群组每日总结：

群组名称: {group_name}
参与人数: {participant_count} 人

对话记录（最近消息）：
{conversation_text}

统计信息：
- 总消息数: {summary.total_messages}
- 关键话题: {', '.join(summary.key_topics)}
- 提到的任务: {', '.join(summary.tasks_mentioned[:3])}
- 做出的决定: {', '.join(summary.decisions_made[:2])}

用户活跃度排名：
{active_users_text}

请生成一份包含以下部分的群组总结：
1. 群组今日主要讨论内容
2. 各成员贡献和活跃度
3. 讨论的技术或业务重点
4. 达成的共识和决策
5. 需要跟进的事项
6. 明日讨论建议

总结语言：中文，专业且具有洞察力，突出群组协作特点。"""
        
        return prompt
    
    def _simulate_ai_response(self, prompt: str, response_type: str) -> str:
        """模拟 AI 响应（实际应调用 AI API）"""
        
        if response_type == "daily_summary":
            return """## 每日对话总结

### 1. 主要讨论内容
- LeetCode 30题（串联所有单词的子串）的解题实现
- Python 深度学习环境的搭建和配置
- Telegram 聊天记录总结系统的可行性分析

### 2. 完成的工作
- 成功实现了 LeetCode 30题的完整解题代码，包含测试用例和性能测试
- 搭建了完整的 Python 深度学习环境（Miniconda + PyTorch + TensorFlow）
- 设计了 Telegram 聊天记录总结系统的架构和基础框架

### 3. 提出的问题
- Telegram Bot API 获取历史消息的可行性
- 数据存储和归档的方案设计
- 定时任务调度的实现方式

### 4. 达成的共识
- 使用 OpenClaw 的会话文件作为数据源
- 采用 JSONL 格式进行数据存储
- 按日/周进行数据归档和组织

### 5. 下一步建议
- 完善 AI 总结生成功能
- 实现定时任务调度
- 测试端到端的工作流程"""
        
        elif response_type == "weekly_report":
            return """## 本周工作报告

### 本周概览
本周主要围绕技术实现和系统设计展开，完成了多个重要模块的开发。

### 主要成就
1. **LeetCode 解题系统**：实现了完整的解题框架，包含测试和性能优化
2. **深度学习环境**：成功搭建了 PyTorch 和 TensorFlow 开发环境
3. **数据管理系统**：设计了基于 OpenClaw 的数据收集和归档系统

### 技术进展
- 掌握了 OpenClaw 会话文件的解析方法
- 实现了 JSONL 数据格式的处理
- 设计了可扩展的数据存储架构

### 遇到的问题
- Telegram API 权限限制
- 多会话数据获取的挑战
- 定时任务调度的复杂性

### 下周计划
1. 完善 AI 总结生成功能
2. 实现消息推送系统
3. 进行系统集成测试
4. 编写用户文档"""
        
        else:
            return "AI 总结生成功能待实现"
    
    def _generate_plan_text(self, date: datetime, priority_tasks: List[str], 
                           follow_up_tasks: List[str], new_tasks: List[str]) -> str:
        """生成计划文本"""
        plan_date = date.strftime("%Y年%m月%d日")
        
        text = f"""# {plan_date} 工作计划

## 优先任务
{self._format_task_list(priority_tasks)}

## 跟进任务
{self._format_task_list(follow_up_tasks)}

## 新任务/学习
{self._format_task_list(new_tasks)}

## 提醒事项
- 检查昨日任务的完成情况
- 更新工作进度记录
- 准备明日计划"""

        return text
    
    def _format_task_list(self, tasks: List[str]) -> str:
        """格式化任务列表"""
        if not tasks:
            return "- 无"
        
        return "\n".join([f"- {task}" for task in tasks])
    
    def _extract_weekly_highlights(self, daily_summaries: List[DailySummary]) -> List[str]:
        """提取每周亮点"""
        highlights = []
        
        for summary in daily_summaries:
            if summary.key_topics:
                highlights.extend(summary.key_topics)
            if summary.tasks_mentioned:
                highlights.extend(summary.tasks_mentioned[:2])
        
        # 去重并限制数量
        return list(set(highlights))[:5]
    
    def _generate_next_week_plan(self, daily_summaries: List[DailySummary]) -> List[str]:
        """生成下周计划"""
        plan_items = []
        
        # 基于本周总结生成下周计划
        all_topics = []
        all_tasks = []
        
        for summary in daily_summaries:
            all_topics.extend(summary.key_topics)
            all_tasks.extend(summary.tasks_mentioned)
        
        # 提取独特的话题和任务
        unique_topics = list(set(all_topics))[:3]
        unique_tasks = list(set(all_tasks))[:3]
        
        # 生成计划项
        for topic in unique_topics:
            plan_items.append(f"深入研究: {topic}")
        
        for task in unique_tasks:
            plan_items.append(f"完成: {task}")
        
        plan_items.append("进行系统性能测试")
        plan_items.append("编写用户使用文档")
        
        return plan_items[:5]
    
    def _generate_weekly_report_text(self, year: int, week: int, daily_summaries: List[DailySummary],
                                    weekly_highlights: List[str], next_week_plan: List[str]) -> str:
        """生成每周报告文本"""
        return f"""# {year}年第{week}周工作报告

## 本周概览
本周共进行了 {len(daily_summaries)} 天的有效对话，涵盖了多个技术主题的开发工作。

## 主要亮点
{self._format_task_list(weekly_highlights)}

## 每日进展
{self._format_daily_progress(daily_summaries)}

## 遇到的问题和解决方案
1. **数据源限制**：发现只能访问当前会话的历史记录
2. **技术验证**：成功验证了 OpenClaw 会话文件的可用性
3. **架构设计**：完成了系统的整体架构设计

## 下周计划
{self._format_task_list(next_week_plan)}

## 总结
本周在技术实现和系统设计方面取得了显著进展，为后续开发奠定了坚实基础。"""
    
    def _format_daily_progress(self, daily_summaries: List[DailySummary]) -> str:
        """格式化每日进展"""
        lines = []
        for summary in daily_summaries:
            date_str = summary.date.strftime("%m月%d日")
            topics = ", ".join(summary.key_topics[:2]) if summary.key_topics else "无特定主题"
            lines.append(f"- {date_str}: {topics} ({summary.total_messages} 条消息)")
        
        return "\n".join(lines)


def test_summarizer():
    """测试总结生成器"""
    try:
        print("初始化 AI 总结生成器...")
        summarizer = AISummarizer()
        
        # 创建测试数据
        test_date = datetime.now() - timedelta(days=1)
        
        # 创建测试消息
        test_messages = [
            Message(
                id="1",
                timestamp=test_date,
                message_type=MessageType.USER,
                content="请帮我实现一个 LeetCode 解题系统",
                user_id="8721157770",
                user_name="gray"
            ),
            Message(
                id="2",
                timestamp=test_date,
                message_type=MessageType.ASSISTANT,
                content="好的，我来实现 LeetCode 30题的解题代码",
                user_id="assistant",
                user_name="助手"
            )
        ]
        
        # 创建测试总结
        test_summary = DailySummary(
            date=test_date,
            user_id="8721157770",
            total_messages=10,
            user_messages=5,
            assistant_messages=5,
            key_topics=["LeetCode 解题", "Python 编程"],
            tasks_mentioned=["实现 LeetCode 30题", "编写测试用例"],
            decisions_made=["使用滑动窗口算法", "采用 Counter 进行频率统计"]
        )
        
        print("\n测试生成每日总结...")
        summary_text = summarizer.generate_daily_summary_text(test_summary, test_messages)
        print("每日总结生成成功:")
        print(summary_text[:200] + "...")
        
        print("\n测试生成工作计划...")
        work_plan = summarizer.generate_work_plan(test_summary)
        print("工作计划生成成功:")
        print(f"- 日期: {work_plan.date.date()}")
        print(f"- 优先任务: {work_plan.priority_tasks}")
        print(f"- 计划文本长度: {len(work_plan.plan_text)} 字符")
        
        print("\n测试生成每周报告...")
        weekly_report = summarizer.generate_weekly_report([test_summary], test_messages)
        print("每周报告生成成功:")
        print(f"- 年份: {weekly_report.year}")
        print(f"- 周数: {weekly_report.week}")
        print(f"- 总消息数: {weekly_report.total_messages}")
        print(f"- 报告文本长度: {len(weekly_report.report_text)} 字符")
        
        print("\n所有测试完成!")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_summarizer()