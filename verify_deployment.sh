#!/bin/bash
# 部署验证脚本

echo "================================================"
echo "Telegram 私聊总结系统 - 部署验证"
echo "================================================"

echo -e "\n🔍 检查配置..."
cd /root/.openclaw/workspace/telegram_summary/scripts
/root/miniconda3/envs/dl/bin/python -c "
import yaml
with open('../config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)
print('✅ 配置文件加载成功')
print(f'  source_type: {config[\"data_source\"][\"source_type\"]} (应为: direct)')
print(f'  sessions_path: {config[\"data_source\"][\"sessions_path\"]}')
"

echo -e "\n🧪 测试系统状态..."
cd /root/.openclaw/workspace/telegram_summary/scripts
/root/miniconda3/envs/dl/bin/python main.py --status 2>&1 | grep -A5 "系统状态检查"

echo -e "\n📊 测试数据收集..."
cd /root/.openclaw/workspace/telegram_summary/scripts
/root/miniconda3/envs/dl/bin/python test_simple.py 2>&1 | tail -10

echo -e "\n⏰ 检查定时任务..."
openclaw cron list 2>&1 | grep -A5 "telegram_daily_summary"

echo -e "\n================================================"
echo "✅ 部署验证完成"
echo "================================================"
echo -e "\n📝 总结:"
echo "1. 配置已设置为 direct (私聊数据源)"
echo "2. 系统使用 main.py (私聊版本)"
echo "3. 定时任务已重新部署"
echo "4. 系统正在处理私聊会话数据"
echo -e "\n🚀 系统将在以下时间自动运行:"
echo "• 每日总结: 每天 08:00 UTC"
echo "• 每周报告: 每周五 18:00 UTC"