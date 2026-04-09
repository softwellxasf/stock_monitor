#!/bin/bash
echo "🚀 推送到 GitHub stock_monitor 仓库"
echo ""
echo "仓库：https://github.com/softwellxasf/stock_monitor.git"
echo ""

# 清除之前的凭证配置
git config --global --unset credential.helper 2>/dev/null

# 配置使用 Personal Access Token
echo ""
echo "⚠️  GitHub 已不支持密码登录，需要使用 Personal Access Token"
echo ""
echo "获取 Token 步骤："
echo "1. 访问：https://github.com/settings/tokens"
echo "2. 点击 'Generate new token (classic)'"
echo "3. 勾选 'repo' 权限"
echo "4. 生成并复制 Token"
echo ""
echo "然后执行："
echo "git push https://575660259@qq.com:您的_TOKEN@github.com/softwellxasf/stock_monitor.git main"
echo ""

# 显示当前提交
echo "=== 待推送的提交 ==="
git log --oneline -10
