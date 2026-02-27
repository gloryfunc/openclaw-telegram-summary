# GitHub SSH 密钥配置指南

## 生成的 SSH 密钥对

### 公钥 (添加到 GitHub)
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIRUHVsxO/WVo7Svjbz8ExKCoZ7d7iSKO4nLQ3CnpIQd openclaw@telegram-summary
```

### 私钥 (已保存在服务器)
- 路径: `/root/.ssh/id_ed25519_telegram_summary`
- **不要分享此私钥**

## 如何将公钥添加到 GitHub

### 方法 1: 通过 GitHub 网站
1. 登录 GitHub
2. 点击右上角头像 → **Settings**
3. 左侧菜单选择 **SSH and GPG keys**
4. 点击 **New SSH key**
5. 填写:
   - **Title**: `OpenClaw Telegram Summary`
   - **Key type**: `Authentication Key`
   - **Key**: 粘贴上面的公钥内容
6. 点击 **Add SSH key**

### 方法 2: 通过 GitHub CLI (如果有)
```bash
gh ssh-key add ~/.ssh/id_ed25519_telegram_summary.pub --title "OpenClaw Telegram Summary"
```

## 测试 SSH 连接

配置完成后，在服务器上运行:
```bash
ssh -T git@github.com
```

应该看到类似这样的响应:
```
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

## 仓库同步步骤

### 1. 提供仓库信息
请提供:
- GitHub 仓库地址 (SSH格式): `git@github.com:username/repo.git`
- 或 HTTPS 格式: `https://github.com/username/repo.git`

### 2. 初始化 git 仓库
```bash
cd /root/.openclaw/workspace/telegram_summary
git init
git remote add origin <你的仓库地址>
```

### 3. 配置 git 用户信息
```bash
git config user.name "你的名字"
git config user.email "你的邮箱"
```

### 4. 提交并推送代码
```bash
git add .
git commit -m "feat: 添加 Telegram 私聊总结系统"
git push -u origin main
```

## 定时任务代码结构

需要同步的代码包括:

### 核心脚本
```
scripts/
├── main.py                    # 主程序 (私聊版本)
├── data_manager.py           # 数据管理器
├── ai_summarizer.py          # AI 总结器
├── jsonl_parser.py           # JSONL 解析器
├── data_models.py            # 数据模型
└── scheduler.py              # 调度器
```

### 配置文件
```
config/
└── config.yaml               # 配置文件 (已设置为 direct)
```

### 部署脚本
```
deploy_group.sh              # 群组部署脚本 (参考)
verify_deployment.sh         # 部署验证脚本
setup_cron.py               # 定时任务设置
```

### 文档
```
GITHUB_SETUP.md             # 本文件
DEPLOYMENT.md               # 部署文档
telegram_summary_architecture.md  # 架构文档
```

## 定时任务配置

已部署的定时任务:
- **每日总结**: 每天 08:00 UTC (`main.py --daily`)
- **每周报告**: 每周五 18:00 UTC (`main.py --weekly`)

配置详情见 `setup_cron.py`。

## 注意事项

1. **敏感信息**: 确保不提交敏感信息 (API密钥、密码等)
2. **.gitignore**: 建议创建 `.gitignore` 排除:
   - `data/` (数据文件)
   - `logs/` (日志文件)
   - `__pycache__/`
   - 环境配置文件

3. **测试**: 同步前请测试代码功能
4. **备份**: 建议先备份现有代码

## 问题排查

如果 SSH 连接失败:
1. 检查公钥是否正确添加到 GitHub
2. 验证 SSH 代理是否运行: `eval "$(ssh-agent -s)"`
3. 添加密钥到代理: `ssh-add ~/.ssh/id_ed25519_telegram_summary`
4. 测试连接: `ssh -T git@github.com`

如需帮助，请提供具体的错误信息。