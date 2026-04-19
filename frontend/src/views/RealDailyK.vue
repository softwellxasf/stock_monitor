<template>
  <div class="real-daily-k">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>📈 日 K 记录</span>
          <div class="header-info">
            <el-tag v-if="currentStock" type="success">{{ currentStock.name }}</el-tag>
            <el-tag v-if="currentPrice" type="warning">现价：¥{{ currentPrice.toFixed(2) }}</el-tag>
          </div>
        </div>
      </template>

      <!-- 查询条件 -->
      <div class="search-bar">
        <el-select
          v-model="searchForm.stockCode"
          placeholder="选择股票"
          filterable
          style="width: 240px"
          @change="onStockChange"
        >
          <el-option
            v-for="stock in stockList"
            :key="stock.code"
            :label="`${stock.code} ${stock.name}`"
            :value="stock.code"
          />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          style="width: 240px"
          @change="loadDailyKData"
        />
        <el-button type="primary" @click="loadDailyKData" :loading="loading">
          <el-icon><Search /></el-icon> 查询
        </el-button>
      </div>

      <!-- K 线图表容器 -->
      <div ref="chartContainer" class="chart-container" v-loading="loading"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { actual, dailyK } from '../api'
import { ElMessage } from 'element-plus'
import { createChart, ColorType, CrosshairMode } from 'lightweight-charts'

const loading = ref(false)
const stockList = ref([])
const chartContainer = ref(null)
const currentStock = ref(null)
const currentPrice = ref(0)
const tradeRecords = ref([])

let chart = null
let candlestickSeries = null
let volumeSeries = null
let ma5Series = null
let ma10Series = null
let ma20Series = null

const defaultDateRange = computed(() => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 180)
  return [start.toISOString().split('T')[0], end.toISOString().split('T')[0]]
})

const searchForm = ref({
  stockCode: '',
  dateRange: []
})

// 日期选择器绑定的值
const dateRange = ref([])

// 初始化图表
const initChart = () => {
  if (!chartContainer.value) return

  // 销毁旧图表
  if (chart) {
    chart.remove()
  }

  // 创建新图表（TradingView 风格）
  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: 600,
    layout: {
      background: { type: ColorType.Solid, color: '#FFFFFF' },
      textColor: '#333333',
    },
    grid: {
      vertLines: { color: '#f0f0f0' },
      horzLines: { color: '#f0f0f0' },
    },
    crosshair: {
      mode: CrosshairMode.Normal,
      vertLine: {
        labelBackgroundColor: '#2962FF',
      },
      horzLine: {
        labelBackgroundColor: '#2962FF',
      },
    },
    rightPriceScale: {
      borderColor: '#e0e0e0',
      scaleMargins: {
        top: 0.2,
        bottom: 0.2,
      },
    },
    timeScale: {
      borderColor: '#e0e0e0',
      timeVisible: true,
      secondsVisible: false,
    },
  })

  // 添加 K 线系列（红涨绿跌）
  candlestickSeries = chart.addCandlestickSeries({
    upColor: '#FF0000',
    downColor: '#00CC00',
    borderUpColor: '#FF0000',
    borderDownColor: '#00CC00',
    wickUpColor: '#FF0000',
    wickDownColor: '#00CC00',
  })

  // 添加成交量系列
  volumeSeries = chart.addHistogramSeries({
    color: '#26a69a',
    priceFormat: {
      type: 'volume',
    },
    priceScaleId: '',
    scaleMargins: {
      top: 0.85,
      bottom: 0,
    },
  })

  // 添加 MA5 均线
  ma5Series = chart.addLineSeries({
    color: '#FFFFFF',
    lineWidth: 2,
    title: 'MA5',
  })

  // 添加 MA10 均线
  ma10Series = chart.addLineSeries({
    color: '#FFD700',
    lineWidth: 2,
    title: 'MA10',
  })

  // 添加 MA20 均线
  ma20Series = chart.addLineSeries({
    color: '#00FFFF',
    lineWidth: 2,
    title: 'MA20',
  })

  // 自适应窗口大小
  window.addEventListener('resize', handleResize)
}

// 处理窗口大小变化
const handleResize = () => {
  if (chart && chartContainer.value) {
    chart.applyOptions({
      width: chartContainer.value.clientWidth,
    })
  }
}

// 计算 MA 均线
const calculateMA = (data, period) => {
  const ma = []
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) continue
    let sum = 0
    for (let j = 0; j < period; j++) {
      sum += data[i - j].close
    }
    ma.push({
      time: data[i].time,
      value: sum / period,
    })
  }
  return ma
}

// 加载股票列表（从实盘持仓）
const loadStockList = async () => {
  try {
    const res = await actual.getPositions({ page: 1, page_size: 100 })
    if (res.data.success) {
      stockList.value = res.data.data.map(s => ({
        code: s.stock_code,
        name: s.stock_name,
        current_price: parseFloat(s.current_price) || 0
      }))
      if (stockList.value.length > 0) {
        searchForm.value.stockCode = stockList.value[0].code
        currentStock.value = stockList.value[0]
        currentPrice.value = stockList.value[0].current_price
        loadDailyKData()
      }
    }
  } catch (error) {
    console.error('加载股票列表失败:', error)
  }
}

// 股票选择变化
const onStockChange = (code) => {
  currentStock.value = stockList.value.find(s => s.code === code)
  currentPrice.value = currentStock.value?.current_price || 0
  loadDailyKData()
}

// 加载日 K 数据
const loadDailyKData = async () => {
  if (!searchForm.value.stockCode) return

  loading.value = true
  try {
    const range = dateRange.value || defaultDateRange.value
    const [start, end] = range

    console.log('查询日期范围:', start, end)
    console.log('股票代码:', searchForm.value.stockCode)

    // 获取真实日 K 数据
    const res = await dailyK.getData(searchForm.value.stockCode, start, end)

    // 获取交易记录
    const tradesRes = await actual.getTrades({
      stock_code: searchForm.value.stockCode,
      start_date: start,
      end_date: end
    })
    if (tradesRes.data.success) {
      tradeRecords.value = tradesRes.data.data || []
      console.log('交易记录:', tradeRecords.value.length, '条')
    }

    if (res.data.success) {
      const kData = res.data.data

      // 准备图表数据
      const candleData = kData.map(item => ({
        time: item.date,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
      }))

      const volumeData = kData.map(item => ({
        time: item.date,
        value: item.volume,
        color: item.close >= item.open ? '#FF0000' : '#00CC00',
      }))

      // 计算均线
      const ma5Data = calculateMA(candleData, 5)
      const ma10Data = calculateMA(candleData, 10)
      const ma20Data = calculateMA(candleData, 20)

      // 更新图表
      candlestickSeries.setData(candleData)
      volumeSeries.setData(volumeData)
      ma5Series.setData(ma5Data)
      ma10Series.setData(ma10Data)
      ma20Series.setData(ma20Data)

      // 添加交易标记
      updateMarkers(candleData)

      console.log('K 线数据:', candleData.length, '条')
      console.log('均线数据：MA5=' + ma5Data.length + ', MA10=' + ma10Data.length + ', MA20=' + ma20Data.length)
    }
  } catch (error) {
    console.error('加载日 K 数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 更新交易标记
const updateMarkers = (candleData) => {
  const markers = []

  tradeRecords.value.forEach(trade => {
    const tradeDate = trade.trade_date?.split(' ')[0] || trade.trade_date
    const dataIndex = candleData.findIndex(d => d.time === tradeDate)
    if (dataIndex === -1) return

    const candle = candleData[dataIndex]
    const isTTrade = trade.remark?.includes('T') || trade.remark?.includes('做 T')

    if (trade.direction === 'BUY') {
      if (isTTrade) {
        // 做 T 买入：橙色小圆点
        markers.push({
          time: tradeDate,
          position: 'belowBar',
          color: '#FF9900',
          shape: 'circle',
          text: 'T',
          size: 0.5,
        })
      } else {
        // 底仓买入：红色圆形 B
        markers.push({
          time: tradeDate,
          position: 'belowBar',
          color: '#FF4444',
          shape: 'circle',
          text: 'B',
          size: 1,
        })
      }
    } else if (trade.direction === 'SELL') {
      if (isTTrade) {
        // 做 T 卖出：绿色小圆点
        markers.push({
          time: tradeDate,
          position: 'aboveBar',
          color: '#00CC00',
          shape: 'circle',
          text: 'T',
          size: 0.5,
        })
      } else {
        // 底仓卖出：蓝色圆形 S
        markers.push({
          time: tradeDate,
          position: 'aboveBar',
          color: '#4488FF',
          shape: 'circle',
          text: 'S',
          size: 1,
        })
      }
    }
  })

  candlestickSeries.setMarkers(markers)
  console.log('交易标记:', markers.length, '个')
}

// 清理资源
onUnmounted(() => {
  if (chart) {
    chart.remove()
    window.removeEventListener('resize', handleResize)
  }
})

onMounted(() => {
  // 初始化日期范围为默认值（近 180 天）
  dateRange.value = defaultDateRange.value
  initChart()
  loadStockList()
})
</script>

<style scoped>
.real-daily-k {
  padding: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info {
  display: flex;
  gap: 8px;
  align-items: center;
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
  align-items: center;
}

.chart-container {
  width: 100%;
  height: 600px;
}
</style>
