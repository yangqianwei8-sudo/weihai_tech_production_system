# GitHub 自动推送配置指南

## 方式一：使用 Personal Access Token（推荐）

1. **生成 GitHub Personal Access Token**
   - 访问：https://github.com/settings/tokens
   - 点击 "Generate new token" -> "Generate new token (classic)"
   - 设置名称，选择过期时间
   - 勾选 `repo` 权限
   - 生成并复制token（只显示一次，请妥善保存）

2. **配置环境变量**
   ```bash
   # 临时设置（当前会话有效）
   export GITHUB_TOKEN=your_token_here
   
   # 永久设置（添加到 ~/.bashrc 或 ~/.bash_profile）
   echo 'export GITHUB_TOKEN=your_token_here' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **使用脚本**
   ```bash
   ./auto_git_push.sh "提交信息"
   ```

## 方式二：使用 Git Credential Helper

1. **配置凭据存储**
   ```bash
   git config --global credential.helper store
   ```

2. **手动推送一次（会提示输入用户名和token）**
   ```bash
   git push origin main
   # 用户名：your_github_username
   # 密码：your_personal_access_token（不是GitHub密码）
   ```

3. **之后脚本即可自动推送**

## 方式三：使用 SSH（最安全）

1. **生成SSH密钥**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. **添加SSH密钥到GitHub**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # 复制输出的内容，添加到 GitHub -> Settings -> SSH and GPG keys
   ```

3. **更改远程仓库URL为SSH**
   ```bash
   git remote set-url origin git@github.com:yangqianwei8-sudo/weihai_tech_production_system.git
   ```

4. **测试连接**
   ```bash
   ssh -T git@github.com
   ```

## 使用自动推送脚本

```bash
# 基本用法
./auto_git_push.sh

# 自定义提交信息
./auto_git_push.sh "修复bug：更新用户界面"

# 使用环境变量中的token
export GITHUB_TOKEN=your_token
./auto_git_push.sh
```

## 定时自动推送（可选）

使用cron设置定时任务：

```bash
# 编辑crontab
crontab -e

# 添加定时任务（例如：每天凌晨2点自动提交和推送）
0 2 * * * cd /home/devbox/project && /home/devbox/project/auto_git_push.sh "定时自动备案：$(date '+\%Y-\%m-\%d')"
```

## 注意事项

- ⚠️ **安全提示**：不要将token提交到代码仓库
- 确保 `.gitignore` 中包含敏感信息文件
- Personal Access Token需要 `repo` 权限才能推送代码

