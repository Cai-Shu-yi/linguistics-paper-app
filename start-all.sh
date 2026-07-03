#!/bin/bash
# 语言学论文速递 - 一键启动（前端 + 后端）
# 使用方式：双击或在终端运行此文件

cd "$(dirname "$0")"

echo "========================================="
echo "  语言学论文速递 · 一键启动"
echo "========================================="

# 杀掉旧进程
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

# 启动后端
echo ""
echo "[1/2] 启动后端 API (端口 8000)..."
/Users/apple/.workbuddy/binaries/python/envs/default/bin/uvicorn backend.main:app --port 8000 &
BACKEND_PID=$!
sleep 2

# 验证后端
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
  echo "      后端启动成功"
else
  echo "      后端启动失败，请检查"
  exit 1
fi

# 启动前端
echo "[2/2] 启动前端 (端口 5173)..."
NODE_PATH=/Users/apple/.workbuddy/binaries/node/workspace/node_modules \
  /Users/apple/.workbuddy/binaries/node/versions/22.22.2/bin/node \
  /Users/apple/.workbuddy/binaries/node/workspace/node_modules/vite/bin/vite.js --port 5173 &
FRONTEND_PID=$!

sleep 2
echo ""
echo "========================================="
echo "  启动完成！"
echo "  前端: http://localhost:5173"
echo "  后端: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo "========================================="
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待任意子进程退出
wait
