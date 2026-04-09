<template>
  <div class="theme-switcher">
    <el-popover placement="bottom" :width="280" trigger="click">
      <template #reference>
        <div class="theme-btn" :title="'主题：' + currentThemeName">
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
              background: `linear-gradient(135deg, ${theme.primary} 0%, ${theme.link} 100%)`
            }"></div>
            <div class="theme-info">
              <span class="theme-name">{{ theme.name }}</span>
              <span class="theme-desc">{{ theme.name === '深蓝商务' ? '专业沉稳' : '柔和静谧' }}</span>
            </div>
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
const currentThemeName = computed(() => themes.value[currentTheme.value]?.name || '')
const themes = computed(() => ({
  navy: { name: '深蓝商务', primary: '#2B5B9E', link: '#3676D1', desc: '专业沉稳' },
  cyan: { name: '灰青静谧', primary: '#3D8C8A', link: '#4A9C9A', desc: '柔和静谧' }
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
  font-weight: 500;
}

.theme-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.theme-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
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
  height: 40px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  flex-shrink: 0;
}

.theme-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.theme-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.theme-desc {
  font-size: 12px;
  color: #999;
}

.check-icon {
  color: var(--theme-primary);
  font-size: 18px;
  flex-shrink: 0;
}
</style>
