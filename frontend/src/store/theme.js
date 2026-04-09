import { defineStore } from 'pinia'
import { ref } from 'vue'

// 主题配置
const themes = {
  mint: {
    name: '薄荷流光',
    primary: '#00B75E',
    secondary: '#F1F1F1',
    accent: '#6531FF',
    sidebar: '#0a2e1f',
    sidebarHover: '#0f3d29',
    sidebarActive: '#1a4d36'
  },
  citrus: {
    name: '柚光晴空',
    primary: '#F45805',
    secondary: '#F5F5F5',
    accent: '#0344A1',
    sidebar: '#3d1a05',
    sidebarHover: '#4d2107',
    sidebarActive: '#5c2809'
  },
  flame: {
    name: '炽烈火焰',
    primary: '#FF4539',
    secondary: '#FEFEFE',
    accent: '#FFCE3B',
    sidebar: '#3d120f',
    sidebarHover: '#4d1713',
    sidebarActive: '#5c1b16'
  }
}

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref(localStorage.getItem('theme') || 'mint')
  
  const themeData = computed(() => themes[currentTheme.value])
  
  function setTheme(themeName) {
    currentTheme.value = themeName
    localStorage.setItem('theme', themeName)
    applyTheme(themeName)
  }
  
  function applyTheme(themeName) {
    const theme = themes[themeName]
    const root = document.documentElement
    
    // 设置 CSS 变量
    root.style.setProperty('--theme-primary', theme.primary)
    root.style.setProperty('--theme-secondary', theme.secondary)
    root.style.setProperty('--theme-accent', theme.accent)
    root.style.setProperty('--theme-sidebar', theme.sidebar)
    root.style.setProperty('--theme-sidebar-hover', theme.sidebarHover)
    root.style.setProperty('--theme-sidebar-active', theme.sidebarActive)
  }
  
  // 初始化主题
  applyTheme(currentTheme.value)
  
  return {
    currentTheme,
    themeData,
    setTheme
  }
})
