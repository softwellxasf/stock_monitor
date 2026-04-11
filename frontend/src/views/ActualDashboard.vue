<template>
  <div class="actual-dashboard" v-loading="loading">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>总资产</span>
              <el-icon><Wallet /></el-icon>
            </div>
          </template>
          <div class="stat-value">¥{{ stats.total_value?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>可用现金</span>
              <el-icon><Money /></el-icon>
            </div>
          </template>
          <div class="stat-value">¥{{ stats.cash?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>持仓数量</span>
              <el-icon><List /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.position_count }} 只</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>自选标的</span>
              <el-icon><Star /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.watchlist_count }} 只</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实盘概况 -->
    <el-card shadow="never" class="overview-card" style="margin-top: 20px">
      <template #header>
        <div class="card-header-title">
          <span>📊 实盘概况</span>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="6">
          <div class="overview-item">
            <div class="overview-label">初始资金</div>
            <div class="overview-value">¥{{ stats.total_capital?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="overview-item">
            <div class="overview-label">当前仓位</div>
            <div class="overview-value" v-if="stats.position_ratio > 0">{{ stats.position_ratio.toFixed(1) }}%</div>
            <div class="overview-value" v-else-if="stats.position_count > 0">0.0%</div>
            <div class="overview-value" v-else>-</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="overview-item">
            <div class="overview-label">累计收益</div>
            <div class="overview-value" :class="stats.total_capital > 0 ? (stats.total_value - stats.total_capital >= 0 ? 'profit' : 'loss') : ''" v-if="stats.total_capital > 0">¥{{ (stats.total_value - stats.total_capital).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</div>
            <div class="overview-value" v-else>-</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="overview-item">
            <div class="overview-label">收益率</div>
            <div class="overview-value" :class="stats.total_capital > 0 ? (stats.total_value - stats.total_capital >= 0 ? 'profit' : 'loss') : ''" v-if="stats.total_capital > 0">{{ ((stats.total_value - stats.total_capital) / stats.total_capital * 100).toFixed(2) }}%</div>
            <div class="overview-value" v-else>-</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 仓位分析图表 -->
    <el-card shadow="never" class="position-analysis-card" style="margin-top: 20px">
      <template #header>
        <div class="card-header-title">
          <span>📊 仓位分析</span>
        </div>
      </template>

      <el-tabs v-model="activePositionTab" class="position-tabs" stretch>
        <el-tab-pane label="📅 日仓位" name="daily">
          <div class="tab-header">
            <el-date-picker
              v-model="actualDailyDateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              @change="loadActualDailyPositionData"
              value-format="YYYY-MM-DD"
              size="small"
            />
            <div class="view-switcher">
              <el-button-group>
                <el-button :type="actualDailyViewMode === 'chart' ? 'primary' : ''" @click="actualDailyViewMode = 'chart'">
                  <el-icon><TrendCharts /></el-icon> 折线图
                </el-button>
                <el-button :type="actualDailyViewMode === 'table' ? 'primary' : ''" @click="actualDailyViewMode = 'table'">
                  <el-icon><List /></el-icon> 表格
                </el-button>
              </el-button-group>
            </div>
          </div>
          <div v-if="actualDailyPositions.length === 0" class="empty-data">暂无数据</div>
          <template v-else>

            <!-- 表格视图 -->
            <el-table v-if="actualDailyViewMode === 'table'" :data="actualDailyPositions" stripe style="width: 100%" :max-height="350">
              <el-table-column prop="date" label="日期" width="100" />
              <el-table-column label="仓位比例" align="right">
                <template #default="{ row }">
                  <el-tag :type="row.position_ratio >= 50 ? 'danger' : 'warning'" size="small">
                    {{ row.position_ratio.toFixed(2) }}%
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="持仓市值" align="right">
                <template #default="{ row }">
                  <span class="currency">¥{{ row.position_value?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="total_asset" label="总资产" align="right">
                <template #default="{ row }">
                  <span class="currency">¥{{ row.total_asset?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</span>
                </template>
              </el-table-column>
            </el-table>

            <!-- 折线图视图 -->
            <div v-else ref="actualDailyPositionChartRef" class="position-chart"></div>
          </template>
        </el-tab-pane>

        <el-tab-pane label="📈 周仓位" name="weekly">
          <div class="tab-header">
            <el-date-picker
              v-model="actualWeeklyDateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              @change="loadActualWeeklyPositionData"
              value-format="YYYY-MM-DD"
              size="small"
            />
            <div class="view-switcher">
              <el-button-group>
                <el-button :type="actualWeeklyViewMode === 'chart' ? 'primary' : ''" @click="actualWeeklyViewMode = 'chart'">
                  <el-icon><TrendCharts /></el-icon> 折线图
                </el-button>
                <el-button :type="actualWeeklyViewMode === 'table' ? 'primary' : ''" @click="actualWeeklyViewMode = 'table'">
                  <el-icon><List /></el-icon> 表格
                </el-button>
              </el-button-group>
            </div>
          </div>
          <div v-if="actualWeeklyPositions.length === 0" class="empty-data">暂无数据</div>
          <template v-else>

            <!-- 表格视图 -->
            <el-table v-if="actualWeeklyViewMode === 'table'" :data="actualWeeklyPositions" stripe style="width: 100%" :max-height="350">
              <el-table-column prop="week" label="日期范围" width="140" />
              <el-table-column label="仓位比例" align="right">
                <template #default="{ row }">
                  <el-tag :type="row.position_ratio >= 50 ? 'danger' : 'warning'" size="small">
                    {{ row.position_ratio.toFixed(2) }}%
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="持仓市值" align="right">
                <template #default="{ row }">
                  <span class="currency">¥{{ row.position_value?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</span>
                </template>
              </el-table-column>
            </el-table>

            <!-- 折线图视图 -->
            <div v-else ref="actualWeeklyPositionChartRef" class="position-chart"></div>
          </template>
        </el-tab-pane>

        <el-tab-pane label="📉 月仓位" name="monthly">
          <div class="tab-header">
            <el-date-picker
              v-model="actualMonthlyDateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              @change="loadActualMonthlyPositionData"
              value-format="YYYY-MM-DD"
              size="small"
            />
            <div class="view-switcher">
              <el-button-group>
                <el-button :type="actualMonthlyViewMode === 'chart' ? 'primary' : ''" @click="actualMonthlyViewMode = 'chart'">
                  <el-icon><TrendCharts /></el-icon> 折线图
                </el-button>
                <el-button :type="actualMonthlyViewMode === 'table' ? 'primary' : ''" @click="actualMonthlyViewMode = 'table'">
                  <el-icon><List /></el-icon> 表格
                </el-button>
              </el-button-group>
            </div>
          </div>
          <div v-if="actualMonthlyPositions.length === 0" class="empty-data">暂无数据</div>
          <template v-else>

            <!-- 表格视图 -->
            <el-table v-if="actualMonthlyViewMode === 'table'" :data="actualMonthlyPositions" stripe style="width: 100%" :max-height="350">
              <el-table-column prop="month" label="月份" width="100" />
              <el-table-column label="仓位比例" align="right">
                <template #default="{ row }">
                  <el-tag :type="row.position_ratio >= 50 ? 'danger' : 'warning'" size="small">
                    {{ row.position_ratio.toFixed(2) }}%
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="持仓市值" align="right">
                <template #default="{ row }">
                  <span class="currency">¥{{ row.position_value?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</span>
                </template>
              </el-table-column>
            </el-table>

            <!-- 折线图视图 -->
            <div v-else ref="actualMonthlyPositionChartRef" class="position-chart"></div>
          </template>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { sim } from '../api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const stats = ref({
  total_value: 0,
  cash: 0,
  position_count: 0,
  position_ratio: 0,
  watchlist_count: 0,
  total_capital: 0
})
const loading = ref(true)

// 仓位图表相关
const activePositionTab = ref('daily')
const actualDailyPositions = ref([])
const actualWeeklyPositions = ref([])
const actualMonthlyPositions = ref([])
const actualDailyDateRange = ref([])
const actualWeeklyDateRange = ref([])
const actualMonthlyDateRange = ref([])

const actualDailyPositionChartRef = ref(null)
const actualWeeklyPositionChartRef = ref(null)
const actualMonthlyPositionChartRef = ref(null)
let actualDailyPositionChartInstance = null
let actualWeeklyPositionChartInstance = null
let actualMonthlyPositionChartInstance = null

// 视图模式：table 或 chart
const actualDailyViewMode = ref('chart')
const actualWeeklyViewMode = ref('chart')
const actualMonthlyViewMode = ref('chart')

onMounted(async () => {
  try {
    const [accountRes, statsRes, watchlistRes, analysisRes] = await Promise.all([
      actual.getAccount(),
      actual.getStats(),
      actual.getList ? actual.getList() : Promise.resolve({ data: { success: true, data: [] } }),
      actual.getAnalysis()
    ])

    let accountData = {}
    let statsData = {}
    let watchlistData = []
    let analysisData = {}

    if (accountRes.data.success) {
      accountData = accountRes.data.data || {}
    }
    if (statsRes.data.success) {
      statsData = statsRes.data.data || {}
    }
    if (watchlistRes.data.success) {
      watchlistData = watchlistRes.data.data || []
    }
    if (analysisRes.data.success) {
      analysisData = analysisRes.data.data || {}
    }

    console.log('statsData:', statsData)
    console.log('position_count:', statsData.position_count)
    
    stats.value = {
      total_value: accountData.total_value || 0,
      cash: accountData.cash || 0,
      total_capital: accountData.total_capital || 0,
      position_count: statsData.position_count || 0,
      position_ratio: statsData.position_ratio || 0,
      watchlist_count: watchlistData.length || 0
    }

    // 加载仓位数据
    actualDailyPositions.value = analysisData.daily_positions || []
    actualWeeklyPositions.value = analysisData.weekly_positions || []
    actualMonthlyPositions.value = analysisData.monthly_positions || []

    // 初始化图表
    setTimeout(() => {
      initActualDailyPositionChart()
    }, 100)

    
    // 从接口获取实际数据范围，设置默认日期
    try {
      const analysisRes = await actual.getAnalysis()
      if (analysisRes.data.success) {
        const analysisData = analysisRes.data.data || {}
        actualDailyPositions.value = analysisData.daily_positions || []
        actualWeeklyPositions.value = analysisData.weekly_positions || []
        actualMonthlyPositions.value = analysisData.monthly_positions || []
        
        // 根据实际数据范围设置默认日期（不限制 60 天）
        if (actualDailyPositions.value.length > 0) {
          const dates = actualDailyPositions.value.map(p => p.date).filter(d => d)
          if (dates.length > 0) {
            const sortedDates = dates.sort()
            const minDate = sortedDates[0]  // 最早日期
            const maxDate = sortedDates[sortedDates.length - 1]  // 最晚日期
            const actualRange = [minDate, maxDate]
            actualDailyDateRange.value = actualRange
            actualWeeklyDateRange.value = actualRange
            actualMonthlyDateRange.value = actualRange
          }
        }
        
        setTimeout(() => { initActualDailyPositionChart() }, 100)
      }
    } catch (error) {
      console.error('加载初始数据失败:', error)
    }
    
    window.addEventListener('resize', () => {
      if (actualDailyPositionChartInstance) actualDailyPositionChartInstance.resize()
      if (actualWeeklyPositionChartInstance) actualWeeklyPositionChartInstance.resize()
      if (actualMonthlyPositionChartInstance) actualMonthlyPositionChartInstance.resize()
    })
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
})

// 加载日仓位数据
const loadActualDailyPositionData = async () => {
  try {
    const [start, end] = actualDailyDateRange.value || []
    if (!start || !end) return
    const analysisRes = await sim.getAnalysis(start, end)
    if (analysisRes.data.success) {
      const analysisData = analysisRes.data.data || {}
      actualDailyPositions.value = analysisData.daily_positions || []
      setTimeout(() => { initActualDailyPositionChart() }, 100)
    }
  } catch (error) {
    console.error('加载日仓位数据失败:', error)
    ElMessage.error('加载日仓位数据失败')
  }
}

// 加载周仓位数据
const loadActualWeeklyPositionData = async () => {
  try {
    const [start, end] = actualWeeklyDateRange.value || []
    if (!start || !end) return
    const analysisRes = await sim.getAnalysis(start, end)
    if (analysisRes.data.success) {
      const analysisData = analysisRes.data.data || {}
      actualWeeklyPositions.value = analysisData.weekly_positions || []
      setTimeout(() => { initActualWeeklyPositionChart() }, 100)
    }
  } catch (error) {
    console.error('加载周仓位数据失败:', error)
    ElMessage.error('加载周仓位数据失败')
  }
}

// 加载月仓位数据
const loadActualMonthlyPositionData = async () => {
  try {
    const [start, end] = actualMonthlyDateRange.value || []
    if (!start || !end) return
    const analysisRes = await sim.getAnalysis(start, end)
    if (analysisRes.data.success) {
      const analysisData = analysisRes.data.data || {}
      actualMonthlyPositions.value = analysisData.monthly_positions || []
      setTimeout(() => { initActualMonthlyPositionChart() }, 100)
    }
  } catch (error) {
    console.error('加载月仓位数据失败:', error)
    ElMessage.error('加载月仓位数据失败')
  }
}



// 监听 tab 切换
watch(activePositionTab, (newTab) => {
  setTimeout(() => {
    if (newTab === 'daily') {
      initActualDailyPositionChart()
    } else if (newTab === 'weekly') {
      initActualWeeklyPositionChart()
    } else if (newTab === 'monthly') {
      initActualMonthlyPositionChart()
    }
  }, 50)
})

// 监听视图模式切换
watch(actualDailyViewMode, (newMode) => {
  if (newMode === 'chart') {
    setTimeout(() => initActualDailyPositionChart(), 50)
  }
})
watch(actualWeeklyViewMode, (newMode) => {
  if (newMode === 'chart') {
    setTimeout(() => initActualWeeklyPositionChart(), 50)
  }
})
watch(actualMonthlyViewMode, (newMode) => {
  if (newMode === 'chart') {
    setTimeout(() => initActualMonthlyPositionChart(), 50)
  }
})

// 初始化日仓位图表
const initActualDailyPositionChart = () => {
  if (!actualDailyPositionChartRef.value || actualDailyPositions.value.length === 0) return

  // 确保 DOM 元素已经渲染
  const chartDom = actualDailyPositionChartRef.value
  if (!chartDom || !chartDom.offsetHeight) return

  if (!actualDailyPositionChartInstance) {
    actualDailyPositionChartInstance = echarts.init(chartDom)
  }

  const data = actualDailyPositions.value.slice().reverse()
  const dates = data.map(d => d.date.slice(5))
  const positionRatios = data.map(d => d.position_ratio)
  const positionValues = data.map(d => d.position_value)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: (params) => {
        const date = params[0].name
        let html = `<div style="padding: 8px; font-weight: bold;">${date}</div>`
        params.forEach(p => {
          const color = '#409EFF'
          let value = p.value.toFixed(2)
          if (p.seriesName === '持仓市值') {
            value = '¥' + value.toLocaleString()
          } else {
            value = value + '%'
          }
          html += `<div style="padding: 4px 8px;">
            <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${color};margin-right:8px;"></span>
            <span>${p.seriesName}: ${value}</span>
          </div>`
        })
        return html
      }
    },
    legend: {
      data: ['仓位比例', '持仓市值'],
      bottom: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLabel: {
        rotate: 45,
        interval: Math.floor(dates.length / 15)
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '仓位比例 (%)',
        position: 'left',
        axisLabel: {
          formatter: '{value}%'
        },
        splitLine: {
          lineStyle: {
            type: 'dashed'
          }
        }
      },
      {
        type: 'value',
        name: '持仓市值 (¥)',
        position: 'right',
        axisLabel: {
          formatter: '¥{value}'
        },
        splitLine: {
          show: false
        }
      }
    ],
    series: [
      {
        name: '仓位比例',
        type: 'line',
        yAxisIndex: 0,
        data: positionRatios,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: '#f56c6c' },
        lineStyle: { width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0.05)' }
          ])
        }
      },
      {
        name: '持仓市值',
        type: 'line',
        yAxisIndex: 1,
        data: positionValues,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: '#409EFF' },
        lineStyle: { width: 2 }
      }
    ]
  }

  actualDailyPositionChartInstance.setOption(option)
}

// 初始化周仓位图表
const initActualWeeklyPositionChart = () => {
  if (!actualWeeklyPositionChartRef.value || actualWeeklyPositions.value.length === 0) return

  const chartDom = actualWeeklyPositionChartRef.value
  if (!chartDom || !chartDom.offsetHeight) return

  if (!actualWeeklyPositionChartInstance) {
    actualWeeklyPositionChartInstance = echarts.init(chartDom)
  }

  const data = actualWeeklyPositions.value.slice().reverse()
  const weeks = data.map(d => d.week)
  const positionRatios = data.map(d => d.position_ratio)

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const week = params[0].name
        const value = params[0].value
        return `<div style="padding: 8px;">
          <div style="font-weight: bold; margin-bottom: 8px;">${week}</div>
          <div>仓位比例：${value.toFixed(2)}%</div>
        </div>`
      }
    },
    legend: {
      data: ['仓位比例'],
      bottom: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: weeks,
      boundaryGap: false,
      axisLabel: {
        rotate: 45,
        interval: Math.floor(weeks.length / 8)
      }
    },
    yAxis: {
      type: 'value',
      name: '仓位比例 (%)',
      axisLabel: {
        formatter: '{value}%'
      },
      splitLine: {
        lineStyle: {
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: '仓位比例',
        type: 'line',
        data: positionRatios,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: '#f56c6c' },
        lineStyle: { width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0.05)' }
          ])
        }
      }
    ]
  }

  actualWeeklyPositionChartInstance.setOption(option)
}

// 初始化月仓位图表
const initActualMonthlyPositionChart = () => {
  if (!actualMonthlyPositionChartRef.value || actualMonthlyPositions.value.length === 0) return

  const chartDom = actualMonthlyPositionChartRef.value
  if (!chartDom || !chartDom.offsetHeight) return

  if (!actualMonthlyPositionChartInstance) {
    actualMonthlyPositionChartInstance = echarts.init(chartDom)
  }

  const data = actualMonthlyPositions.value.slice().reverse()
  const months = data.map(d => d.month.slice(5))
  const positionRatios = data.map(d => d.position_ratio)

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const month = params[0].name
        const value = params[0].value
        return `<div style="padding: 8px;">
          <div style="font-weight: bold; margin-bottom: 8px;">${month}月</div>
          <div>平均仓位：${value.toFixed(2)}%</div>
        </div>`
      }
    },
    legend: {
      data: ['仓位比例'],
      bottom: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: months,
      boundaryGap: false,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '仓位比例 (%)',
      axisLabel: {
        formatter: '{value}%'
      },
      splitLine: {
        lineStyle: {
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: '仓位比例',
        type: 'line',
        data: positionRatios,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: '#f56c6c' },
        lineStyle: { width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0.05)' }
          ])
        }
      }
    ]
  }

  actualMonthlyPositionChartInstance.setOption(option)
}
</script>

<style scoped>
.actual-dashboard { padding: 10px; }
.stat-value { font-size: 24px; font-weight: bold; color: #409EFF; text-align: center; padding: 20px 0; }
.stat-value.profit { color: #f56c6c; }
.stat-value.loss { color: #67c23a; }

/* 概览卡片 */
.overview-card {
  margin-top: 20px;
}

.card-header-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.overview-item {
  padding: 16px;
  text-align: center;
}

.overview-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.overview-value {
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
}

.overview-value.profit {
  color: #f56c6c;
}

.overview-value.loss {
  color: #67c23a;
}

.position-analysis-card {
  margin-top: 20px;
}

.position-tabs {
  margin-top: 10px;
}

.position-chart {
  width: 100%;
  height: 350px;
}

.empty-data {
  text-align: center;
  color: #909399;
  padding: 60px 0;
  font-size: 14px;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.view-switcher {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 0;
}

.currency {
  color: #606266;
}
</style>

<style scoped>
</style>
