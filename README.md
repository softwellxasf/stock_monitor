# stockMonitor 📊

股票持仓、模拟交易和统计 Web 系统

## 技术栈

- **后端**: Python 3 + Flask + SQLAlchemy
- **前端**: Vue 3 + Element Plus + Vite
- **数据库**: MySQL (复用 stockProject 数据库)

## 功能

- ✅ 用户登录/注册（JWT 认证）
- ✅ 模拟盘持仓管理
- ✅ 自选表查看
- ✅ 账户统计分析
- ✅ 实时数据展示

## 快速开始

### 1. 安装后端依赖

```bash
cd backend
pip3 install -r requirements.txt
python3 app.py
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
npm run dev
```

### 3. 访问系统

- 前端：http://localhost:3000
- 后端：http://localhost:5000
- 默认账号：`admin` / `admin123`

## 数据库

复用 stockProject 项目的 MySQL 数据库：
- 主机：127.0.0.1
- 端口：3306
- 数据库：stock_project
- 用户：root

## 数据表

- `sm_users` - 用户表
- `sim_account` - 模拟账户
- `sim_positions` - 模拟持仓
- `watchlist` - 自选表

## 项目结构

```
stockMonitor/
├── backend/          # 后端 Flask 应用
│   ├── app.py       # 主应用
│   ├── config.py    # 配置
│   └── requirements.txt
├── frontend/         # 前端 Vue 应用
│   ├── src/
│   │   ├── api/     # API 调用
│   │   ├── views/   # 页面组件
│   │   ├── router/  # 路由
│   │   └── main.js
│   └── package.json
└── README.md
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/login | POST | 用户登录 |
| /api/register | POST | 用户注册 |
| /api/sim-account | GET | 获取模拟账户 |
| /api/sim-positions | GET | 获取持仓列表 |
| /api/watchlist | GET | 获取自选表 |
| /api/stats | GET | 获取统计数据 |

## License

Private
