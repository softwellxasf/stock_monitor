#!/bin/bash
echo "🛑 停止 stockMonitor..."

# 停止后端
pkill -f "python3 app.py" 2>/dev/null
echo "后端已停止"

# 停止前端
pkill -f "vite" 2>/dev/null
pkill -f "node.*vite" 2>/dev/null
echo "前端已停止"

echo "✅ 停止完成"
