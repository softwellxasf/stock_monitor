#!/bin/bash
echo "🚀 启动 stockMonitor..."

# 启动后端
cd backend
echo "启动后端 (Flask :5000)..."
python3 app.py &
BACKEND_PID=$!

# 启动前端
cd ../frontend
echo "启动前端 (Vite :3000)..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ 启动完成!"
echo "   后端：http://localhost:5000"
echo "   前端：http://localhost:3000"
echo "   默认账号：admin / admin123"
echo ""
echo "按 Ctrl+C 停止服务"

wait
