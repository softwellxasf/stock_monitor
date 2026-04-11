<template>
  <div class="sim-daily-k">
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
          v-model="searchForm.dateRange"
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

      <!-- K 线图表 -->
      <div ref="kChartRef" class="k-chart" v-loading="loading"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { sim, dailyK } from '../api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const loading = ref(false)
const stockList = ref([])
const kChartRef = ref(null)
const currentStock = ref(null)
const currentPrice = ref(0)
let kChartInstance = null

const defaultDateRange = computed(() => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)  // 默认最近 30 天
  return [start.toISOString().split('T')[0], end.toISOString().split('T')[0]]
})

const searchForm = ref({
  stockCode: '',
  dateRange: []
})
const tradeRecords = ref([])  // 交易记录

// 加载股票列表
const loadStockList = async () => {
  try {
    const res = await sim.getList()
    if (res.data.success) {
      stockList.value = res.data.data.map(s => ({
        code: s.stock_code,
        name: s.stock_name,
        current_price: parseFloat(s.current_price) || 0
      })
  
  console.log('=== 交易标记数据 ===')
  console.log('底仓买入标记数据:', buyMarks)
  console.log('底仓卖出标记数据:', sellMarks)
  console.log('做 T 买入标记数据:', tBuyMarks)
  console.log('做 T 卖出标记数据:', tSellMarks))
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

// 加载日 K 数据（使用真实数据）
const loadDailyKData = async () => {
  if (!searchForm.value.stockCode) return
  
  loading.value = true
  try {
    const dateRange = searchForm.value.dateRange || defaultDateRange.value
    const start = dateRange[0]
    const end = dateRange[1]
    console.log('默认日期范围:', defaultDateRange.value)
    console.log('查询日期范围:', start, end)
    console.log('股票代码:', searchForm.value.stockCode)
    
    // 获取真实日 K 数据
    const res = await dailyK.getData(searchForm.value.stockCode, start, end)
    
    // 获取交易记录
    const tradesRes = await sim.getTrades({
      stock_code: searchForm.value.stockCode,
      start_date: start,
      end_date: end
    })
  
  console.log('=== 交易标记数据 ===')
  console.log('底仓买入标记数据:', buyMarks)
  console.log('底仓卖出标记数据:', sellMarks)
  console.log('做 T 买入标记数据:', tBuyMarks)
  console.log('做 T 卖出标记数据:', tSellMarks)
    if (tradesRes.data.success) {
      tradeRecords.value = tradesRes.data.data || []
      console.log('交易记录:', tradeRecords.value.length, '条')
    }
    
    if (res.data.success) {
      const kData = res.data.data
      
      if (kData.length === 0) {
        ElMessage.warning('暂无该股票日 K 数据')
        loading.value = false
        return
      }
      
      // 准备图表数据
      const dates = kData.map(item => item.date)
      const ohlcData = kData.map(item => [
        item.open,    // 开盘价
        item.close,   // 收盘价
        item.low,     // 最低价
        item.high     // 最高价
      ])
      const volumes = kData.map(item => item.volume)
      const ma5Data = kData.map(item => item.ma5)
      const ma10Data = kData.map(item => item.ma10)
      const ma20Data = kData.map(item => item.ma20)
      
      renderKChart(dates, ohlcData, volumes, { ma5Data, ma10Data, ma20Data })
    }
  } catch (error) {
    console.error('加载日 K 数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 渲染专业 K 线图表（带交易标记）
const renderKChart = (dates, ohlcData, volumes, indicators) => {
  // 准备交易标记数据
  const buyMarks = []  // 底仓买入（黄色向上箭头）
  const sellMarks = []  // 底仓卖出（红色向下箭头）
  const tBuyMarks = []  // 做 T 买入（蓝色加号）
  const tSellMarks = []  // 做 T 卖出（紫色减号）
  
  tradeRecords.value.forEach(trade => {
    const tradeDate = trade.trade_date?.split(' ')[0] || trade.trade_date
    const dataIndex = dates.indexOf(tradeDate)
    if (dataIndex === -1) return
    
    const isTTrade = trade.remark?.includes('T') || trade.remark?.includes('做 T')
    const high = ohlcData[dataIndex][2]
    const low = ohlcData[dataIndex][3]
    
    if (trade.direction === 'BUY') {
      if (isTTrade) {
        // 做 T 买入：橙色小圆点 + T 字
        tBuyMarks.push({
          xAxis: dataIndex,
          yAxis: low * 0.96,
          value: 'T',
          itemStyle: { color: '#FF9900' }  // 橙色
        })
  
  console.log('=== 交易标记数据 ===')
  console.log('底仓买入标记数据:', buyMarks)
  console.log('底仓卖出标记数据:', sellMarks)
  console.log('做 T 买入标记数据:', tBuyMarks)
  console.log('做 T 卖出标记数据:', tSellMarks)
      } else {
        // 底仓买入：红色圆形背景 + 白色 B 字
        buyMarks.push({
          xAxis: dataIndex,
          yAxis: low * 0.94,
          value: 'B',
          itemStyle: { 
            color: '#FF4444',  // 红色背景
            textBorderColor: '#FFFFFF',  // 白色边框
            textBorderWidth: 1
          }
        })
  
  console.log('=== 交易标记数据 ===')
  console.log('底仓买入标记数据:', buyMarks)
  console.log('底仓卖出标记数据:', sellMarks)
  console.log('做 T 买入标记数据:', tBuyMarks)
  console.log('做 T 卖出标记数据:', tSellMarks)
      }
    } else if (trade.direction === 'SELL') {
      if (isTTrade) {
        // 做 T 卖出：绿色小圆点 + T 字
        tSellMarks.push({
          xAxis: dataIndex,
          yAxis: high * 1.04,
          value: 'T',
          itemStyle: { color: '#00CC00' }  // 绿色
        })
  
  console.log('=== 交易标记数据 ===')
  console.log('底仓买入标记数据:', buyMarks)
  console.log('底仓卖出标记数据:', sellMarks)
  console.log('做 T 买入标记数据:', tBuyMarks)
  console.log('做 T 卖出标记数据:', tSellMarks)
      } else {
        // 底仓卖出：蓝色圆形背景 + 白色 S 字
        sellMarks.push({
          xAxis: dataIndex,
          yAxis: high * 1.06,
          value: 'S',
          itemStyle: { 
            color: '#4488FF',  // 蓝色背景
            textBorderColor: '#FFFFFF',  // 白色边框
            textBorderWidth: 1
          }
        })
  
  console.log('=== 交易标记数据 ===')
  console.log('底仓买入标记数据:', buyMarks)
  console.log('底仓卖出标记数据:', sellMarks)
  console.log('做 T 买入标记数据:', tBuyMarks)
  console.log('做 T 卖出标记数据:', tSellMarks)
      }
    }
  })
  
  console.log('=== 交易标记数据 ===')
  console.log('底仓买入标记数据:', buyMarks)
  console.log('底仓卖出标记数据:', sellMarks)
  console.log('做 T 买入标记数据:', tBuyMarks)
  console.log('做 T 卖出标记数据:', tSellMarks)
  if (!kChartRef.value) return
  
  if (kChartInstance) {
    kChartInstance.dispose()
  }
  
  kChartInstance = echarts.init(kChartRef.value, 'light', {
    renderer: 'canvas',
    devicePixelRatio: window.devicePixelRatio || 1
  })
  
  console.log('=== 交易标记数据 ===')
  console.log('底仓买入标记数据:', buyMarks)
  console.log('底仓卖出标记数据:', sellMarks)
  console.log('做 T 买入标记数据:', tBuyMarks)
  console.log('做 T 卖出标记数据:', tSellMarks)
  
  // 专业金融配色
  const colorUp = '#FF0000'      // 红色（涨）
  const colorDown = '#00CC00'    // 绿色（跌）
  const colorMa5 = '#FFFFFF'     // 金黄色
  const colorMa10 = '#FFD700'    // 青色
  const colorMa20 = '#00FFFF'    // 粉色
  
  const option = {
    backgroundColor: '#ffffff',
    animation: false,
    title: {
      text: `${searchForm.value.stockCode} 日 K 线图`,
      left: 'center',
      textStyle: {
        fontSize: 14,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      borderWidth: 3,
      borderColor: '#ccc',
      padding: 10,
      textStyle: {
        fontSize: 12
      },
      formatter: (params) => {
        const dataIndex = params[0].dataIndex
        const data = ohlcData[dataIndex]
        const date = dates[dataIndex]
        const open = data[0].toFixed(2)
        const high = data[2].toFixed(2)
        const low = data[1].toFixed(2)
        const close = data[3].toFixed(2)
        const volume = volumes[dataIndex].toLocaleString()
        
        return `
          <div style="font-weight:bold;margin-bottom:5px;">${date}</div>
          <div>开盘：${open}</div>
          <div>最高：${high}</div>
          <div>最低：${low}</div>
          <div>收盘：${close}</div>
          <div>成交量：${volume}</div>
        `
      }
    },
    legend: {
      data: ['K 线', 'MA5', 'MA10', 'MA20', '成交量', '底仓买入', '底仓卖出', '做 T 买入', '做 T 卖出'],
      top: 30,
      textStyle: {
        fontSize: 10
      }
    },
    grid: [
      {
        left: '8%',
        right: '8%',
        height: '55%',
        top: '12%'
      },
      {
        left: '8%',
        right: '8%',
        top: '70%',
        height: '12%'
      }
    ],
    axisPointer: {
      link: [
        { xAxisIndex: [0, 1] }
      ]
    },
    xAxis: [
      {
        type: 'category',
        data: dates,
        scale: true,
        boundaryGap: false,
        axisLine: {
          lineStyle: {
            color: '#ccc'
          }
        },
        axisLabel: {
          fontSize: 10,
          rotate: 0,
          interval: Math.floor(dates.length / 10)
        },
        splitLine: {
          show: false
        },
        min: 'dataMin',
        max: 'dataMax'
      },
      {
        type: 'category',
        gridIndex: 1,
        data: dates,
        axisLabel: {
          show: false
        },
        axisLine: {
          lineStyle: {
            color: '#ccc'
          }
        },
        splitLine: {
          show: false
        }
      }
    ],
    yAxis: [
      {
        scale: true,
        name: '股价',
        nameLocation: 'middle',
        nameGap: 50,
        position: 'right',
        axisLine: {
          lineStyle: {
            color: '#ccc'
          }
        },
        axisLabel: {
          fontSize: 10,
          formatter: (value) => value.toFixed(2)
        },
        splitLine: {
          lineStyle: {
            color: '#f0f0f0',
            type: 'dashed'
          }
        }
      },
      {
        scale: true,
        gridIndex: 1,
        name: '成交量',
        nameLocation: 'middle',
        nameGap: 40,
        position: 'right',
        axisLine: {
          lineStyle: {
            color: '#ccc'
          }
        },
        axisLabel: {
          fontSize: 10,
          formatter: (value) => {
            if (value >= 1000000) {
              return (value / 1000000).toFixed(1) + 'M'
            } else if (value >= 1000) {
              return (value / 1000).toFixed(0) + 'K'
            }
            return value.toString()
          }
        },
        splitLine: {
          show: false
        }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 50,
        end: 100,
        minValueSpan: 10
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        top: '95%',
        height: 20,
        start: 50,
        end: 100,
        borderColor: '#ddd',
        fillerColor: 'rgba(0,0,0,0.1)',
        handleStyle: {
          color: '#999'
        }
      }
    ],
    series: [
      {
        name: 'K 线',
        type: 'candlestick',
        data: ohlcData,
        itemStyle: {
          color: colorUp,
          color0: colorDown,
          borderColor: colorUp,
          borderColor0: colorDown,
          borderWidth: 2
        },
        barMaxWidth: 20,
        barMinWidth: 8,
        zlevel: 1
      },
      {
        name: 'MA5',
        type: 'line',
        data: indicators.ma5Data,
        smooth: true,
        lineStyle: {
          width: 1.5,  // 加粗
          color: colorMa5,
          type: 'solid',
          shadowColor: 'rgba(0,0,0,0.3)',  // 阴影
          shadowBlur: 2
        },
        symbol: 'none',
        zlevel: 2
      },
      {
        name: 'MA10',
        type: 'line',
        data: indicators.ma10Data,
        smooth: true,
        lineStyle: {
          width: 1.5,  // 加粗
          color: colorMa10,
          type: 'solid',
          shadowColor: 'rgba(0,0,0,0.3)',
          shadowBlur: 2
        },
        symbol: 'none',
        zlevel: 2
      },
      {
        name: 'MA20',
        type: 'line',
        data: indicators.ma20Data,
        smooth: true,
        lineStyle: {
          width: 1.5,  // 加粗
          color: colorMa20,
          type: 'solid',
          shadowColor: 'rgba(0,0,0,0.3)',
          shadowBlur: 2
        },
        symbol: 'none',
        zlevel: 2
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes.map((vol, idx) => {
          const open = ohlcData[idx][0]
          const close = ohlcData[idx][3]
          return {
            value: vol,
            itemStyle: {
              color: close >= open ? colorUp : colorDown,
              opacity: 0.8
            }
          }
        })
  
  console.log('=== 交易标记数据 ===')
  console.log('底仓买入标记数据:', buyMarks)
  console.log('底仓卖出标记数据:', sellMarks)
  console.log('做 T 买入标记数据:', tBuyMarks)
  console.log('做 T 卖出标记数据:', tSellMarks),
        barMaxWidth: 25,
        zlevel: 1
      },
      {
        name: '底仓买入',
        type: 'custom',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: buyMarks,
        renderItem: (params, api) => {
          const point = api.coord([api.value(0), api.value(1)])
          return {
            type: 'circle',
            shape: { r: 10 },
            position: [point[0], point[1]],
            style: {
              fill: '#FF4444'
            }
          }
        },
        zlevel: 3
      },
      {
        name: '底仓买入文字',
        type: 'custom',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: buyMarks,
        renderItem: (params, api) => {
          const point = api.coord([api.value(0), api.value(1)])
          return {
            type: 'text',
            style: {
              text: 'B',
              fill: '#FFFFFF',
              fontSize: 12,
              fontWeight: 'bold'
            },
            position: [point[0], point[1] - 4]
          }
        },
        zlevel: 4
      },
      {
        name: '底仓卖出',
        type: 'custom',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: sellMarks,
        renderItem: (params, api) => {
          const point = api.coord([api.value(0), api.value(1)])
          return {
            type: 'circle',
            shape: { r: 10 },
            position: [point[0], point[1]],
            style: {
              fill: '#4488FF'
            }
          }
        },
        zlevel: 3
      },
      {
        name: '底仓卖出文字',
        type: 'custom',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: sellMarks,
        renderItem: (params, api) => {
          const point = api.coord([api.value(0), api.value(1)])
          return {
            type: 'text',
            style: {
              text: 'S',
              fill: '#FFFFFF',
              fontSize: 12,
              fontWeight: 'bold'
            },
            position: [point[0], point[1] - 4]
          }
        },
        zlevel: 4
      },
      {
        name: '做 T 买入',
        type: 'custom',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: tBuyMarks,
        renderItem: (params, api) => {
          const point = api.coord([api.value(0), api.value(1)])
          return {
            type: 'circle',
            shape: { r: 6 },
            position: [point[0], point[1]],
            style: {
              fill: '#FF9900'
            }
          }
        },
        zlevel: 3
      },
      {
        name: '做 T 买入文字',
        type: 'custom',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: tBuyMarks,
        renderItem: (params, api) => {
          const point = api.coord([api.value(0), api.value(1)])
          return {
            type: 'text',
            style: {
              text: 'T',
              fill: '#FFFFFF',
              fontSize: 9,
              fontWeight: 'bold'
            },
            position: [point[0], point[1] - 3]
          }
        },
        zlevel: 4
      },
      {
        name: '做 T 卖出',
        type: 'custom',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: tSellMarks,
        renderItem: (params, api) => {
          const point = api.coord([api.value(0), api.value(1)])
          return {
            type: 'circle',
            shape: { r: 6 },
            position: [point[0], point[1]],
            style: {
              fill: '#00CC00'
            }
          }
        },
        zlevel: 3
      },
      {
        name: '做 T 卖出文字',
        type: 'custom',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: tSellMarks,
        renderItem: (params, api) => {
          const point = api.coord([api.value(0), api.value(1)])
          return {
            type: 'text',
            style: {
              text: 'T',
              fill: '#FFFFFF',
              fontSize: 9,
              fontWeight: 'bold'
            },
            position: [point[0], point[1] - 3]
          }
        },
        zlevel: 4
      }
    ]
  }
  
  console.log('=== K 线图配置 ===')
  console.log('MA5 颜色:', colorMa5)
  console.log('MA10 颜色:', colorMa10)
  console.log('MA20 颜色:', colorMa20)
  console.log('底仓买入标记:', buyMarks.length)
  console.log('底仓卖出标记:', sellMarks.length)
  console.log('做 T 买入标记:', tBuyMarks.length)
  console.log('做 T 卖出标记:', tSellMarks.length)
  
  kChartInstance.setOption(option)
}

// 窗口大小变化时重新渲染图表
window.addEventListener('resize', () => {
  if (kChartInstance) {
    kChartInstance.resize()
  }
})

onMounted(() => {
  loadStockList()
  // 设置默认日期范围（最近 6 个月/180 天）
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 180)
  searchForm.value.dateRange = [
    start.toISOString().split('T')[0],
    end.toISOString().split('T')[0]
  ]
})
</script>

<style scoped>
.sim-daily-k {
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

.k-chart {
  width: 100%;
  height: 650px;
}
</style>
