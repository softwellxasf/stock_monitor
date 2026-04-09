<template>
  <div class="theme-switcher">
    <el-popover placement="bottom" :width="260" trigger="click">
      <template #reference>
        <div class="theme-btn">
          <el-icon><Brush /></el-icon>
        </div>
      </template>
      
      <div class="theme-panel">
        <h4>选择主题</h4>
        <div class="theme-options">
          <div 
            v-for="(theme, key) in themes" 
            :key="key"
            class="theme-option"
            :class="{ active: currentTheme === key }"
            @click="setTheme(key)"
          >
            <div class="theme-preview" :style="{
              background: `linear-gradient(135deg, ${theme.primary} 0%, ${theme.accent} 100%)`
            }"></div>
            <span class="theme-name">{{ theme.name }}</span>
            <el-icon v-if="currentTheme === key" class="check-icon"><Check /></el-icon>
          </div>
        </div>
      </div>
    </el-popover>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useThemeStore } from '../store/theme'

const themeStore = useThemeStore()
const currentTheme = computed(() => themeStore.currentTheme)
const themes = computed(() => ({
  mint: { name: '薄荷流光', primary: '#00B75E', accent: '#6531FF' },
  citrus: { name: '柚光晴空', primary: '#F45805', accent: '#0344A1' }
}))

const setTheme = (key) => {
  themeStore.setTheme(key)
}
</script>

<style scoped>
.theme-switcher { margin-right: 15px; }

.theme-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
  color: #606266;
}

.theme-btn:hover { background: #f5f7fa; }

.theme-panel h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 14px;
}

.theme-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.theme-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.theme-option:hover { background: #f5f7fa; }

.theme-option.active {
  border-color: var(--theme-primary);
  background: #f5f7fa;
}

.theme-preview {
  width: 50px;
  height: 36px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.theme-name { flex: 1; font-size: 14px; color: #333; }

.check-icon { color: var(--theme-primary); font-size: 18px; }
</style>
