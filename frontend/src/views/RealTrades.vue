<template>
  <div class="real-trades">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>📝 交易记录</span>
          <el-tag type="warning" size="small">实盘</el-tag>
        </div>
      </template>
      
      <el-alert
        title="实盘数据接入中..."
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
        show-icon
      />
      
      <el-table :data="sampleData" stripe style="width: 100%">
        <el-table-column prop="trade_date" label="交易日期" width="120" />
        <el-table-column prop="stock_code" label="代码" width="120" />
        <el-table-column prop="stock_name" label="名称" width="120" />
        <el-table-column prop="action" label="操作" width="80">
          <template #default="{ row }">
            <el-tag :type="row.action === '买入' ? 'success' : 'danger'">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="成交价" width="100">
          <template #default="{ row }">¥{{ row.price?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">¥{{ row.amount?.toLocaleString() }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
const sampleData = [
  { trade_date: '2026-04-08', stock_code: '600519.SH', stock_name: '贵州茅台', action: '买入', price: 1680.00, quantity: 100, amount: 168000 },
  { trade_date: '2026-04-05', stock_code: '000858.SZ', stock_name: '五粮液', action: '买入', price: 95.00, quantity: 500, amount: 47500 },
  { trade_date: '2026-04-01', stock_code: '300750.SZ', stock_name: '宁德时代', action: '买入', price: 180.00, quantity: 200, amount: 36000 }
]
</script>

<style scoped>
.real-trades {
  padding: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
