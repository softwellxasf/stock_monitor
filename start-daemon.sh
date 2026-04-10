#!/bin/bash
echo "🚀 启动 stockMonitor..."

# 启动后端
cd /home/lizr/pyProject/stockMonitor/backend
echo "启动后端 (Flask :5000)..."
nohup python3 app.py > /var/log/stockmonitor-backend.log 2>&1 &
BACKEND_PID=$!
echo "后端 PID: $BACKEND_PID"

# 等待后端启动
sleep 2

# 启动前端
cd /home/lizr/pyProject/stockMonitor/frontend
echo "启动前端 (Vite :3000)..."
nohup npm run dev > /var/log/stockmonitor-frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端 PID: $FRONTEND_PID"

echo ""
echo "✅ 启动完成!"
echo "   后端：http://localhost:5000"
echo "   前端：http://localhost:3000"
echo "   默认账号：admin / admin123"

# 保持主进程运行
tail -f /dev/null
