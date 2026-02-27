#!/usr/bin/env python3
"""
设置 OpenClaw cron 任务
"""

import json
from datetime import datetime

def create_cron_jobs():
    """创建 cron 任务配置"""
    
    # 每日任务配置 (早上8点 UTC)
    daily_job = {
        "name": "telegram_daily_summary",
        "schedule": {
            "kind": "cron",
            "expr": "0 8 * * *",  # 每天8:00 UTC
            "tz": "UTC"
        },
        "payload": {
            "kind": "agentTurn",
            "message": "运行 Telegram 每日总结任务。使用命令: cd /root/.openclaw/workspace/telegram_summary/scripts && /root/miniconda3/envs/dl/bin/python main.py --daily",
            "model": "deepseek/deepseek-chat",
            "thinking": "off"
        },
        "sessionTarget": "isolated",
        "enabled": True,
        "delivery": {
            "mode": "announce",
            "channel": "telegram",
            "to": "8721157770",
            "bestEffort": True
        }
    }
    
    # 每周任务配置 (周五下午6点 UTC)
    weekly_job = {
        "name": "telegram_weekly_report", 
        "schedule": {
            "kind": "cron",
            "expr": "0 18 * * 5",  # 每周五18:00 UTC
            "tz": "UTC"
        },
        "payload": {
            "kind": "agentTurn",
            "message": "运行 Telegram 每周报告任务。使用命令: cd /root/.openclaw/workspace/telegram_summary/scripts && /root/miniconda3/envs/dl/bin/python main.py --weekly",
            "model": "deepseek/deepseek-chat",
            "thinking": "off"
        },
        "sessionTarget": "isolated",
        "enabled": True,
        "delivery": {
            "mode": "announce",
            "channel": "telegram",
            "to": "8721157770",
            "bestEffort": True
        }
    }
    
    return {
        "daily": daily_job,
        "weekly": weekly_job
    }

def generate_setup_commands():
    """生成设置命令"""
    
    jobs = create_cron_jobs()
    
    print("="*70)
    print("Telegram 总结系统 - Cron 任务设置")
    print("="*70)
    
    print("\n📋 任务配置:")
    
    print("\n1. 每日任务 (早上8点 UTC):")
    print(f"   名称: {jobs['daily']['name']}")
    print(f"   时间: {jobs['daily']['schedule']['expr']}")
    print(f"   时区: {jobs['daily']['schedule']['tz']}")
    
    print("\n2. 每周任务 (周五下午6点 UTC):")
    print(f"   名称: {jobs['weekly']['name']}")
    print(f"   时间: {jobs['weekly']['schedule']['expr']}")
    print(f"   时区: {jobs['weekly']['schedule']['tz']}")
    
    print("\n🚀 设置命令:")
    print("\n# 1. 首先检查当前 cron 状态")
    print("openclaw cron status")
    
    print("\n# 2. 添加每日任务")
    daily_cmd = f"""openclaw cron add --job '{json.dumps(jobs['daily'], ensure_ascii=False)}'"""
    print(daily_cmd)
    
    print("\n# 3. 添加每周任务")
    weekly_cmd = f"""openclaw cron add --job '{json.dumps(jobs['weekly'], ensure_ascii=False)}'"""
    print(weekly_cmd)
    
    print("\n# 4. 验证任务列表")
    print("openclaw cron list")
    
    print("\n# 5. 手动测试任务 (可选)")
    print("# 测试每日任务:")
    print("openclaw cron run --jobId <daily-job-id>")
    print("\n# 测试每周任务:")
    print("openclaw cron run --jobId <weekly-job-id>")
    
    print("\n📁 配置文件:")
    print("\n将以下配置保存到 cron_jobs.json:")
    
    config_file = {
        "jobs": jobs,
        "created_at": datetime.now().isoformat(),
        "description": "Telegram 聊天记录总结系统定时任务",
        "notes": [
            "每日任务: 早上8点生成前一天的总结和计划",
            "每周任务: 周五下午6点生成周报",
            "所有输出会推送到 Telegram 用户 8721157770"
        ]
    }
    
    print(json.dumps(config_file, ensure_ascii=False, indent=2))
    
    print("\n🔧 手动运行命令:")
    print("\n# 运行每日总结")
    print("cd /root/.openclaw/workspace/telegram_summary/scripts")
    print("/root/miniconda3/envs/dl/bin/python main.py --daily")
    
    print("\n# 运行每周报告")
    print("cd /root/.openclaw/workspace/telegram_summary/scripts")
    print("/root/miniconda3/envs/dl/bin/python main.py --weekly")
    
    print("\n# 查看系统状态")
    print("cd /root/.openclaw/workspace/telegram_summary/scripts")
    print("/root/miniconda3/envs/dl/bin/python main.py --status")
    
    print("\n📝 注意事项:")
    print("1. 确保 OpenClaw Gateway 正在运行")
    print("2. 确保 Python 环境正确配置")
    print("3. 确保有足够的磁盘空间存储数据")
    print("4. 系统日志保存在 telegram_summary/logs/ 目录")
    
    print("\n" + "="*70)
    print("设置完成")
    print("="*70)

if __name__ == "__main__":
    generate_setup_commands()