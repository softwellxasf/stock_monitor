<template>
  <div class="kline-chart">
    <el-card shadow="never" class="chart-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="title">K 线图</span>
            <el-tag v-if="currentStock" class="stock-tag" type="success">
              {{ currentStock.code }} - {{ currentStock.name }}
            </el-tag>
            <el-tag v-if="currentPrice" class="price-tag" type="warning">
              现价：¥{{ currentPrice.toFixed(2) }}
            </el-tag>
          </div>
          <div class="header-right">
            <el-radio-group v-model="klineType" size="small" @change="onKlineTypeChange">
              <el-radio-button label="day">日 K</el-radio-button>
              <el-radio-button label="week">周 K</el-radio-button>
              <el-radio-button label="month">月 K</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>

      <!-- 工具栏 -->
      <div class="toolbar">
        <el-select
          v-model="selectedStockCode"
          placeholder="选择股票"
          filterable
          style="width: 280px"
          @change="onStockChange"
        >
          <el-option
            v-for="stock in stockList"
            :key="stock.code"
            :label="`${stock.code} - ${stock.name}`"
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
          @change="loadData"
        />
        <el-button type="primary" size="small" @click="loadData" :loading="loading">
          <el-icon><Search /></el-icon> 查询
        </el-button>
      </div>

      <!-- 主图表区 -->
      <div class="chart-wrapper" v-loading="loading">
        <!-- 悬浮数据框 -->
        <div v-if="hoverData.time" class="floating-tooltip">
          <div class="tooltip-date">{{ hoverData.time }}</div>
          <div class="tooltip-row">
            <span class="tooltip-label">O:</span>
            <span :class="getPriceClass(hoverData.open, hoverData.close)" class="tooltip-value">{{ hoverData.open?.toFixed(2) }}</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">H:</span>
            <span :class="getPriceClass(hoverData.high, hoverData.close)" class="tooltip-value">{{ hoverData.high?.toFixed(2) }}</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">L:</span>
            <span :class="getPriceClass(hoverData.low, hoverData.close)" class="tooltip-value">{{ hoverData.low?.toFixed(2) }}</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">C:</span>
            <span :class="getPriceClass(hoverData.close, hoverData.close)" class="tooltip-value">{{ hoverData.close?.toFixed(2) }}</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">V:</span>
            <span class="tooltip-value">{{ formatVolume(hoverData.volume) }}</span>
          </div>
          <!-- 交易记录 -->
          <div v-for="(trade, idx) in hoverData.trades" :key="idx" :class="['tooltip-trade', trade.direction === 'BUY' ? 'trade-buy' : 'trade-sell']">
            <div class="tooltip-trade-label">{{ trade.direction === 'BUY' ? '买入' : '卖出' }} {{ trade.remark ? `(${trade.remark})` : '' }}</div>
            <div class="tooltip-trade-row">
              <span class="tooltip-label">价格:</span>
              <span class="tooltip-value">{{ trade.price?.toFixed(2) }}</span>
            </div>
            <div class="tooltip-trade-row">
              <span class="tooltip-label">数量:</span>
              <span class="tooltip-value">{{ trade.volume }}</span>
            </div>
          </div>
          <div class="tooltip-divider"></div>
          <div class="tooltip-row">
            <span class="tooltip-label">DIF:</span>
            <span class="tooltip-value dif">{{ hoverData.dif?.toFixed(4) }}</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">DEA:</span>
            <span class="tooltip-value dea">{{ hoverData.dea?.toFixed(4) }}</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">MACD:</span>
            <span :class="hoverData.macd >= 0 ? 'price-up' : 'price-down'" class="tooltip-value">{{ hoverData.macd?.toFixed(4) }}</span>
          </div>
        </div>
        <!-- K 线主图 -->
        <div ref="mainChartContainer" class="main-chart"></div>
        <!-- 副图 (MACD + 成交量) -->
        <div ref="subChartContainer" class="sub-chart"></div>
      </div>

      <!-- 图例信息 -->
      <div class="legend">
        <span class="legend-item">
          O: <span :class="getPriceClass(currentData?.open, currentData?.close)">{{ currentData?.open?.toFixed(2) || '-' }}</span>
        </span>
        <span class="legend-item">
          H: <span :class="getPriceClass(currentData?.high, currentData?.close)">{{ currentData?.high?.toFixed(2) || '-' }}</span>
        </span>
        <span class="legend-item">
          L: <span :class="getPriceClass(currentData?.low, currentData?.close)">{{ currentData?.low?.toFixed(2) || '-' }}</span>
        </span>
        <span class="legend-item">
          C: <span :class="getPriceClass(currentData?.close, currentData?.close)">{{ currentData?.close?.toFixed(2) || '-' }}</span>
        </span>
        <span class="legend-item ma5">
          MA5: <span>{{ currentMA5?.toFixed(2) || '-' }}</span>
        </span>
        <span class="legend-item ma10">
          MA10: <span>{{ currentMA10?.toFixed(2) || '-' }}</span>
        </span>
        <span class="legend-item ma20">
          MA20: <span>{{ currentMA20?.toFixed(2) || '-' }}</span>
        </span>
        <span class="legend-item">
          V: <span>{{ formatVolume(currentData?.volume) }}</span>
        </span>
        <span class="legend-item macd-dif">
          DIF: <span>{{ currentDIF?.toFixed(4) || '-' }}</span>
        </span>
        <span class="legend-item macd-dea">
          DEA: <span>{{ currentDEA?.toFixed(4) || '-' }}</span>
        </span>
        <span class="legend-item macd-hist">
          MACD: <span :class="currentMACD >= 0 ? 'price-up' : 'price-down'">{{ currentMACD?.toFixed(4) || '-' }}</span>
        </span>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { createChart, ColorType, CrosshairMode, LineType } from 'lightweight-charts'
import { ElMessage } from 'element-plus'
import { sim, dailyK } from '../api'

// ============ 状态 ============
const loading = ref(false)
const stockList = ref([])
const selectedStockCode = ref('')
const currentStock = ref(null)
const currentPrice = ref(0)
const tradeRecords = ref([])
const klineType = ref('day')
const dateRange = ref([])

// 当前数据 - 使用 shallowRef 试试
const currentData = ref({ time: '', open: null, high: null, low: null, close: null, volume: null })
const currentMA5 = ref(null)
const currentMA10 = ref(null)
const currentMA20 = ref(null)
const currentDIF = ref(null)
const currentDEA = ref(null)
const currentMACD = ref(null)

// 悬浮框数据
const hoverData = ref({
  time: '',
  open: null,
  high: null,
  low: null,
  close: null,
  volume: null,
  dif: null,
  dea: null,
  macd: null,
  trade: null, // { direction, price, volume }
})

// 存储交易记录 Map，用于快速查找
let tradeDataMap = new Map()

// 存储完整数据用于十字光标显示
let candleDataMap = new Map()
let macdDataMap = new Map()
let ma5DataMap = new Map()
let ma10DataMap = new Map()
let ma20DataMap = new Map()

// 图表实例
let mainChart = null
let subChart = null
let candlestickSeries = null
let ma5Series = null
let ma10Series = null
let ma20Series = null
let macdSeries = null
let macdSignalSeries = null
let macdHistogramSeries = null

// 主图表容器引用
const mainChartContainer = ref(null)
// 副图容器引用
const subChartContainer = ref(null)

// ============ 计算属性 ============
const defaultDateRange = computed(() => {
  const end = new Date()
  const start = new Date()
  // 日 K 默认近 1 年，周 K/月 K 默认近 6 个月
  const days = klineType.value === 'day' ? 365 : 180
  start.setDate(start.getDate() - days)
  return [start.toISOString().split('T')[0], end.toISOString().split('T')[0]]
})

// ============ 初始化 ============
const initCharts = () => {
  initMainChart()
  initSubChart()
}

const initMainChart = () => {
  if (!mainChartContainer.value) return

  if (mainChart) {
    mainChart.remove()
  }

  mainChart = createChart(mainChartContainer.value, {
    width: mainChartContainer.value.clientWidth,
    height: 500,
    layout: {
      background: { type: ColorType.Solid, color: '#1a1a2e' },
      textColor: '#d1d4dc',
      fontSize: 12,
    },
    grid: {
      vertLines: { color: 'rgba(42, 46, 57, 0.4)' },
      horzLines: { color: 'rgba(42, 46, 57, 0.4)' },
    },
    crosshair: {
      mode: CrosshairMode.Normal,
      vertLine: {
        color: 'rgba(224, 227, 235, 0.8)',
        labelBackgroundColor: '#2962FF',
        style: 3,
      },
      horzLine: {
        color: 'rgba(224, 227, 235, 0.8)',
        labelBackgroundColor: '#2962FF',
        style: 3,
      },
    },
    rightPriceScale: {
      borderColor: 'rgba(197, 203, 206, 0.8)',
      scaleMargins: {
        top: 0.15,
        bottom: 0.2,
      },
      alignLabels: true,
    },
    timeScale: {
      borderColor: 'rgba(197, 203, 206, 0.8)',
      timeVisible: true,
      secondsVisible: false,
      fixLeftEdge: false,
      fixRightEdge: false,
      lockVisibleTimeRangeOnResize: true,
    },
    handleScroll: {
      wheel: true,
      pressedMouseMove: true,
      horzTouchDrag: true,
      vertTouchDrag: false,
    },
  })

  // K 线系列（红涨绿跌）
  candlestickSeries = mainChart.addCandlestickSeries({
    upColor: '#ef5350',
    downColor: '#26a69a',
    borderUpColor: '#ef5350',
    borderDownColor: '#26a69a',
    wickUpColor: '#ef5350',
    wickDownColor: '#26a69a',
    priceLineVisible: false,
  })

  // MA5 均线
  ma5Series = mainChart.addLineSeries({
    color: '#ff9800',
    lineWidth: 2,
    title: 'MA5',
    priceLineVisible: false,
    lastValueVisible: true,
  })

  // MA10 均线
  ma10Series = mainChart.addLineSeries({
    color: '#00bcd4',
    lineWidth: 2,
    title: 'MA10',
    priceLineVisible: false,
    lastValueVisible: true,
  })

  // MA20 均线
  ma20Series = mainChart.addLineSeries({
    color: '#9c27b0',
    lineWidth: 2,
    title: 'MA20',
    priceLineVisible: false,
    lastValueVisible: true,
  })

  // 自适应窗口大小
  window.addEventListener('resize', handleResize)
}

// 副图 (MACD + 成交量)
const initSubChart = () => {
  if (!subChartContainer.value) return

  subChart = createChart(subChartContainer.value, {
    width: subChartContainer.value.clientWidth,
    height: 280,
    layout: {
      background: { type: ColorType.Solid, color: '#1a1a2e' },
      textColor: '#d1d4dc',
      fontSize: 12,
    },
    grid: {
      vertLines: { color: 'rgba(42, 46, 57, 0.4)' },
      horzLines: { color: 'rgba(42, 46, 57, 0.4)' },
    },
    crosshair: {
      mode: CrosshairMode.Normal,
      vertLine: {
        color: 'rgba(224, 227, 235, 0.8)',
        labelBackgroundColor: '#2962FF',
        style: 3,
      },
      horzLine: {
        color: 'rgba(224, 227, 235, 0.8)',
        labelBackgroundColor: '#2962FF',
        style: 3,
      },
    },
    rightPriceScale: {
      borderColor: 'rgba(197, 203, 206, 0.8)',
      // MACD 线需要更多空间
      scaleMargins: {
        top: 0.05,
        bottom: 0.35,
      },
    },
    timeScale: {
      borderColor: 'rgba(197, 203, 206, 0.8)',
      timeVisible: true,
      secondsVisible: false,
    },
    handleScroll: {
      wheel: true,
      pressedMouseMove: true,
      horzTouchDrag: true,
      vertTouchDrag: false,
    },
  })

  // MACD DIF 线（蓝色）
  macdSeries = subChart.addLineSeries({
    color: '#2962FF',
    lineWidth: 2,
    title: 'DIF',
    priceLineVisible: false,
    lastValueVisible: true,
    lastValuePriceLine: true,
    priceScaleId: 'right',
  })

  // MACD DEA 线（橙色）
  macdSignalSeries = subChart.addLineSeries({
    color: '#ff6d00',
    lineWidth: 2,
    title: 'DEA',
    priceLineVisible: false,
    lastValueVisible: true,
    lastValuePriceLine: true,
    priceScaleId: 'right',
  })

  // MACD Histogram（柱状图，零轴附近）
  macdHistogramSeries = subChart.addHistogramSeries({
    priceFormat: {
      type: 'volume',
    },
    priceScaleId: '',
    scaleMargins: {
      top: 0.72,
      bottom: 0,
    },
    color: '#ef5350',
    lastValueVisible: false,
    priceLineVisible: false,
  })

  // 成交量系列 - 不显示

  // 同步主图时间轴
  if (mainChart) {
    mainChart.timeScale().subscribeVisibleLogicalRangeChange((range) => {
      if (range && subChart) {
        subChart.timeScale().setVisibleLogicalRange(range)
      }
    })
  }
}

// ============ 数据处理 ============
const handleResize = () => {
  if (mainChart && mainChartContainer.value) {
    mainChart.applyOptions({
      width: mainChartContainer.value.clientWidth,
      height: Math.max(400, mainChartContainer.value.clientHeight),
    })
  }
  if (subChart && subChartContainer.value) {
    subChart.applyOptions({
      width: subChartContainer.value.clientWidth,
      height: 260,
    })
  }
}

// 计算 MA
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

// 计算 EMA
const calculateEMA = (data, period, valueKey = 'close') => {
  const ema = []
  const k = 2 / (period + 1)

  // 第一个 EMA 使用简单平均
  if (data.length < period) return []

  let sum = 0
  for (let i = 0; i < period; i++) {
    sum += data[i][valueKey]
  }
  ema.push({
    time: data[period - 1].time,
    value: sum / period,
  })

  // 后续使用 EMA 公式
  for (let i = period; i < data.length; i++) {
    const prevEma = ema[ema.length - 1].value
    const currValue = data[i][valueKey]
    // 处理 NaN
    if (isNaN(prevEma) || isNaN(currValue)) continue
    const currEma = currValue * k + prevEma * (1 - k)
    ema.push({
      time: data[i].time,
      value: currEma,
    })
  }

  return ema
}

// 计算 MACD
const calculateMACD = (data) => {
  const ema12 = calculateEMA(data, 12, 'close')
  const ema26 = calculateEMA(data, 26, 'close')

  // DIFF = EMA12 - EMA26
  const diff = []
  const signalPeriod = 9

  // 合并 EMA12 和 EMA26 数据
  const ema12Map = new Map(ema12.map(item => [item.time, item.value]))
  const ema26Map = new Map(ema26.map(item => [item.time, item.value]))

  data.forEach(item => {
    if (ema12Map.has(item.time) && ema26Map.has(item.time)) {
      diff.push({
        time: item.time,
        value: ema12Map.get(item.time) - ema26Map.get(item.time),
      })
    }
  })

  // Signal = DIFF 的 9 日 EMA (注意：DIFF 数据字段是 value)
  const signal = calculateEMA(diff, signalPeriod, 'value')

  // Histogram = DIFF - Signal
  const histogram = []
  const signalMap = new Map(signal.map(item => [item.time, item.value]))

  diff.forEach(item => {
    if (signalMap.has(item.time)) {
      const histValue = item.value - signalMap.get(item.time)
      histogram.push({
        time: item.time,
        value: histValue,
        color: histValue >= 0 ? '#ef5350' : '#26a69a',
      })
    }
  })

  return { diff, signal, histogram }
}

// 转换周期数据（周 K、月 K）
const convertKlineData = (data, type) => {
  if (type === 'day') return data

  const grouped = []
  let currentGroup = null
  let currentKey = ''

  data.forEach(item => {
    const date = new Date(item.time)
    let key = ''

    if (type === 'week') {
      // 按周分组（以周一为基准）
      const year = date.getFullYear()
      const week = getWeekNumber(date)
      key = `${year}-W${week}`
    } else if (type === 'month') {
      // 按月分组
      const year = date.getFullYear()
      const month = date.getMonth() + 1
      key = `${year}-${month.toString().padStart(2, '0')}`
    }

    if (key !== currentKey) {
      if (currentGroup) {
        grouped.push(currentGroup)
      }
      currentGroup = {
        time: item.time,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volume,
      }
      currentKey = key
    } else {
      currentGroup.high = Math.max(currentGroup.high, item.high)
      currentGroup.low = Math.min(currentGroup.low, item.low)
      currentGroup.close = item.close
      currentGroup.volume += item.volume
    }
  })

  if (currentGroup) {
    grouped.push(currentGroup)
  }

  return grouped
}

// 获取周数
const getWeekNumber = (date) => {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
  const dayNum = d.getUTCDay() || 7
  d.setUTCDate(d.getUTCDate() + 4 - dayNum)
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
  return Math.ceil((((d - yearStart) / 86400000) + 1) / 7)
}

// ============ 数据加载 ============
const loadStockList = async () => {
  try {
    const res = await sim.getList()
    if (res.data.success) {
      stockList.value = res.data.data.map(s => ({
        code: s.stock_code,
        name: s.stock_name,
        current_price: parseFloat(s.current_price) || 0
      }))
      if (stockList.value.length > 0) {
        selectedStockCode.value = stockList.value[0].code
        currentStock.value = stockList.value[0]
        currentPrice.value = stockList.value[0].current_price
        loadData()
      }
    }
  } catch (error) {
    console.error('加载股票列表失败:', error)
  }
}

const onStockChange = (code) => {
  currentStock.value = stockList.value.find(s => s.code === code)
  currentPrice.value = currentStock.value?.current_price || 0
  loadData()
}

const onKlineTypeChange = () => {
  loadData()
}

const loadData = async () => {
  if (!selectedStockCode.value) return

  loading.value = true
  try {
    const range = dateRange.value || defaultDateRange.value
    const [start, end] = range

    // 获取基础日 K 数据
    const res = await dailyK.getData(selectedStockCode.value, start, end)

    // 获取交易记录
    const tradesRes = await sim.getTrades({
      stock_code: selectedStockCode.value,
      start_date: start,
      end_date: end
    })
    if (tradesRes.data.success) {
      tradeRecords.value = tradesRes.data.data || []
      console.log('交易记录原始数据:', tradesRes.data.data)
    }

    if (res.data.success) {
      const rawData = res.data.data

      // 转换为图表格式
      const candleData = rawData.map(item => ({
        time: item.date,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volume || 0,
      }))

      // 根据 K 线类型转换数据
      const convertedData = convertKlineData(candleData, klineType.value)

      // 计算均线
      const ma5Data = calculateMA(convertedData, 5)
      const ma10Data = calculateMA(convertedData, 10)
      const ma20Data = calculateMA(convertedData, 20)

      // 计算 MACD
      const macdData = calculateMACD(convertedData)

      // 更新图表
      candlestickSeries.setData(convertedData)
      ma5Series.setData(ma5Data)
      ma10Series.setData(ma10Data)
      ma20Series.setData(ma20Data)

      macdSeries.setData(macdData.diff)
      macdSignalSeries.setData(macdData.signal)
      macdHistogramSeries.setData(macdData.histogram)

      // 保存数据用于十字光标显示
      candleDataMap = new Map(convertedData.map(d => [d.time, d]))
      ma5DataMap = new Map(ma5Data.map(m => [m.time, m.value]))
      ma10DataMap = new Map(ma10Data.map(m => [m.time, m.value]))
      ma20DataMap = new Map(ma20Data.map(m => [m.time, m.value]))
      macdDataMap = new Map()
      macdData.diff.forEach(d => macdDataMap.set(d.time, d))
      macdData.signal.forEach(d => {
        const existing = macdDataMap.get(d.time)
        if (existing) {
          macdDataMap.set(d.time, { ...existing, signal: d.value })
        }
      })
      macdData.histogram.forEach(d => {
        const existing = macdDataMap.get(d.time)
        if (existing) {
          macdDataMap.set(d.time, { ...existing, histogram: d.value })
        }
      })

      // 保存交易记录用于悬浮框显示
      tradeDataMap = new Map()
      tradeRecords.value.forEach(trade => {
        const tradeDate = trade.trade_date?.split(' ')[0] || trade.trade_date
        // 同一天可能有多笔交易，用数组存储
        if (!tradeDataMap.has(tradeDate)) {
          tradeDataMap.set(tradeDate, [])
        }
        tradeDataMap.get(tradeDate).push({
          direction: trade.direction,
          price: parseFloat(trade.price) || 0,
          volume: trade.quantity || trade.volume || 0, // 后端返回 quantity，映射为 volume
          remark: trade.remark,
        })
      })

      console.log('交易记录:', {
        tradeRecordsCount: tradeRecords.value.length,
        tradeDataMapSize: tradeDataMap.size,
        sampleTrade: tradeDataMap.values().next()?.value,
      })

      console.log('数据已存储到 Maps:', {
        candleDataMapSize: candleDataMap.size,
        ma5DataMapSize: ma5DataMap.size,
        macdDataMapSize: macdDataMap.size,
        tradeDataMapSize: tradeDataMap.size,
        sampleTime: convertedData[0]?.time,
        sampleCandle: candleDataMap.get(convertedData[0]?.time)
      })

      // 成交量不单独显示

      // 添加交易标记
      updateMarkers(convertedData)

      // 更新当前数据
      if (convertedData.length > 0) {
        const lastData = convertedData[convertedData.length - 1]
        currentData.value = lastData

        const lastMA5 = ma5Data[ma5Data.length - 1]
        const lastMA10 = ma10Data[ma10Data.length - 1]
        const lastMA20 = ma20Data[ma20Data.length - 1]

        currentMA5.value = lastMA5?.value || null
        currentMA10.value = lastMA10?.value || null
        currentMA20.value = lastMA20?.value || null
      }

      // 同步副图时间轴
      const visibleRange = mainChart.timeScale().getVisibleLogicalRange()
      if (visibleRange && subChart) {
        subChart.timeScale().setVisibleLogicalRange(visibleRange)
      }

      // 添加十字光标移动事件监听
      mainChart.subscribeCrosshairMove((param) => {
        if (!param.point || param.time === undefined) return

        const time = param.time

        // lightweight-charts v4.x BusinessDay 格式：{ year, month, day }
        // 我们需要转换为 'YYYY-MM-DD' 字符串
        let timeStr = ''
        if (typeof time === 'object' && time !== null && 'year' in time) {
          const month = String(time.month).padStart(2, '0')
          const day = String(time.day).padStart(2, '0')
          timeStr = `${time.year}-${month}-${day}`
        } else {
          timeStr = String(time)
        }

        if (candleDataMap.has(timeStr)) {
          const data = candleDataMap.get(timeStr)
          // 更新底部图例
          currentData.value = {
            time: data.time,
            open: data.open,
            high: data.high,
            low: data.low,
            close: data.close,
            volume: data.volume
          }
          currentMA5.value = ma5DataMap.get(timeStr) || null
          currentMA10.value = ma10DataMap.get(timeStr) || null
          currentMA20.value = ma20DataMap.get(timeStr) || null

          const macd = macdDataMap.get(timeStr)
          currentDIF.value = macd?.value || null
          currentDEA.value = macd?.signal || null
          currentMACD.value = macd?.histogram || null

          // 更新悬浮框数据
          const trades = tradeDataMap.get(timeStr) || []
          hoverData.value = {
            time: data.time,
            open: data.open,
            high: data.high,
            low: data.low,
            close: data.close,
            volume: data.volume,
            dif: macd?.value || null,
            dea: macd?.signal || null,
            macd: macd?.histogram || null,
            trades: trades, // 显示所有交易
          }
        } else {
          // 移出图表时隐藏悬浮框
          hoverData.value.time = ''
        }
      })
    }
  } catch (error) {
    console.error('加载数据失败:', error)
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

    const isTTrade = trade.remark?.includes('T') || trade.remark?.includes('做 T')

    if (trade.direction === 'BUY') {
      if (isTTrade) {
        // 做 T 买入：橙色小三角
        markers.push({
          time: tradeDate,
          position: 'belowBar',
          color: '#ff9800',
          shape: 'arrowUp',
          text: 'T',
          size: 0.8,
        })
      } else {
        // 底仓买入：红色圆形 B
        markers.push({
          time: tradeDate,
          position: 'belowBar',
          color: '#ef5350',
          shape: 'circle',
          text: 'B',
          size: 1,
        })
      }
    } else if (trade.direction === 'SELL') {
      if (isTTrade) {
        // 做 T 卖出：绿色小三角
        markers.push({
          time: tradeDate,
          position: 'aboveBar',
          color: '#26a69a',
          shape: 'arrowDown',
          text: 'T',
          size: 0.8,
        })
      } else {
        // 底仓卖出：蓝色圆形 S
        markers.push({
          time: tradeDate,
          position: 'aboveBar',
          color: '#2196f3',
          shape: 'circle',
          text: 'S',
          size: 1,
        })
      }
    }
  })

  // 按时间升序排序（lightweight-charts 要求）
  markers.sort((a, b) => {
    if (a.time < b.time) return -1
    if (a.time > b.time) return 1
    return 0
  })

  if (candlestickSeries) {
    candlestickSeries.setMarkers(markers)
  }
}

// 格式化成交量
const formatVolume = (volume) => {
  if (!volume) return '-'
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  }
  if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  }
  return volume.toString()
}

// 获取价格样式类
const getPriceClass = (price, close) => {
  if (price === null || price === undefined) return ''
  if (price > close) return 'price-up'
  if (price < close) return 'price-down'
  return 'price-equal'
}

// ============ 生命周期 ============
onMounted(() => {
  // 初始化日期范围为默认值（近 1 年）
  dateRange.value = defaultDateRange.value

  initCharts()
  loadStockList()
})

onUnmounted(() => {
  if (mainChart) {
    mainChart.remove()
  }
  if (subChart) {
    subChart.remove()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.kline-chart {
  padding: 0;
  height: 100%;
}

.chart-card {
  height: 100%;
  border-radius: 8px;
}

.chart-card :deep(.el-card__body) {
  padding: 16px;
  height: calc(100% - 60px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #e8eaed;
}

.stock-tag {
  font-size: 13px;
}

.price-tag {
  font-size: 13px;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
  align-items: center;
}

.chart-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-radius: 8px;
  overflow: hidden;
  background: #1a1a2e;
  position: relative;
}

/* 悬浮数据框 */
.floating-tooltip {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(26, 26, 46, 0.95);
  border: 1px solid rgba(74, 78, 87, 0.8);
  border-radius: 6px;
  padding: 10px 12px;
  z-index: 100;
  font-size: 12px;
  font-family: 'Roboto Mono', monospace;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  pointer-events: none;
  min-width: 140px;
}

.tooltip-date {
  color: #e8eaed;
  font-weight: 600;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(74, 78, 87, 0.5);
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 4px;
}

.tooltip-label {
  color: #888;
}

.tooltip-value {
  color: #d1d4dc;
  font-weight: 500;
}

.tooltip-value.dif {
  color: #2962FF;
}

.tooltip-value.dea {
  color: #ff6d00;
}

.tooltip-divider {
  height: 1px;
  background: rgba(74, 78, 87, 0.5);
  margin: 6px 0;
}

.tooltip-trade {
  padding: 8px;
  border-radius: 4px;
  margin: 6px 0;
}

.tooltip-trade.trade-buy {
  background: rgba(239, 83, 80, 0.15);
  border: 1px solid rgba(239, 83, 80, 0.3);
}

.tooltip-trade.trade-sell {
  background: rgba(38, 166, 154, 0.15);
  border: 1px solid rgba(38, 166, 154, 0.3);
}

.tooltip-trade-label {
  font-weight: 600;
  font-size: 13px;
  margin-bottom: 6px;
}

.trade-buy .tooltip-trade-label {
  color: #ef5350;
}

.trade-sell .tooltip-trade-label {
  color: #26a69a;
}

.tooltip-trade-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 3px;
  font-size: 11px;
}

.main-chart {
  width: 100%;
  min-height: 400px;
  flex: 1;
}

.sub-chart {
  width: 100%;
  height: 260px;
  flex-shrink: 0;
}

.legend {
  display: flex;
  gap: 20px;
  padding: 12px 16px;
  background: #1a1a2e;
  border-radius: 4px;
  margin-top: 12px;
  flex-wrap: wrap;
  font-size: 12px;
  font-family: 'Roboto Mono', monospace;
}

.legend-item {
  color: #d1d4dc;
}

.legend-item .price-up {
  color: #ef5350;
}

.legend-item .price-down {
  color: #26a69a;
}

.legend-item .price-equal {
  color: #b2b5be;
}

.legend-item.ma5 {
  color: #ff9800;
}

.legend-item.ma10 {
  color: #00bcd4;
}

.legend-item.ma20 {
  color: #9c27b0;
}

.legend-item.macd-dif {
  color: #2962FF;
}

.legend-item.macd-dea {
  color: #ff6d00;
}

.legend-item.macd-hist {
  color: #d1d4dc;
}

/* 深色主题覆盖 */
:deep(.el-card) {
  background: #16162a;
  border-color: #2a2e39;
}

:deep(.el-card__header) {
  background: #1a1a2e;
  border-color: #2a2e39;
  padding: 12px 16px;
}

:deep(.el-select .el-input__wrapper) {
  background-color: #2a2e39;
  box-shadow: none;
}

:deep(.el-select .el-input__inner) {
  color: #e8eaed;
}

:deep(.el-date-picker) {
  --el-datepicker-bg-color: #2a2e39;
  --el-datepicker-text-color: #e8eaed;
}

:deep(.el-button) {
  --el-button-bg-color: #2962FF;
  --el-button-border-color: #2962FF;
}

:deep(.el-radio-group .el-radio-button__inner) {
  background: #2a2e39;
  color: #d1d4dc;
  border-color: #3a3e49;
}

:deep(.el-radio-group .el-radio-button__orig-radio:checked) + .el-radio-button__inner {
  background: #2962FF;
  color: #fff;
  border-color: #2962FF;
}

/* Loading 遮罩深色样式 */
:deep(.el-loading-mask) {
  background-color: rgba(26, 26, 46, 0.8);
}

:deep(.el-loading-spinner .path) {
  stroke: #2962FF;
}
</style>
