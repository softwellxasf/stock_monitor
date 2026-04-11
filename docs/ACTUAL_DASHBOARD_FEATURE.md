# 📊 实盘概览页面功能

**添加日期：** 2026-04-11  
**参考：** 模拟概览页面（SimDashboard.vue）

---

## 🎯 功能说明

实盘概览页面提供实盘持仓和收益的概览视图，功能与模拟概览类似。

---

## 📊 页面功能

### 1. 核心指标卡片

| 指标 | 说明 | 数据来源 |
|------|------|----------|
| **账户总值** | 当前账户总资产 | actual.getAccount() |
| **可用资金** | 账户现金余额 | actual.getAccount() |
| **持仓数量** | 当前持仓股票数 | actual.getStats() |
| **当前仓位** | 持仓市值/总资产 | actual.getStats() |
| **累计收益** | 总盈亏金额 | actual.getStats() |
| **收益率** | 累计收益百分比 | actual.getStats() |

### 2. 收益概览

- 今日收益
- 本周收益
- 本月收益
- 持仓成本

### 3. 仓位分析

**三个维度的仓位数据：**
- 📅 **日仓位** - 每日仓位变化趋势
- 📈 **周仓位** - 每周平均仓位
- 📉 **月仓位** - 每月平均仓位

**每个维度支持：**
- ✅ 日期范围选择器
- ✅ 折线图/表格切换
- ✅ 仓位比例和持仓市值显示

---

## 🔧 技术实现

### 前端文件

**文件：** `frontend/src/views/ActualDashboard.vue`

**基于：** `SimDashboard.vue`（模拟概览）

**主要修改：**
```javascript
// API 调用
actual.getAccount()      // 获取账户信息
actual.getStats()        // 获取统计数据
actual.getAnalysis()     // 获取收益分析数据
actual.getList()         // 获取自选列表

// 变量命名
actualDailyPositions     // 日仓位数据
actualWeeklyPositions    // 周仓位数据
actualMonthlyPositions   // 月仓位数据
```

### 后端 API

**文件：** `backend/app.py`

**接口：** `/api/actual-stats`

**返回数据：**
```json
{
  "success": true,
  "data": {
    "position_count": 1,
    "total_market_value": 19028.0,
    "total_cost": 19028.0,
    "total_profit": 273530.16,
    "profit_pct": 136.77,
    "position_ratio": 4.02
  }
}
```

### 路由配置

**文件：** `frontend/src/router/index.js`

**路由：**
```javascript
{
  path: 'real',
  name: 'ActualDashboard',
  component: () => import('../views/ActualDashboard.vue'),
  meta: { requiresAuth: true, title: '实盘概览' }
}
```

---

## 🌐 访问方式

### 访问地址

| 页面 | 地址 |
|------|------|
| **实盘概览** | http://localhost:3001/real |
| 模拟概览 | http://localhost:3001/sim |
| 实盘持仓 | http://localhost:3001/real/positions |
| 实盘交易 | http://localhost:3001/real/trades |
| 实盘分析 | http://localhost:3001/real/analysis |

### 导航菜单

在左侧导航栏点击：
- **实盘** → 实盘概览
- **实盘持仓** → 持仓列表
- **交易记录** → 交易记录
- **收益分析** → 收益分析

---

## 📈 与模拟概览对比

| 功能 | 模拟概览 | 实盘概览 |
|------|----------|----------|
| 账户总值 | ✅ | ✅ |
| 持仓数量 | ✅ | ✅ |
| 当前仓位 | ✅ | ✅ |
| 累计收益 | ✅ | ✅ |
| 日仓位分析 | ✅ | ✅ |
| 周仓位分析 | ✅ | ✅ |
| 月仓位分析 | ✅ | ✅ |
| 日期选择器 | ✅ | ✅ |
| 图表/表格切换 | ✅ | ✅ |

**数据来源不同：**
- 模拟概览：`sim_*` 表
- 实盘概览：`positions`, `trades` 表

---

## ✅ 功能验证

### 测试步骤

1. **访问页面**
   - 打开 http://localhost:3001/real
   - 登录 admin / admin123

2. **检查核心指标**
   - 账户总值显示正确
   - 持仓数量显示正确
   - 当前仓位显示正确（约 4%）

3. **测试仓位分析**
   - 点击"📅 日仓位" tab
   - 选择日期范围
   - 切换折线图/表格视图
   - 检查数据是否正确

4. **测试周/月仓位**
   - 点击"📈 周仓位" tab
   - 选择日期范围（支持多年）
   - 检查数据是否正确
   - 月仓位同理

---

## 📝 注意事项

### 1. 数据来源

实盘概览使用实盘数据表：
- `positions` - 当前持仓
- `trades` - 交易记录
- `daily_snapshots` - 每日快照（实盘）

### 2. 仓位比例计算

```python
# 持仓市值
total_market_value = sum(current_price * quantity for all positions)

# 仓位比例
position_ratio = total_market_value / total_asset * 100
```

### 3. 日期范围

支持查询任意日期范围：
- 日仓位：默认最近 60 天
- 周仓位：默认最近 60 天
- 月仓位：默认最近 60 天
- 可自定义选择

---

## 📚 相关文档

- `docs/SIM_DASHBOARD_FEATURES.md` - 模拟概览功能说明
- `docs/POSITION_DATE_RANGE_FEATURE.md` - 日期选择器功能
- `docs/ACTUAL_DASHBOARD_FEATURE.md` - 本文档

---

_功能添加：2026-04-11_  
_学霸 AI 📊_
