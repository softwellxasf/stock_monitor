# 📊 实盘仓位接口功能

**添加日期：** 2026-04-11  
**接口：** GET /api/actual-analysis

---

## 🎯 功能说明

实盘收益分析接口新增日/周/月仓位数据，支持实盘概览页面的仓位分析功能。

---

## 🔧 接口详情

### 接口：GET /api/actual-analysis

**功能：** 获取实盘收益分析数据（包含日/周/月仓位）

**请求：**
```http
GET /api/actual-analysis
Authorization: Bearer <token>
```

**响应：**
```json
{
  "success": true,
  "data": {
    "daily_returns": [...],
    "weekly_returns": [...],
    "monthly_returns": [...],
    "calendar_data": [...],
    "monthly_summary": [...],
    "daily_positions": [
      {
        "date": "2026-04-10",
        "position_ratio": 81.10,
        "position_value": 162198.79,
        "total_asset": 200000.00
      }
    ],
    "weekly_positions": [
      {
        "week": "04-08 ~ 04-14",
        "position_ratio": 81.10,
        "position_value": 162198.79
      }
    ],
    "monthly_positions": [
      {
        "month": "2026-04",
        "position_ratio": 81.10,
        "position_value": 162198.79
      }
    ]
  }
}
```

---

## 📊 仓位数据字段

### 日仓位（daily_positions）

| 字段 | 类型 | 说明 |
|------|------|------|
| **date** | string | 日期（YYYY-MM-DD） |
| **position_ratio** | number | 仓位比例（%） |
| **position_value** | number | 持仓市值（元） |
| **total_asset** | number | 总资产（元） |

### 周仓位（weekly_positions）

| 字段 | 类型 | 说明 |
|------|------|------|
| **week** | string | 周范围（MM-DD ~ MM-DD） |
| **position_ratio** | number | 平均仓位比例（%） |
| **position_value** | number | 平均持仓市值（元） |

### 月仓位（monthly_positions）

| 字段 | 类型 | 说明 |
|------|------|------|
| **month** | string | 月份（YYYY-MM） |
| **position_ratio** | number | 平均仓位比例（%） |
| **position_value** | number | 平均持仓市值（元） |

---

## 📈 计算逻辑

### 仓位比例计算

```python
# 日仓位比例
position_ratio = position_value / total_asset * 100

# 周仓位比例（周平均）
avg_pos_ratio = sum(position_values) / sum(total_assets) * 100

# 月仓位比例（月平均）
avg_pos_ratio = sum(position_values) / sum(total_assets) * 100
```

### 数据来源

**数据表：** `DailySnapshot`（实盘每日快照）

**字段：**
- `snapshot_date` - 日期
- `position_value` - 持仓市值
- `total_asset` - 总资产

---

## 🌐 前端使用

### API 调用

```javascript
// 获取实盘收益分析数据
const analysisRes = await actual.getAnalysis()
if (analysisRes.data.success) {
  const analysisData = analysisRes.data.data
  
  // 日仓位数据
  actualDailyPositions.value = analysisData.daily_positions || []
  
  // 周仓位数据
  actualWeeklyPositions.value = analysisData.weekly_positions || []
  
  // 月仓位数据
  actualMonthlyPositions.value = analysisData.monthly_positions || []
}
```

### 页面显示

**实盘概览页面：** http://localhost:3001/real

**功能：**
- 📅 日仓位 - 每日仓位变化趋势
- 📈 周仓位 - 每周平均仓位
- 📉 月仓位 - 每月平均仓位

---

## 📝 注意事项

### 1. 数据范围

- **日仓位：** 最近 60 天
- **周仓位：** 最近 30 周
- **月仓位：** 最近 15 个月

### 2. 数据更新

**更新频率：** 每日收盘后

**更新方式：**
- 自动：定时任务（每日 15:30）
- 手动：调用快照接口

### 3. 空数据处理

如果某天/周/月没有快照数据：
```json
{
  "date": "2026-04-10",
  "position_ratio": 0,
  "position_value": 0
}
```

---

## 📚 相关文档

- `docs/ACTUAL_DASHBOARD_FEATURE.md` - 实盘概览功能
- `docs/ACTUAL_ACCOUNT_FEATURE.md` - 实盘账户功能
- `docs/ACTUAL_POSITION_API.md` - 本文档

---

_功能添加：2026-04-11_  
_学霸 AI 📊_
