<template>
  <div class="sim-analysis">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>总盈亏</span>
              <el-icon class="icon-red"><TrendCharts /></el-icon>
            </div>
          </template>
          <div class="stat-value" :class="stats.total_profit >= 0 ? 'profit' : 'loss'">
            {{ stats.total_profit >= 0 ? '+' : '' }}¥{{ stats.total_profit?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}
          </div>
          <div class="stat-sub">{{ stats.profit_pct?.toFixed(2) }}%</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>持仓成本</span>
              <el-icon class="icon-blue"><Money /></el-icon>
            </div>
          </template>
          <div class="stat-value">¥{{ stats.total_cost?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</div>
          <div class="stat-sub">市值：¥{{ stats.total_market_value?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>持仓统计</span>
              <el-icon class="icon-orange"><List /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.position_count }} 只</div>
          <div class="stat-sub">交易记录：{{ stats.trade_count }} 笔</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 收益趋势主卡片 -->
    <el-card shadow="never" class="analysis-card">
      <el-empty v-if="!analysisLoaded" description="加载中..." :image-size="100" />

      <div v-else class="analysis-content">
        <!-- 收益概览 -->
        <el-card shadow="never" class="overview-card">
          <template #header>
            <div class="card-header-title">
              <span>📊 收益概览</span>
            </div>
          </template>

          <el-row :gutter="20">
            <el-col :span="6">
              <div class="overview-item">
                <div class="overview-label">今日收益</div>
                <div class="overview-value" :class="latestDailyReturn >= 0 ? 'profit' : 'loss'">
                  {{ latestDailyReturn >= 0 ? '+' : '' }}{{ latestDailyReturn?.toFixed(2) }}%
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="overview-item">
                <div class="overview-label">本周收益</div>
                <div class="overview-value" :class="latestWeeklyReturn >= 0 ? 'profit' : 'loss'">
                  {{ latestWeeklyReturn >= 0 ? '+' : '' }}{{ latestWeeklyReturn?.toFixed(2) }}%
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="overview-item">
                <div class="overview-label">本月收益</div>
                <div class="overview-value" :class="latestMonthlyReturn >= 0 ? 'profit' : 'loss'">
                  {{ latestMonthlyReturn >= 0 ? '+' : '' }}{{ latestMonthlyReturn?.toFixed(2) }}%
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="overview-item">
                <div class="overview-label">持仓成本</div>
                <div class="overview-value">¥{{ stats.total_cost?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 收益统计表格（选项卡） -->
        <el-tabs v-model="activeTab" class="mt-4" stretch>
          <el-tab-pane label="📅 日收益率" name="daily">
            <div class="view-switcher">
              <el-button-group>
                <el-button :type="dailyViewMode === 'chart' ? 'primary' : ''" @click="dailyViewMode = 'chart'">
                  <el-icon><TrendCharts /></el-icon> 折线图
                </el-button>
                <el-button :type="dailyViewMode === 'table' ? 'primary' : ''" @click="dailyViewMode = 'table'">
                  <el-icon><List /></el-icon> 表格
                </el-button>
              </el-button-group>
            </div>

            <!-- 表格视图 -->
            <el-table v-if="dailyViewMode === 'table'" :data="dailyReturns" stripe style="width: 100%" :max-height="350">
              <el-table-column prop="date" label="日期" width="100" />
              <el-table-column label="上证指数收益率" align="right">
                <template #default="{ row }">
                  <el-tag :type="row.sh_index_return >= 0 ? 'danger' : 'success'" size="small">
                    {{ row.sh_index_return >= 0 ? '+' : '' }}{{ row.sh_index_return.toFixed(2) }}%
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="累计收益" align="right">
                <template #default="{ row }">
                  <el-tag :type="row.total_return >= 0 ? 'danger' : 'success'" size="small">
                    {{ row.total_return >= 0 ? '+' : '' }}{{ row.total_return.toFixed(4) }}%
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="total_asset" label="总资产" align="right">
                <template #default="{ row }">
                  <span class="currency">¥{{ row.total_asset?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</span>
                </template>
              </el-table-column>
            </el-table>

            <!-- 折线图视图 -->
            <div v-else ref="dailyChartRef" class="daily-chart"></div>
          </el-tab-pane>

          <el-tab-pane label="📈 周收益率" name="weekly">
            <div class="view-switcher">
              <el-button-group>
                <el-button :type="weeklyViewMode === 'chart' ? 'primary' : ''" @click="weeklyViewMode = 'chart'">
                  <el-icon><TrendCharts /></el-icon> 折线图
                </el-button>
                <el-button :type="weeklyViewMode === 'table' ? 'primary' : ''" @click="weeklyViewMode = 'table'">
                  <el-icon><List /></el-icon> 表格
                </el-button>
              </el-button-group>
            </div>

            <!-- 表格视图 -->
            <el-table v-if="weeklyViewMode === 'table'" :data="weeklyReturns" stripe style="width: 100%" :max-height="350">
              <el-table-column prop="week" label="日期范围" width="140" />
              <el-table-column label="组合周收益率" align="right">
                <template #default="{ row }">
                  <el-tag :type="row.weekly_return >= 0 ? 'danger' : 'success'" size="small">
                    {{ row.weekly_return >= 0 ? '+' : '' }}{{ row.weekly_return.toFixed(2) }}%
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="上证指数收益率" align="right">
                <template #default="{ row }">
                  <el-tag :type="row.sh_index_return >= 0 ? 'danger' : 'success'" size="small">
                    {{ row.sh_index_return >= 0 ? '+' : '' }}{{ row.sh_index_return.toFixed(2) }}%
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="trading_days" label="交易天数" width="90" align="center" />
            </el-table>

            <!-- 折线图视图 -->
            <div v-else ref="weeklyChartRef" class="weekly-chart"></div>
          </el-tab-pane>

          <el-tab-pane label="📉 月收益率" name="monthly">
            <div class="view-switcher">
              <el-button-group>
                <el-button :type="monthlyViewMode === 'chart' ? 'primary' : ''" @click="monthlyViewMode = 'chart'">
                  <el-icon><TrendCharts /></el-icon> 折线图
                </el-button>
                <el-button :type="monthlyViewMode === 'table' ? 'primary' : ''" @click="monthlyViewMode = 'table'">
                  <el-icon><List /></el-icon> 表格
                </el-button>
              </el-button-group>
            </div>

            <!-- 表格视图 -->
            <el-table v-if="monthlyViewMode === 'table'" :data="monthlyReturns" stripe style="width: 100%" :max-height="350">
              <el-table-column prop="month" label="月份" width="100" />
              <el-table-column label="组合月收益率" align="right">
                <template #default="{ row }">
                  <el-tag :type="row.monthly_return >= 0 ? 'danger' : 'success'" size="small">
                    {{ row.monthly_return >= 0 ? '+' : '' }}{{ row.monthly_return.toFixed(2) }}%
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="上证指数收益率" align="right">
                <template #default="{ row }">
                  <el-tag :type="row.sh_index_return >= 0 ? 'danger' : 'success'" size="small">
                    {{ row.sh_index_return >= 0 ? '+' : '' }}{{ row.sh_index_return.toFixed(2) }}%
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="trading_days" label="交易天数" width="90" align="center" />
              <el-table-column label="盈亏天数" align="center">
                <template #default="{ row }">
                  <span class="profit-tag">{{ row.positive_days }}</span> 盈 /
                  <span class="loss-tag">{{ row.negative_days }}</span> 亏
                </template>
              </el-table-column>
            </el-table>

            <!-- 折线图视图 -->
            <div v-else ref="monthlyChartRef" class="monthly-chart"></div>
          </el-tab-pane>

          <el-tab-pane label="📋 月度汇总" name="summary">
            <el-table :data="monthlySummary" stripe style="width: 100%" :max-height="350">
              <el-table-column prop="month" label="月份" width="100" />
              <el-table-column label="组合月收益" align="right">
                <template #default="{ row }">
                  <el-tag :type="row.return >= 0 ? 'danger' : 'success'" size="small">
                    {{ row.return >= 0 ? '+' : '' }}{{ row.return.toFixed(2) }}%
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="上证指数收益率" align="right">
                <template #default="{ row }">
                  <el-tag :type="row.sh_index_return >= 0 ? 'danger' : 'success'" size="small">
                    {{ row.sh_index_return >= 0 ? '+' : '' }}{{ row.sh_index_return.toFixed(2) }}%
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="trading_days" label="交易天数" width="90" align="center" />
              <el-table-column label="盈亏天数比" align="center">
                <template #default="{ row }">
                  <span class="profit-tag">{{ row.positive_days }}</span> /
                  <span class="loss-tag">{{ row.negative_days }}</span>
                  <span class="win-rate">({{ row.win_rate }}%)</span>
                </template>
              </el-table-column>
              <el-table-column label="最大单日收益" align="right">
                <template #default="{ row }">
                  <span class="profit-tag">+{{ row.max_daily.toFixed(2) }}%</span>
                </template>
              </el-table-column>
              <el-table-column label="最大单日亏损" align="right">
                <template #default="{ row }">
                  <span class="loss-tag">{{ row.min_daily.toFixed(2) }}%</span>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>

        <!-- 收益日历热力图 -->
        <div class="section-header mt-4">
          <span class="section-icon">📆</span>
          <span class="section-title">收益日历</span>
        </div>
        <div class="calendar-container mt-2">
          <div class="calendar-legend">
            <span class="legend-label">跌</span>
            <div class="legend-items">
              <div class="legend-item"><div class="legend-box loss-5"></div><span>&lt;-5%</span></div>
              <div class="legend-item"><div class="legend-box loss-3"></div><span>-3%</span></div>
              <div class="legend-item"><div class="legend-box loss-1"></div><span>-1%</span></div>
              <div class="legend-item"><div class="legend-box neutral"></div><span>0%</span></div>
              <div class="legend-item"><div class="legend-box gain-1"></div><span>+1%</span></div>
              <div class="legend-item"><div class="legend-box gain-3"></div><span>+3%</span></div>
              <div class="legend-item"><div class="legend-box gain-5"></div><span>&gt;+5%</span></div>
            </div>
            <span class="legend-label">涨</span>
          </div>
          <div class="calendar-grid" v-if="monthlySummary.length > 0">
            <div v-for="month in monthlySummary" :key="month.month" class="calendar-month">
              <div class="calendar-month-title">{{ month.month }}</div>
              <div class="calendar-weekdays">
                <span>日</span><span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span>
              </div>
              <div class="calendar-days">
                <div
                  v-for="day in getCalendarDays(month.month)"
                  :key="day.date || day.day"
                  class="calendar-day"
                  :class="[getReturnClass(day.return), { empty: !day.date }]"
                  :title="day.date ? `${day.date}: ${day.return >= 0 ? '+' : ''}${day.return.toFixed(4)}%` : ''"
                >
                  <span class="day-num">{{ day.day }}</span>
                  <span v-if="day.return !== 0 && day.date" class="day-return" :class="day.return >= 0 ? 'profit' : 'loss'">
                    {{ day.return >= 0 ? '+' : '' }}{{ day.return.toFixed(2) }}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { sim } from '../api'
import * as echarts from 'echarts'

const stats = ref({})
const positions = ref([])
const allTrades = ref([])
const statsLoaded = ref(false)

const analysisData = ref({})
const analysisLoaded = ref(false)
const activeTab = ref('daily')
const dailyViewMode = ref('chart')
const weeklyViewMode = ref('chart')
const monthlyViewMode = ref('chart')
const dailyChartRef = ref(null)
const weeklyChartRef = ref(null)
const monthlyChartRef = ref(null)
let dailyChartInstance = null
let weeklyChartInstance = null
let monthlyChartInstance = null

const dailyReturns = computed(() => analysisData.value.daily_returns || [])
const weeklyReturns = computed(() => analysisData.value.weekly_returns || [])
const monthlyReturns = computed(() => analysisData.value.monthly_returns || [])
const monthlySummary = computed(() => analysisData.value.monthly_summary || [])
const calendarData = computed(() => analysisData.value.calendar_data || [])

const latestDailyReturn = computed(() => {
  const returns = dailyReturns.value
  return returns.length > 0 ? returns[0]?.daily_return : 0
})
const latestWeeklyReturn = computed(() => {
  const returns = weeklyReturns.value
  return returns.length > 0 ? returns[0]?.weekly_return : 0
})
const latestMonthlyReturn = computed(() => {
  const returns = monthlyReturns.value
  return returns.length > 0 ? returns[0]?.monthly_return : 0
})

// 获取某月的交易日历数据
const getCalendarDays = (monthStr) => {
  const [year, month] = monthStr.split('-').map(Number)
  const daysInMonth = new Date(year, month, 0).getDate()
  const firstDayOfWeek = new Date(year, month - 1, 1).getDay()

  const result = []

  // 填充空白
  for (let i = 0; i < firstDayOfWeek; i++) {
    result.push({ date: '', day: '-', return: 0 })
  }

  // 填充日期
  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    const dayData = calendarData.value.find(d => d.date === dateStr)
    result.push({
      date: dateStr,
      day: day,
      return: dayData ? dayData.return : 0  // 直接使用百分比数据
    })
  }

  return result
}

// 根据收益率返回 CSS 类
const getReturnClass = (ret) => {
  if (ret === 0 || ret === undefined) return ''  // 无数据或 0%
  if (ret >= 5) return 'gain-5'   // ≥+5% 深红
  if (ret >= 3) return 'gain-3'   // +3%~+5% 中红
  if (ret > 0) return 'gain-1'    // +0.01%~+3% 浅红
  if (ret >= -1) return 'loss-1'  // -1%~0% 浅绿
  if (ret >= -3) return 'loss-3'  // -3%~-1% 中绿
  return 'loss-5'                 // ≤-3% 深绿
}

const loadStats = async () => {
  try {
    const res = await sim.getStats()
    if (res.data.success) {
      stats.value = res.data.data
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadPositions = async () => {
  try {
    const res = await sim.getPositions()
    if (res.data.success) {
      positions.value = res.data.data
    }
  } catch (error) {
    console.error('加载持仓失败:', error)
  }
}

const loadTrades = async () => {
  try {
    const res = await sim.getTrades()
    if (res.data.success) {
      allTrades.value = res.data.data
    }
  } catch (error) {
    console.error('加载交易记录失败:', error)
  }
}

const loadAnalysis = async () => {
  try {
    const res = await sim.getAnalysis()
    if (res.data.success) {
      analysisData.value = res.data.data
      // 只初始化当前激活的图表
      setTimeout(() => {
        if (activeTab.value === 'daily' && dailyViewMode.value === 'chart') {
          initDailyChart()
        }
      }, 200)
    }
  } catch (error) {
    console.error('加载收益分析失败:', error)
  } finally {
    analysisLoaded.value = true
  }
}

// 初始化日收益率折线图
const initDailyChart = () => {
  if (!dailyChartRef.value) return

  const chartDom = dailyChartRef.value
  if (!chartDom || !chartDom.offsetHeight) return

  if (dailyChartInstance) {
    dailyChartInstance.dispose()
  }
  dailyChartInstance = echarts.init(chartDom)

  const data = dailyReturns.value.slice().reverse()
  const dates = data.map(d => d.date.slice(5))
  const dailyReturnsData = data.map(d => d.daily_return)  // 转换为百分比
  const totalReturns = data.map(d => d.total_return)  // 转换为百分比
  const shIndexReturns = data.map(d => d.sh_index_return || 0)  // 转换为百分比

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: (params) => {
        const date = params[0].name
        let html = `<div style="padding: 8px; font-weight: bold;">${date}</div>`
        params.forEach(p => {
          const color = p.value >= 0 ? '#f56c6c' : '#67c23a'
          const sign = p.value >= 0 ? '+' : ''
          html += `<div style="padding: 4px 8px;">
            <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${color};margin-right:8px;"></span>
            <span style="color:${color};font-weight:bold;">${p.seriesName}: ${sign}${p.value.toFixed(2)}%</span>
          </div>`
        })
        return html
      }
    },
    legend: {
      data: ['日收益率', '累计收益', '上证指数'],
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
    yAxis: {
      type: 'value',
      name: '收益率 (%)',
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
        name: '日收益率',
        type: 'line',
        data: dailyReturnsData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: '#f56c6c' },
        lineStyle: { width: 2 }
      },
      {
        name: '累计收益',
        type: 'line',
        data: totalReturns,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: '#409EFF' },
        lineStyle: { width: 2 }
      },
      {
        name: '上证指数',
        type: 'line',
        data: shIndexReturns,
        smooth: true,
        symbol: 'none',
        itemStyle: { color: '#67c23a' },
        lineStyle: { width: 2, type: 'dashed' }
      }
    ]
  }

  dailyChartInstance.setOption(option)
}

// 初始化周收益率折线图
const initWeeklyChart = () => {
  if (!weeklyChartRef.value) return

  const chartDom = weeklyChartRef.value
  if (!chartDom || !chartDom.offsetHeight) return

  if (weeklyChartInstance) {
    weeklyChartInstance.dispose()
  }
  weeklyChartInstance = echarts.init(chartDom)

  const data = weeklyReturns.value.slice().reverse()
  const weeks = data.map(d => d.week)
  const weeklyReturnsData = data.map(d => d.weekly_return)
  const shIndexReturns = data.map(d => d.sh_index_return || 0)  // 转换为百分比

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const week = params[0].name
        let html = `<div style="padding: 8px;">`
        params.forEach(p => {
          const value = p.value
          const sign = value >= 0 ? '+' : ''
          const color = value >= 0 ? '#f56c6c' : '#67c23a'
          html += `<div style="color: ${color}; font-weight: bold; margin-bottom: 4px;">
            ${p.seriesName}: ${sign}${value.toFixed(2)}%
          </div>`
        })
        html += `</div>`
        return html
      }
    },
    legend: {
      data: ['组合周收益率', '上证指数'],
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
        interval: Math.floor(weeks.length / 12)
      }
    },
    yAxis: {
      type: 'value',
      name: '收益率 (%)',
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
        name: '组合周收益率',
        type: 'line',
        data: weeklyReturnsData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: '#f56c6c' },
        lineStyle: { width: 2 }
      },
      {
        name: '上证指数',
        type: 'line',
        data: shIndexReturns,
        smooth: true,
        symbol: 'none',
        itemStyle: { color: '#67c23a' },
        lineStyle: { width: 2, type: 'dashed' }
      }
    ]
  }

  weeklyChartInstance.setOption(option)
}

// 初始化月收益率折线图
const initMonthlyChart = () => {
  if (!monthlyChartRef.value) return

  const chartDom = monthlyChartRef.value
  if (!chartDom || !chartDom.offsetHeight) return

  if (monthlyChartInstance) {
    monthlyChartInstance.dispose()
  }
  monthlyChartInstance = echarts.init(chartDom)

  const data = monthlyReturns.value.slice().reverse()
  const months = data.map(d => d.month.slice(5))
  const monthlyReturnsData = data.map(d => d.monthly_return)
  const shIndexReturns = data.map(d => d.sh_index_return || 0)  // 转换为百分比

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const month = params[0].name
        let html = `<div style="padding: 8px;">`
        params.forEach(p => {
          const value = p.value
          const sign = value >= 0 ? '+' : ''
          const color = value >= 0 ? '#f56c6c' : '#67c23a'
          html += `<div style="color: ${color}; font-weight: bold; margin-bottom: 4px;">
            ${p.seriesName}: ${sign}${value.toFixed(2)}%
          </div>`
        })
        html += `</div>`
        return html
      }
    },
    legend: {
      data: ['组合月收益率', '上证指数'],
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
      name: '收益率 (%)',
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
        name: '组合月收益率',
        type: 'line',
        data: monthlyReturnsData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: '#f56c6c' },
        lineStyle: { width: 2 }
      },
      {
        name: '上证指数',
        type: 'line',
        data: shIndexReturns,
        smooth: true,
        symbol: 'none',
        itemStyle: { color: '#67c23a' },
        lineStyle: { width: 2, type: 'dashed' }
      }
    ]
  }

  monthlyChartInstance.setOption(option)
}

// 监听视图模式切换和数据变化
watch([dailyViewMode, dailyReturns, activeTab], () => {
  if (dailyViewMode.value === 'chart' && activeTab.value === 'daily') {
    setTimeout(() => initDailyChart(), 100)
  }
}, { deep: true })

watch([weeklyViewMode, weeklyReturns, activeTab], () => {
  if (weeklyViewMode.value === 'chart' && activeTab.value === 'weekly') {
    setTimeout(() => initWeeklyChart(), 100)
  }
}, { deep: true })

watch([monthlyViewMode, monthlyReturns, activeTab], () => {
  if (monthlyViewMode.value === 'chart' && activeTab.value === 'monthly') {
    setTimeout(() => initMonthlyChart(), 100)
  }
}, { deep: true })

// 监听 tab 切换
watch(activeTab, (newTab) => {
  setTimeout(() => {
    if (newTab === 'daily' && dailyViewMode.value === 'chart') {
      initDailyChart()
    } else if (newTab === 'weekly' && weeklyViewMode.value === 'chart') {
      initWeeklyChart()
    } else if (newTab === 'monthly' && monthlyViewMode.value === 'chart') {
      initMonthlyChart()
    }
  }, 50)
})

onMounted(async () => {
  await Promise.all([loadStats(), loadPositions(), loadTrades(), loadAnalysis()])
  statsLoaded.value = true

  window.addEventListener('resize', () => {
    if (dailyChartInstance) dailyChartInstance.resize()
    if (weeklyChartInstance) weeklyChartInstance.resize()
    if (monthlyChartInstance) monthlyChartInstance.resize()
  })
})
</script>

<style scoped>
.sim-analysis {
  padding: 15px;
}

.mb-4 {
  margin-bottom: 20px;
}

.mt-2 {
  margin-top: 10px;
}

.mt-4 {
  margin-top: 20px;
}

/* 统计卡片 */
.stat-card {
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header .icon-red { color: #f56c6c; }
.card-header .icon-blue { color: #409EFF; }
.card-header .icon-orange { color: #e6a23c; }

.stat-value {
  font-size: 26px;
  font-weight: bold;
  text-align: center;
  padding: 12px 0;
}

.stat-value.profit {
  color: #f56c6c;
}

.stat-value.loss {
  color: #67c23a;
}

.stat-sub {
  text-align: center;
  color: #909399;
  font-size: 14px;  /* 增大字体 */
  padding-bottom: 12px;
}

/* 分析卡片 */
.analysis-card {
  margin-top: 20px;
}

/* 概览卡片 */
.overview-card {
  margin-bottom: 20px;
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

/* 表格样式 */
:deep(.el-table) {
  font-size: 14px;  /* 增大字体 */
}

:deep(.el-table th) {
  background: #fafafa;
  color: #606266;
  font-weight: 600;
}

:deep(.el-table__row:hover) {
  background: #f5f7fa;
}

/* 视图切换器 */
.view-switcher {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}

/* 折线图容器 */
.daily-chart,
.weekly-chart,
.monthly-chart {
  width: 100%;
  height: 400px;
}

/* 选项卡样式 */
:deep(.el-tabs__item) {
  font-size: 14px;
  padding: 0 20px;
}

:deep(.el-tabs__header) {
  margin-bottom: 16px;
}

:deep(.el-tabs__active-bar) {
  background: #409EFF;
}

.currency {
  color: #606266;
  font-family: 'Segoe UI', monospace;
}

/* 盈亏标签 */
.profit-tag {
  color: #f56c6c;
  font-weight: bold;
}

.loss-tag {
  color: #67c23a;
  font-weight: bold;
}

.win-rate {
  color: #909399;
  font-size: 12px;
  margin-left: 4px;
}

/* 日历热力图 */
.calendar-container {
  margin-top: 10px;
}

.calendar-legend {
  display: flex;
  align-items: center;
  justify-content: space-between;  /* 分散对齐 */
  gap: 12px;
  margin-bottom: 20px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
  border-radius: 8px;
}

.legend-label {
  font-size: 14px;  /* 增大字体 */
  color: #606266;
  font-weight: 500;
}

.legend-items {
  display: flex;
  align-items: center;
  gap: 10px;
}

.legend-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
}

.legend-box {
  width: 22px;
  height: 22px;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.legend-box.gain-5 { background: #dc3545; }
.legend-box.gain-3 { background: #f46a6a; }
.legend-box.gain-1 { background: #ff9b9b; }
.legend-box.neutral { background: #e4e7ed; }
.legend-box.loss-1 { background: #9acd32; }
.legend-box.loss-3 { background: #7cba32; }
.legend-box.loss-5 { background: #5faa32; }

.legend-item span {
  font-size: 10px;
  color: #909399;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.calendar-month {
  background: #ffffff;
  border-radius: 10px;
  padding: 14px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.3s;
}

.calendar-month:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.calendar-month-title {
  font-size: 15px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
  text-align: center;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 3px;
  margin-bottom: 6px;
}

.calendar-weekdays span {
  text-align: center;
  font-size: 12px;  /* 增大字体 */
  color: #909399;
  padding: 6px 0;
  font-weight: 500;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 3px;
}

.calendar-day {
  aspect-ratio: 1;
  min-height: 60px;  /* 增大最小高度 */
  border-radius: 6px;
  padding: 4px;  /* 增加内边距 */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;  /* 分散对齐 */
  font-size: 12px;  /* 增大字体 */
  border: 1px solid transparent;
  transition: transform 0.2s;
}

.calendar-day.empty {
  visibility: hidden;
}

.calendar-day:hover {
  transform: scale(1.05);
}

.calendar-day.gain-5 { background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); border-color: #dc3545; box-shadow: 0 2px 6px rgba(220, 53, 69, 0.4); }
.calendar-day.gain-3 { background: linear-gradient(135deg, #f46a6a 0%, #e55a5a 100%); border-color: #f46a6a; box-shadow: 0 2px 6px rgba(244, 106, 106, 0.3); }
.calendar-day.gain-1 { background: linear-gradient(135deg, #ff9b9b 0%, #ff8b8b 100%); border-color: #ff9b9b; }
.calendar-day.loss-1 { background: linear-gradient(135deg, #9acd32 0%, #8ac222 100%); border-color: #9acd32; }
.calendar-day.loss-3 { background: linear-gradient(135deg, #7cba32 0%, #6eae24 100%); border-color: #7cba32; box-shadow: 0 2px 6px rgba(124, 186, 50, 0.3); }
.calendar-day.loss-5 { background: linear-gradient(135deg, #5faa32 0%, #519a24 100%); border-color: #5faa32; box-shadow: 0 2px 6px rgba(95, 170, 50, 0.4); }

.day-num {  /* 日期数字更大更清晰 */
  font-weight: bold;
  font-size: 14px;  /* 增大字体 */
  color: #333333;
}

.day-return {  /* 收益率显示优化 */
  font-size: 12px;  /* 增大字体 */
  margin-top: 2px;
  font-weight: 600;
  color: #ffffff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.calendar-day.gain-5 .day-return,
.calendar-day.gain-3 .day-return,
.calendar-day.loss-3 .day-return,
.calendar-day.loss-5 .day-return {  /* 收益率显示优化 */
  color: #ffffff;
}

.calendar-day:not(.gain-5):not(.gain-3):not(.loss-3):not(.loss-5):hover {
  border-color: #409EFF;
}
</style>
