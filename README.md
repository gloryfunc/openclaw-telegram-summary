# OpenClaw Telegram 私聊总结系统

基于 OpenClaw 的 Telegram 私聊会话自动总结系统，使用 AI 生成每日/每周对话总结。

## 🚀 功能特性

- 📊 **自动数据收集**：从 OpenClaw 会话文件自动收集私聊对话数据
- 🤖 **AI 驱动总结**：使用 DeepSeek 模型生成智能对话总结
- ⏰ **定时任务调度**：自动运行每日总结和每周报告
- 📁 **结构化存储**：按日期和用户组织数据归档
- 🔔 **实时通知**：通过 Telegram 推送总结报告
- 🛠️ **一键部署**：完整的部署和验证脚本

## 🏗️ 系统架构

```
openclaw-telegram-summary/
├── scripts/                 # 核心脚本
│   ├── main.py             # 主程序入口
│   ├── data_manager.py     # 数据管理
│   ├── ai_summarizer.py    # AI 总结生成
│   ├── jsonl_parser.py     # JSONL 文件解析
│   ├── data_models.py      # 数据模型定义
│   ├── scheduler.py        # 任务调度
│   └── test_simple.py      # 简单测试
├── config/                 # 配置文件
│   └── config.yaml         # 主配置文件
├── docs/                   # 文档
│   ├── DEPLOYMENT.md       # 部署指南
│   └── ARCHITECTURE.md     # 架构文档
└── scripts/               # 工具脚本
    ├── deploy_group.sh    # 群组部署脚本
    └── verify_deployment.sh # 部署验证
```

## ⚙️ 快速开始

### 1. 环境要求
- Python 3.8+
- OpenClaw 运行环境
- DeepSeek API 访问权限

### 2. 安装配置
```bash
# 克隆仓库
git clone git@github.com:leopoldwalden/openclaw-telegram-summary.git
cd openclaw-telegram-summary

# 配置环境
cp config/config.yaml.example config/config.yaml
# 编辑配置文件，设置你的 API 密钥和路径
```

### 3. 运行测试
```bash
cd scripts
python test_simple.py
python main.py --status
```

### 4. 部署定时任务
```bash
# 使用 OpenClaw cron 系统
openclaw cron add --name "telegram_daily_summary" \
  --cron "0 8 * * *" --tz "UTC" \
  --session "isolated" \
  --message "运行 Telegram 每日总结任务。使用命令: cd /path/to/openclaw-telegram-summary/scripts && python main.py --daily"
```

## 📅 定时任务配置

系统预配置了两个定时任务：

| 任务 | 时间 | 描述 |
|------|------|------|
| 每日总结 | 每天 08:00 UTC | 生成前一天的对话总结 |
| 每周报告 | 每周五 18:00 UTC | 生成本周对话报告 |

## 🔧 配置说明

### 数据源配置
```yaml
data_source:
  sessions_path: "/root/.openclaw/agents/main/sessions"
  file_pattern: "*.jsonl"
  source_type: "direct"  # direct: 私聊数据, group: 群组数据
```

### AI 配置
```yaml
ai:
  model: "deepseek/deepseek-chat"
  max_tokens: 2000
  temperature: 0.7
```

### 存储配置
```yaml
storage:
  base_path: "/path/to/data"
  raw_data: "raw"
  processed_data: "processed"
  summaries: "summaries"
```

## 📊 数据流程

1. **数据收集**：从 OpenClaw 会话文件解析对话数据
2. **日期过滤**：按目标日期筛选相关消息
3. **数据归档**：原始数据保存到按日期组织的目录
4. **AI 处理**：使用 DeepSeek 模型生成总结
5. **结果存储**：总结保存为 JSON 格式
6. **通知发送**：通过 Telegram 推送结果

## 🐛 故障排除

### 常见问题

1. **SSH 连接失败**
   ```bash
   # 测试 SSH 连接
   ssh -T git@github.com
   ```

2. **Python 依赖缺失**
   ```bash
   pip install pyyaml
   ```

3. **OpenClaw 会话路径错误**
   - 检查 `config.yaml` 中的 `sessions_path`
   - 确保 OpenClaw 正在运行并生成会话文件

### 日志查看
```bash
# 查看系统日志
tail -f logs/system.log

# 查看定时任务日志
openclaw cron runs --jobId <job_id>
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [OpenClaw](https://openclaw.ai) - 提供会话数据接口
- [DeepSeek](https://www.deepseek.com) - AI 模型支持
- Telegram Bot API - 消息推送服务

## 📞 支持

如有问题或建议，请：
1. 查看 [Issues](https://github.com/leopoldwalden/openclaw-telegram-summary/issues)
2. 提交新的 Issue
3. 或通过 Telegram 联系维护者

---

**Happy Summarizing!** 🎉