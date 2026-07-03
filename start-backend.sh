#!/bin/bash
# 语言学论文速递 - 启动后端服务
# 使用方式：双击或在终端运行此文件

cd "$(dirname "$0")"

# 先杀掉可能存在的旧进程
lsof -ti:8000 | xargs kill -9 2>/dev/null

echo "正在启动语言学论文速递后端..."
/Users/apple/.workbuddy/binaries/python/envs/default/bin/uvicorn backend.main:app --port 8000 --reload

echo "后端已停止。"
