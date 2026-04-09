import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 主题配置 - 专业商务风格（侧边栏调浅）
const themes = {
  navy: {
    name: '深蓝商务',
    primary: '#2B5B9E',
    title: '#1F3A61',
    text: '#333333',
    textSecondary: '#666666',
    border: '#E5E6EB',
    bg: '#F7F8FA',
    success: '#27AE60',
    warning: '#F59E0B',
    danger: '#E53E3E',
    link: '#3676D1',
    sidebar: '#2d4a6b',        // 调浅：原 #1a3a5c
    sidebarHover: '#3d5a7b',   // 调浅：原 #234a6f
    sidebarActive: '#3d6bb3'   // 调浅：原 #2B5B9E
  },
  cyan: {
    name: '灰青静谧',
    primary: '#3D8C8A',
    title: '#2C3E50',
    text: '#444444',
    textSecondary: '#777777',
    border: '#E8E8ED',
    bg: '#F9FAFB',
    success: '#22C55E',
    warning: '#F97316',
    danger: '#EF4444',
    link: '#4A9C9A',
    sidebar: '#3d5c5a',        // 调浅：原 #2c5a58
    sidebarHover: '#4d6c6a',   // 调浅：原 #356b69
    sidebarActive: '#4d9c9a'   // 调浅：原 #3D8C8A
  }
}

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref(localStorage.getItem('theme') || 'navy')
  
  const themeData = computed(() => themes[currentTheme.value])
  
  function setTheme(themeName) {
    currentTheme.value = themeName
    localStorage.setItem('theme', themeName)
    applyTheme(themeName)
  }
  
  function applyTheme(themeName) {
    const theme = themes[themeName]
    const root = document.documentElement
    
    root.style.setProperty('--theme-primary', theme.primary)
    root.style.setProperty('--theme-title', theme.title)
    root.style.setProperty('--theme-text', theme.text)
    root.style.setProperty('--theme-text-secondary', theme.textSecondary)
    root.style.setProperty('--theme-border', theme.border)
    root.style.setProperty('--theme-bg', theme.bg)
    root.style.setProperty('--theme-success', theme.success)
    root.style.setProperty('--theme-warning', theme.warning)
    root.style.setProperty('--theme-danger', theme.danger)
    root.style.setProperty('--theme-link', theme.link)
    root.style.setProperty('--theme-sidebar', theme.sidebar)
    root.style.setProperty('--theme-sidebar-hover', theme.sidebarHover)
    root.style.setProperty('--theme-sidebar-active', theme.sidebarActive)
  }
  
  applyTheme(currentTheme.value)
  
  return { currentTheme, themeData, setTheme }
})
