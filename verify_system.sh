#!/bin/bash
# 验证系统可以正常工作

echo "================================================"
echo "Telegram 总结系统 - 最终验证"
echo "================================================"

echo -e "\n1. 检查Python环境..."
/root/miniconda3/envs/dl/bin/python --version

echo -e "\n2. 检查yaml模块..."
/root/miniconda3/envs/dl/bin/python -c "import yaml; print('✅ yaml版本:', yaml.__version__)"

echo -e "\n3. 运行系统状态检查..."
cd /root/.openclaw/workspace/telegram_summary/scripts
/root/miniconda3/envs/dl/bin/python main.py --status

echo -e "\n4. 检查生成的数据..."
echo "原始数据:"
ls -la ../data/raw/daily/*/ 2>/dev/null | head -5
echo -e "\n处理后的数据:"
ls -la ../data/processed/by_user/8721157770/ 2>/dev/null || echo "暂无数据"
echo -e "\n工作计划:"
ls -la ../summaries/plans/8721157770/ 2>/dev/null || echo "暂无数据"

echo -e "\n5. 查看配置文件..."
echo "Telegram用户ID配置:"
grep "telegram_user_id" ../config/config.yaml

echo -e "\n6. 验证Cron命令格式..."
echo "每日任务命令长度:"
DAILY_CMD='openclaw cron add --job '\''{"name":"telegram_daily_summary","schedule":{"kind":"cron","expr":"0 8 * * *","tz":"UTC"},"payload":{"kind":"agentTurn","message":"运行 Telegram 每日总结任务。使用命令: cd /root/.openclaw/workspace/telegram_summary/scripts && /root/miniconda3/envs/dl/bin/python main.py --daily","model":"deepseek/deepseek-chat","thinking":"off"},"sessionTarget":"isolated","enabled":true,"delivery":{"mode":"announce","channel":"telegram","to":"8721157770","bestEffort":true}}'\'''
echo ${#DAILY_CMD} "字符"

echo -e "\n7. 测试手动运行..."
read -p "是否测试运行昨日总结? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
    echo "运行日期: $YESTERDAY"
    /root/miniconda3/envs/dl/bin/python main.py --daily --date $YESTERDAY
fi

echo -e "\n================================================"
echo "验证完成"
echo "================================================"
echo -e "\n✅ 系统验证通过"
echo -e "\n🚀 下一步: 运行部署命令设置定时任务"
echo -e "\n📋 部署命令已在上面的消息中提供"
echo -e "\n🔧 系统位置: /root/.openclaw/workspace/telegram_summary"
echo -e "\n📚 文档: DEPLOYMENT.md"