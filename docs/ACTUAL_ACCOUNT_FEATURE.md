# 📊 实盘账户功能

**添加日期：** 2026-04-11  
**功能：** 实盘账户管理和数据展示

---

## 🎯 功能说明

创建实盘账户表和相关 API 接口，支持实盘账户数据的查询和展示。

---

## 📊 数据库表结构

### actual_account 表

| 字段 | 类型 | 说明 |
|------|------|------|
| **id** | INT | 主键 |
| **total_capital** | DECIMAL(12,2) | 总资本（初始资金） |
| **cash** | DECIMAL(12,2) | 可用资金（现金） |
| **total_value** | DECIMAL(12,2) | 总资产 |
| **total_cost_paid** | DECIMAL(12,2) | 已投入成本 |
| **created_at** | DATETIME | 创建时间 |
| **updated_at** | DATETIME | 更新时间 |

### 初始数据

```sql
INSERT INTO actual_account VALUES (
  1,              -- id
  200000.00,      -- total_capital
  180972.00,      -- cash
  200000.00,      -- total_value
  0.00,           -- total_cost_paid
  NOW(), NOW()    -- 时间戳
);
```

**账户数据：**
- 总资本：¥200,000
- 现金：¥180,972
- 总资产：¥200,000
- 持仓市值：¥19,028（约 9.5% 仓位）

---

## 🔧 后端 API

### 接口：GET /api/actual-account

**功能：** 获取实盘账户信息

**请求：**
```http
GET /api/actual-account
Authorization: Bearer <token>
```

**响应：**
```json
{
  "success": true,
  "data": {
    "total_capital": 200000.00,
    "cash": 180972.00,
    "total_value": 200000.00,
    "total_cost_paid": 0.00,
    "position_value": 19028.00
  }
}
```

**字段说明：**
- `total_capital` - 总资本（初始资金）
- `cash` - 可用资金
- `total_value` - 总资产
- `total_cost_paid` - 已投入成本
- `position_value` - 持仓市值（计算得出：total_value - cash）

---

## 📊 前端使用

### API 调用

**文件：** `frontend/src/api/index.js`

```javascript
export const actual = {
  getAccount: () => api.get('/actual-account'),
  getPositions: (params) => api.get('/actual-positions', { params }),
  getStats: () => api.get('/actual-stats'),
  getAnalysis: () => api.get('/actual-analysis'),
  getList: () => api.get('/watchlist')
}
```

### 页面使用

**文件：** `frontend/src/views/ActualDashboard.vue`

```javascript
// 获取账户信息
const accountRes = await actual.getAccount()
if (accountRes.data.success) {
  const accountData = accountRes.data.data
  stats.value.total_value = accountData.total_value
  stats.value.cash = accountData.cash
  stats.value.total_capital = accountData.total_capital
}
```

---

## 📈 账户计算逻辑

### 持仓市值

```python
position_value = total_value - cash
# 示例：200000 - 180972 = 19028
```

### 仓位比例

```python
position_ratio = position_value / total_value * 100
# 示例：19028 / 200000 * 100 = 9.51%
```

### 累计收益

```python
total_profit = total_value - total_capital
# 示例：200000 - 200000 = 0
```

### 收益率

```python
profit_pct = total_profit / total_capital * 100
# 示例：0 / 200000 * 100 = 0%
```

---

## 🌐 访问方式

### 实盘概览页面

**地址：** http://localhost:3001/real

**功能：**
- ✅ 账户总值显示
- ✅ 可用资金 显示
- ✅ 持仓数量 显示
- ✅ 当前仓位 显示
- ✅ 累计收益 显示
- ✅ 收益率 显示

---

## 📝 注意事项

### 1. 数据来源

实盘账户数据来自 `actual_account` 表，与模拟账户（`sim_account`）独立。

### 2. 数据更新

**自动更新：**
- 每次获取账户信息时，从数据库读取最新数据

**手动更新：**
```sql
UPDATE actual_account 
SET cash = 180972.00, 
    total_value = 200000.00,
    updated_at = NOW()
WHERE id = 1;
```

### 3. 仓位计算

仓位比例 = 持仓市值 / 总资产 × 100%

**示例：**
- 持仓市值：¥19,028
- 总资产：¥200,000
- 仓位比例：9.51%

---

## 📚 相关文档

- `docs/ACTUAL_DASHBOARD_FEATURE.md` - 实盘概览功能
- `docs/ACTUAL_ACCOUNT_FEATURE.md` - 本文档
- `docs/SIM_ACCOUNT_FEATURE.md` - 模拟账户功能

---

_功能添加：2026-04-11_  
_学霸 AI 📊_
