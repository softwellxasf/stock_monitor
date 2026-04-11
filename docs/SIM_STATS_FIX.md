# 🔧 模拟盘总盈亏计算修复

**修复日期：** 2026-04-11  
**问题：** 总盈亏数据显示不正确

---

## 🐛 问题描述

### 原计算逻辑（错误）

```python
# 错误代码
realized_profit = db.session.query(db.func.sum(SimTrade.amount - SimTrade.cost)).filter(
    SimTrade.action == 'SELL'
).scalar() or 0

unrealized_profit = 0  # 未实现盈亏

total_profit = realized_profit + unrealized_profit
```

**问题：**
- `SimTrade.cost` 字段存的是**佣金**（5-20 元），不是交易成本
- 计算结果：`sum(amount - 佣金)` = ¥4,552,910 ❌
- 明显错误（远大于实际盈亏）

### 错误数据示例

| 字段 | 错误值 | 正确值 |
|------|--------|--------|
| total_profit | ¥4,552,910 | ¥273,530 |
| profit_pct | 2276% | 136.77% |

---

## ✅ 修复方案

### 新计算逻辑（正确）

```python
# 修复后代码
account = SimAccount.query.filter_by(id=1).first()

if account and account.total_capital:
    total_profit = float(account.total_value) - float(account.total_capital)
    profit_pct = ((float(account.total_value) - float(account.total_capital)) / float(account.total_capital) * 100)
else:
    total_profit = 0
    profit_pct = 0
```

**优点：**
- ✅ 直接计算账户总值变化
- ✅ 不依赖交易记录
- ✅ 简单准确

---

## 📊 数据验证

### 数据库验证

```sql
-- sim_account 表数据
SELECT total_capital, total_value, (total_value - total_capital) as profit
FROM sim_account WHERE id=1;

-- 结果：
-- total_capital: ¥200,000.00
-- total_value: ¥473,530.16
-- profit: ¥273,530.16 ✅
```

### 回测数据验证

```sql
-- sim_daily_snapshots 最新快照
SELECT snapshot_date, total_asset, total_return
FROM sim_daily_snapshots
ORDER BY snapshot_date DESC LIMIT 1;

-- 结果：
-- snapshot_date: 2026-04-10
-- total_asset: ¥473,530.16
-- total_return: 136.7651% ✅
```

---

## 📈 修复前后对比

| 指标 | 修复前 | 修复后 | 状态 |
|------|--------|--------|------|
| **总盈亏** | ¥4,552,910 ❌ | **¥273,530** ✅ | 已修复 |
| **收益率** | 2276% ❌ | **136.77%** ✅ | 已修复 |
| 计算方式 | sum(amount-cost) | value-capital | 简化 |
| 准确性 | ❌ 错误 | ✅ 准确 | 已验证 |

---

## 🔍 根本原因

### SimTrade.cost 字段含义

| 字段 | 含义 | 示例值 |
|------|------|--------|
| amount | 交易金额 | ¥10,000 |
| cost | **佣金** | ¥5-20 |
| price | 成交价 | ¥50.00 |
| quantity | 数量 | 200 股 |

**误解：**
- 原代码认为 `cost` 是交易成本（买入价×数量）
- 实际 `cost` 是佣金（约万三，最低 5 元）

**正确理解：**
- 已实现盈亏应该从持仓成本价和卖出价计算
- 或者直接用账户总值变化

---

## 💡 最佳实践

### 总盈亏计算推荐方案

**方案 1：账户总值变化（推荐）**
```python
total_profit = account.total_value - account.total_capital
profit_pct = (total_profit / account.total_capital) * 100
```

**方案 2：持仓盈亏累计**
```python
# 已实现盈亏（卖出交易）
realized = sum((sell_price - buy_price) * quantity for each sell)

# 未实现盈亏（当前持仓）
unrealized = sum((current_price - cost_price) * quantity for each position)

total_profit = realized + unrealized
```

**方案 1 优点：**
- ✅ 简单直接
- ✅ 不易出错
- ✅ 已验证准确

---

## 📝 总结

### 修复内容

1. **删除错误计算** - 不再使用 `sum(amount - cost)`
2. **使用账户总值** - 直接计算 `total_value - total_capital`
3. **简化逻辑** - 减少依赖，提高准确性

### 验证结果

- ✅ 总盈亏：¥273,530（正确）
- ✅ 收益率：136.77%（正确）
- ✅ 与回测数据一致

### 后续建议

1. **添加数据验证** - 定期检查账户总值与快照一致
2. **文档说明** - 明确 `SimTrade.cost` 字段含义
3. **单元测试** - 添加盈亏计算测试用例

---

_修复完成：2026-04-11_  
_学霸 AI 📊_
