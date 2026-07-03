# 语言学论文速递

温暖、简洁的语言学论文推送工具，覆盖 CSSCI 外语类 + SSCI 语言学期刊，支持 AI 深度解读。

## 快速开始（本地）

```bash
# 一键启动前后端
./start-all.sh

# 然后打开 http://localhost:5173
```

## 部署后端到 Railway

1. 将本项目推送到 GitHub
2. 打开 [railway.app](https://railway.app) 用 GitHub 登录
3. 点击 "New Project" → "Deploy from GitHub repo" → 选择本项目
4. Railway 会自动识别 `railway.json` 配置
5. 部署成功后，复制后端 URL（如 `https://xxx.up.railway.app`）
6. 修改 `src/services/paperService.ts` 中的 `YOUR_BACKEND_URL` 为实际地址
7. 重新构建前端并部署

## 项目结构

```
linguistics-paper-app/
├── src/                  # React 前端源码
├── backend/              # Python FastAPI 后端
│   ├── main.py           # API 入口（含 212 本期刊清单）
│   ├── database.py       # SQLite 数据库
│   ├── paper_fetcher.py  # CrossRef/Semantic Scholar 抓取
│   └── requirements.txt
├── start-all.sh          # 本地一键启动
├── start-backend.sh      # 仅启动后端
└── railway.json          # Railway 部署配置
```

## AI 解读功能

需在设置页面输入 [DeepSeek API Key](https://platform.deepseek.com/api_keys)，密钥仅存储浏览器本地。
