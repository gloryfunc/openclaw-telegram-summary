# Telegram 聊天记录总结系统 - 部署文档

## 系统概述

基于用户与 Telegram Bot 的对话记录，自动生成：
1. **每日总结** - 前一天的对话总结
2. **工作计划** - 当天的工作计划
3. **每周报告** - 本周的工作报告

## 系统架构

```
telegram_summary/
├── config/              # 配置文件
│   └── config.yaml     # 系统配置
├── scripts/            # Python 脚本
│   ├── main.py        # 主入口
│   ├── data_manager.py # 数据管理
│   ├── jsonl_parser.py # 数据解析
│   ├── ai_summarizer.py # AI 总结
│   └── scheduler.py    # 任务调度
├── data/               # 数据存储
│   ├── raw/           # 原始数据归档
│   │   ├── daily/     # 按日归档
│   │   └── weekly/    # 按周归档
│   └── processed/     # 处理后的数据
│       ├── by_user/   # 按用户汇总
│       └── by_week/   # 按周汇总
├── summaries/          # 生成的总结
│   ├── daily/         # 每日总结
│   ├── weekly/        # 每周报告
│   └── plans/         # 工作计划
└── logs/              # 系统日志
```

## 环境要求

- **Python**: 3.10+
- **OpenClaw**: 2026.2.9+
- **依赖包**: PyYAML
- **存储空间**: 至少 100MB

## 安装步骤

### 1. 检查环境
```bash
# 检查 Python
python --version

# 检查 OpenClaw
openclaw --version

# 检查依赖
pip list | grep pyyaml
```

### 2. 配置系统
编辑 `config/config.yaml`：
```yaml
# 数据源配置
data_source:
  sessions_path: "/root/.openclaw/agents/main/sessions"
  
# 推送配置  
notification:
  telegram_user_id: "8721157770"
  enable_daily: true
  enable_weekly: true
```

### 3. 测试系统
```bash
cd /root/.openclaw/workspace/telegram_summary/scripts

# 查看系统状态
/root/miniconda3/envs/dl/bin/python main.py --status

# 测试每日总结
/root/miniconda3/envs/dl/bin/python main.py --daily --date 2026-02-23

# 测试每周报告
/root/miniconda3/envs/dl/bin/python main.py --weekly
```

## 定时任务配置

### 使用 OpenClaw Cron

#### 检查当前状态
```bash
openclaw cron status
```

#### 添加每日任务 (早上8点 UTC)
```bash
openclaw cron add --job '{
  "name": "telegram_daily_summary",
  "schedule": {
    "kind": "cron",
    "expr": "0 8 * * *",
    "tz": "UTC"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "运行 Telegram 每日总结任务。使用命令: cd /root/.openclaw/workspace/telegram_summary/scripts && /root/miniconda3/envs/dl/bin/python main.py --daily",
    "model": "deepseek/deepseek-chat",
    "thinking": "off"
  },
  "sessionTarget": "isolated",
  "enabled": true,
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "to": "8721157770",
    "bestEffort": true
  }
}'
```

#### 添加每周任务 (周五下午6点 UTC)
```bash
openclaw cron add --job '{
  "name": "telegram_weekly_report",
  "schedule": {
    "kind": "cron",
    "expr": "0 18 * * 5",
    "tz": "UTC"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "运行 Telegram 每周报告任务。使用命令: cd /root/.openclaw/workspace/telegram_summary/scripts && /root/miniconda3/envs/dl/bin/python main.py --weekly",
    "model": "deepseek/deepseek-chat",
    "thinking": "off"
  },
  "sessionTarget": "isolated",
  "enabled": true,
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "to": "8721157770",
    "bestEffort": true
  }
}'
```

#### 验证任务
```bash
# 查看任务列表
openclaw cron list

# 手动测试任务
openclaw cron run --jobId <job-id>
```

## 手动运行命令

### 每日任务
```bash
cd /root/.openclaw/workspace/telegram_summary/scripts
/root/miniconda3/envs/dl/bin/python main.py --daily

# 指定日期
/root/miniconda3/envs/dl/bin/python main.py --daily --date 2026-02-23
```

### 每周任务
```bash
cd /root/.openclaw/workspace/telegram_summary/scripts
/root/miniconda3/envs/dl/bin/python main.py --weekly

# 指定年份和周数
/root/miniconda3/envs/dl/bin/python main.py --weekly --year 2026 --week 9
```

### 系统状态
```bash
cd /root/.openclaw/workspace/telegram_summary/scripts
/root/miniconda3/envs/dl/bin/python main.py --status
```

## 数据管理

### 查看数据
```bash
# 查看原始数据
ls -la telegram_summary/data/raw/daily/

# 查看处理后的数据
ls -la telegram_summary/data/processed/by_user/8721157770/

# 查看生成的总结
ls -la telegram_summary/summaries/plans/8721157770/
```

### 清理数据
```bash
# 清理30天前的数据
find telegram_summary/data/raw/daily -type d -mtime +30 -exec rm -rf {} \;
find telegram_summary/logs -name "*.log" -mtime +30 -delete
```

## 日志查看

### 系统日志
```bash
# 查看今日日志
tail -f telegram_summary/logs/task_log_$(date +%Y-%m-%d).json

# 查看错误日志
grep -r "error" telegram_summary/logs/
```

### OpenClaw 日志
```bash
# 查看 Gateway 日志
journalctl -u openclaw-gateway -f

# 查看 cron 执行日志
openclaw cron runs --jobId <job-id>
```

## 故障排除

### 常见问题

#### 1. Python 导入错误
```bash
# 安装依赖
pip install pyyaml

# 检查 Python 路径
which python
```

#### 2. 数据解析失败
```bash
# 检查会话文件是否存在
ls -la /root/.openclaw/agents/main/sessions/*.jsonl

# 测试解析器
cd telegram_summary/scripts
python jsonl_parser.py
```

#### 3. 定时任务不执行
```bash
# 检查 cron 状态
openclaw cron status

# 检查 Gateway 状态
systemctl status openclaw-gateway

# 手动测试任务
openclaw cron run --jobId <job-id>
```

#### 4. 推送失败
```bash
# 检查 Telegram 配置
cat telegram_summary/config/config.yaml | grep telegram_user_id

# 检查网络连接
curl -s https://api.telegram.org
```

### 调试模式
```bash
# 启用详细日志
cd telegram_summary/scripts
DEBUG=1 /root/miniconda3/envs/dl/bin/python main.py --daily
```

## 系统限制

### 已知限制
1. **数据源限制**: 只能访问用户与当前 bot 的对话记录
2. **无法获取**: 用户的其他 Telegram 聊天记录
3. **无法获取**: 群组聊天记录（除非 bot 在群组中）

### 性能考虑
1. **存储空间**: 每日约 1-5MB 数据增长
2. **处理时间**: 每日任务约 10-30 秒
3. **内存使用**: 约 50-100MB

## 备份与恢复

### 备份数据
```bash
# 备份整个系统
tar -czf telegram_summary_backup_$(date +%Y%m%d).tar.gz telegram_summary/

# 只备份数据
tar -czf telegram_data_backup_$(date +%Y%m%d).tar.gz telegram_summary/data/
```

### 恢复数据
```bash
# 恢复整个系统
tar -xzf telegram_summary_backup_20260224.tar.gz

# 恢复数据
tar -xzf telegram_data_backup_20260224.tar.gz -C telegram_summary/
```

## 更新与维护

### 更新代码
```bash
# 备份当前版本
cp -r telegram_summary/scripts telegram_summary/scripts_backup_$(date +%Y%m%d)

# 更新脚本
# 将新版本复制到 scripts/ 目录
```

### 监控系统
```bash
# 监控磁盘使用
df -h /root/.openclaw

# 监控进程
ps aux | grep python | grep telegram_summary

# 监控日志大小
du -sh telegram_summary/logs/
```

## 联系方式

- **项目路径**: `/root/.openclaw/workspace/telegram_summary`
- **问题反馈**: 通过 Telegram 联系
- **文档更新**: 查看本文件

---

**最后更新**: 2026-02-24  
**版本**: 1.0.0  
**状态**: 生产就绪