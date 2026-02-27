#!/bin/bash
# Telegram 聊天记录总结系统 - 快速启动脚本

set -e

echo "================================================"
echo "Telegram 聊天记录总结系统 - 快速启动"
echo "================================================"

# 检查环境
echo -e "\n🔍 检查环境..."
python --version
openclaw --version

# 检查目录
echo -e "\n📁 检查目录结构..."
if [ -d "scripts" ]; then
    echo "✅ scripts/ 目录存在"
else
    echo "❌ scripts/ 目录不存在"
    exit 1
fi

if [ -f "config/config.yaml" ]; then
    echo "✅ config/config.yaml 存在"
else
    echo "❌ config/config.yaml 不存在"
    exit 1
fi

# 创建必要目录
echo -e "\n📂 创建目录..."
mkdir -p data/raw/daily
mkdir -p data/raw/weekly
mkdir -p data/processed/by_user
mkdir -p data/processed/by_week
mkdir -p summaries/daily
mkdir -p summaries/weekly
mkdir -p summaries/plans
mkdir -p logs

echo "✅ 目录结构创建完成"

# 测试系统
echo -e "\n🧪 测试系统..."
cd scripts

echo "1. 测试系统状态..."
/root/miniconda3/envs/dl/bin/python main.py --status

echo -e "\n2. 测试每日总结 (昨天)..."
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
/root/miniconda3/envs/dl/bin/python main.py --daily --date $YESTERDAY

echo -e "\n3. 查看生成的数据..."
echo "原始数据:"
ls -la ../data/raw/daily/
echo -e "\n处理后的数据:"
ls -la ../data/processed/by_user/8721157770/ 2>/dev/null || echo "暂无数据"
echo -e "\n工作计划:"
ls -la ../summaries/plans/8721157770/ 2>/dev/null || echo "暂无数据"

# 显示部署命令
echo -e "\n================================================"
echo "🚀 部署命令"
echo "================================================"

echo -e "\n📅 设置定时任务:"
echo ""
echo "# 每日任务 (早上8点 UTC)"
echo 'openclaw cron add --job '\''{"name":"telegram_daily_summary","schedule":{"kind":"cron","expr":"0 8 * * *","tz":"UTC"},"payload":{"kind":"agentTurn","message":"运行 Telegram 每日总结任务。使用命令: cd /root/.openclaw/workspace/telegram_summary/scripts && /root/miniconda3/envs/dl/bin/python main.py --daily","model":"deepseek/deepseek-chat","thinking":"off"},"sessionTarget":"isolated","enabled":true,"delivery":{"mode":"announce","channel":"telegram","to":"8721157770","bestEffort":true}}'\'''
echo ""
echo "# 每周任务 (周五下午6点 UTC)"
echo 'openclaw cron add --job '\''{"name":"telegram_weekly_report","schedule":{"kind":"cron","expr":"0 18 * * 5","tz":"UTC"},"payload":{"kind":"agentTurn","message":"运行 Telegram 每周报告任务。使用命令: cd /root/.openclaw/workspace/telegram_summary/scripts && /root/miniconda3/envs/dl/bin/python main.py --weekly","model":"deepseek/deepseek-chat","thinking":"off"},"sessionTarget":"isolated","enabled":true,"delivery":{"mode":"announce","channel":"telegram","to":"8721157770","bestEffort":true}}'\'''
echo ""

echo -e "\n🔧 手动运行命令:"
echo ""
echo "# 查看系统状态"
echo "cd /root/.openclaw/workspace/telegram_summary/scripts"
echo "/root/miniconda3/envs/dl/bin/python main.py --status"
echo ""
echo "# 运行每日总结"
echo "cd /root/.openclaw/workspace/telegram_summary/scripts"
echo "/root/miniconda3/envs/dl/bin/python main.py --daily"
echo ""
echo "# 运行每周报告"
echo "cd /root/.openclaw/workspace/telegram_summary/scripts"
echo "/root/miniconda3/envs/dl/bin/python main.py --weekly"

echo -e "\n📝 查看文档:"
echo "cat ../DEPLOYMENT.md | head -50"

echo -e "\n================================================"
echo "✅ 快速启动完成"
echo "================================================"
echo ""
echo "下一步:"
echo "1. 运行上面的定时任务命令"
echo "2. 系统将在指定时间自动运行"
echo "3. 通过 Telegram 接收通知"
echo ""