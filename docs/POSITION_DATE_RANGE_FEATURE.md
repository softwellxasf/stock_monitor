# 📊 模拟概览仓位分析时间段查询功能

**添加日期：** 2026-04-11  
**功能：** 仓位分析支持自定义时间段查询

---

## 🎯 功能说明

### 时间段选择器

**位置：** 模拟概览 → 仓位分析卡片右上角

**默认值：** 最近 60 天

**功能：**
- 📅 支持自定义开始和结束日期
- 🔄 选择后自动刷新仓位数据
- 📊 支持日/周/月仓位数据查询

---

## 💡 使用方法

### 1. 查看最近 60 天仓位（默认）

打开模拟概览页面，默认显示最近 60 天的仓位数据。

### 2. 自定义时间段

1. 点击仓位分析卡片右上角的日期选择器
2. 选择开始日期和结束日期
3. 自动刷新仓位数据

### 3. 切换仓位类型

- 📅 **日仓位** - 每日仓位变化
- 📈 **周仓位** - 每周平均仓位
- 📉 **月仓位** - 每月平均仓位

---

## 🔧 技术实现

### 前端修改

**文件：** `frontend/src/views/SimDashboard.vue`

**新增：**
- `positionDateRange` - 时间段选择器绑定值
- `defaultDateRange` - 默认时间段（最近 60 天）
- `loadPositionData()` - 加载仓位数据函数

**修改：**
- 仓位分析卡片头部添加日期选择器
- onMounted 时初始化默认时间段

### API 修改

**文件：** `frontend/src/api/index.js`

**修改：**
```javascript
// 修改前
getAnalysis: () => api.get('/sim-analysis')

// 修改后
getAnalysis: (startDate, endDate) => {
  const params = new URLSearchParams()
  if (startDate && endDate) {
    params.append('start_date', startDate)
    params.append('end_date', endDate)
  }
  return api.get(`/sim-analysis?${params.toString()}`)
}
```

### 后端修改

**文件：** `backend/app.py`

**修改：**
```python
# 获取时间段参数
start_date = request.args.get('start_date')
end_date = request.args.get('end_date')

# 过滤快照数据
query = SimDailySnapshot.query.order_by(SimDailySnapshot.snapshot_date.desc())
if start_date and end_date:
    from datetime import datetime
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    query = query.filter(
        SimDailySnapshot.snapshot_date >= start,
        SimDailySnapshot.snapshot_date <= end
    )

snapshots = query.all()
```

---

## 📊 数据示例

### 默认（最近 60 天）

```
日期范围：2026-02-10 ~ 2026-04-11
日仓位数据：60 条
周仓位数据：9 条
月仓位数据：3 条
```

### 自定义（2026 年第一季度）

```
日期范围：2026-01-01 ~ 2026-03-31
日仓位数据：90 条
周仓位数据：13 条
月仓位数据：3 条
```

---

## 📝 使用场景

### 场景 1：查看最近仓位变化

**操作：** 使用默认值（最近 60 天）

**用途：**
- 了解近期仓位趋势
- 判断当前仓位水平
- 调整投资策略

### 场景 2：回顾历史仓位

**操作：** 选择历史时间段

**用途：**
- 回顾特定时期仓位管理
- 分析仓位与收益关系
- 总结经验教训

### 场景 3：对比不同时期

**操作：** 选择不同时间段多次查询

**用途：**
- 对比牛市/熊市仓位
- 分析仓位策略有效性
- 优化仓位管理

---

## 🎨 UI 设计

### 日期选择器样式

```
┌─────────────────────────────────────┐
│ 📊 仓位分析    [开始日期] 至 [结束日期] │
├─────────────────────────────────────┤
│ [日仓位] [周仓位] [月仓位]           │
│ ...                                 │
└─────────────────────────────────────┘
```

### 响应式设计

- **桌面端：** 日期选择器显示在右上角
- **移动端：** 日期选择器自动换行

---

## ✅ 功能验证

### 验证步骤

1. ✅ 打开模拟概览页面
2. ✅ 检查日期选择器是否显示
3. ✅ 检查默认值是否为最近 60 天
4. ✅ 选择自定义时间段
5. ✅ 检查仓位数据是否刷新
6. ✅ 切换日/周/月仓位
7. ✅ 检查数据是否正确

### 预期结果

- ✅ 日期选择器正常显示
- ✅ 默认值为最近 60 天
- ✅ 选择时间段后数据自动刷新
- ✅ 日/周/月仓位数据正确
- ✅ 图表正常渲染

---

## 📚 相关文档

- `docs/SIM_DASHBOARD_FEATURES.md` - 模拟概览功能说明
- `docs/POSITION_ANALYSIS.md` - 仓位分析方法
- `docs/API_DOCUMENTATION.md` - API 接口文档

---

_功能添加：2026-04-11_  
_学霸 AI 📊_
