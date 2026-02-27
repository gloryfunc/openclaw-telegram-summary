#!/bin/bash
# Telegram 群组总结系统 - 部署脚本

set -e

echo "================================================"
echo "Telegram 群组聊天记录总结系统 - 部署"
echo "================================================"

# 检查环境
echo -e "\n🔍 检查环境..."
/root/miniconda3/envs/dl/bin/python --version

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
    
    # 检查群组配置
    echo -e "\n🎯 检查群组配置..."
    TARGET_GROUP=$(grep -A1 "target_group" config/config.yaml | tail -1 | tr -d ' :' || echo "未设置")
    echo "目标群组: $TARGET_GROUP"
else
    echo "❌ config/config.yaml 不存在"
    exit 1
fi

# 创建群组数据目录
echo -e "\n📂 创建群组数据目录..."
mkdir -p data/group/raw/daily
mkdir -p data/group/raw/weekly
mkdir -p data/group/processed
mkdir -p data/group/summaries/daily
mkdir -p data/group/summaries/weekly
mkdir -p data/group/logs

echo "✅ 群组目录结构创建完成"

# 测试群组系统
echo -e "\n🧪 测试群组系统..."
cd scripts

echo "1. 测试群组系统状态..."
/root/miniconda3/envs/dl/bin/python main_group.py --status

echo -e "\n2. 测试群组数据解析..."
/root/miniconda3/envs/dl/bin/python group_data_manager.py

# 显示部署命令
echo -e "\n================================================"
echo "🚀 群组系统部署命令"
echo "================================================"

echo -e "\n📅 设置群组定时任务:"

echo -e "\n# 删除旧的私聊任务（如果需要）"
echo "openclaw cron remove --jobId 7f5bac75-c30d-4406-99f4-4eb24150daf9"
echo "openclaw cron remove --jobId c60218f2-ec3b-481d-8d6a-2e33c1d4c645"

echo -e "\n# 添加群组每日任务 (早上8点 UTC)"
echo 'openclaw cron add --name "telegram_group_daily_summary" --cron "0 8 * * *" --tz "UTC" --session "isolated" --message "运行 Telegram 群组每日总结任务。使用命令: cd /root/.openclaw/workspace/telegram_summary/scripts && /root/miniconda3/envs/dl/bin/python main_group.py --daily" --model "deepseek/deepseek-chat" --thinking "off" --announce --channel "telegram" --to "8721157770" --best-effort-deliver'

echo -e "\n# 添加群组每周任务 (周五下午6点 UTC)"
echo 'openclaw cron add --name "telegram_group_weekly_report" --cron "0 18 * * 5" --tz "UTC" --session "isolated" --message "运行 Telegram 群组每周报告任务。使用命令: cd /root/.openclaw/workspace/telegram_summary/scripts && /root/miniconda3/envs/dl/bin/python main_group.py --weekly" --model "deepseek/deepseek-chat" --thinking "off" --announce --channel "telegram" --to "8721157770" --best-effort-deliver'

echo -e "\n🔧 手动运行命令:"

echo -e "\n# 查看群组系统状态"
echo "cd /root/.openclaw/workspace/telegram_summary/scripts"
echo "/root/miniconda3/envs/dl/bin/python main_group.py --status"

echo -e "\n# 运行群组每日总结"
echo "cd /root/.openclaw/workspace/telegram_summary/scripts"
echo "/root/miniconda3/envs/dl/bin/python main_group.py --daily"

echo -e "\n# 运行群组每周报告"
echo "cd /root/.openclaw/workspace/telegram_summary/scripts"
echo "/root/miniconda3/envs/dl/bin/python main_group.py --weekly"

echo -e "\n# 测试群组数据解析"
echo "cd /root/.openclaw/workspace/telegram_summary/scripts"
echo "/root/miniconda3/envs/dl/bin/python group_data_manager.py"

echo -e "\n📝 重要提示:"
echo "1. 确保bot已添加到 '$TARGET_GROUP' 群组"
echo "2. 确保bot在群组中有消息读取权限"
echo "3. 群组中需要有实际聊天记录"
echo "4. 系统会自动识别群组会话格式"

echo -e "\n🔍 验证步骤:"
echo "1. 将bot添加到 'develop group' 群组"
echo "2. 在群组中发送一些测试消息"
echo "3. 等待几分钟让OpenClaw记录消息"
echo "4. 运行测试命令验证数据解析"

echo -e "\n⚠️  当前限制:"
echo "1. 需要bot在群组中才能获取数据"
echo "2. 只能处理bot加入后的新消息"
echo "3. 需要Telegram Bot API权限支持"

echo -e "\n================================================"
echo "✅ 群组系统部署准备完成"
echo "================================================"
echo -e "\n下一步:"
echo "1. 将bot添加到 '$TARGET_GROUP' 群组"
echo "2. 在群组中产生聊天记录"
echo "3. 运行上面的部署命令"
echo "4. 系统将在指定时间自动运行"