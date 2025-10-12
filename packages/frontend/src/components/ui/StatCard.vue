<template>
  <div 
    class="stat-card" 
    :class="[
      `variant-${variant}`,
      `size-${size}`,
      { 'animated': animated }
    ]"
  >
    <!-- 背景装饰 -->
    <div class="card-background">
      <div class="bg-pattern"></div>
      <div class="bg-gradient"></div>
    </div>

    <!-- 卡片内容 -->
    <div class="card-content">
      <!-- 图标区域 -->
      <div class="icon-section">
        <div class="icon-container">
          <el-icon><component :is="icon" /></el-icon>
        </div>
        <div v-if="trend" class="trend-indicator" :class="trendClass">
          <el-icon><component :is="trendIcon" /></el-icon>
          <span>{{ trend }}</span>
        </div>
      </div>

      <!-- 数据区域 -->
      <div class="data-section">
        <div class="value-container">
          <span class="value" :class="{ 'counting': animated }">
            {{ displayValue }}
          </span>
          <span v-if="unit" class="unit">{{ unit }}</span>
        </div>
        <div class="label">{{ label }}</div>
        <div v-if="description" class="description">{{ description }}</div>
      </div>

      <!-- 进度条（可选） -->
      <div v-if="progress !== undefined" class="progress-section">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${progress}%` }"
          ></div>
        </div>
        <span class="progress-text">{{ progress }}%</span>
      </div>
    </div>

    <!-- 悬浮效果 -->
    <div class="hover-effect"></div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch, type Component } from 'vue'
import { ArrowUp, ArrowDown, Minus } from '@element-plus/icons-vue'

interface Props {
  icon: Component
  label: string
  value: number | string
  unit?: string
  description?: string
  variant?: 'primary' | 'success' | 'warning' | 'error' | 'info' | 'purple'
  size?: 'sm' | 'md' | 'lg'
  trend?: string
  trendType?: 'up' | 'down' | 'neutral'
  progress?: number
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  trendType: 'neutral',
  animated: true
})

const displayValue = ref<number | string>(0)

// 计算属性
const trendClass = computed(() => {
  switch (props.trendType) {
    case 'up': return 'trend-up'
    case 'down': return 'trend-down'
    default: return 'trend-neutral'
  }
})

const trendIcon = computed(() => {
  switch (props.trendType) {
    case 'up': return ArrowUp
    case 'down': return ArrowDown
    default: return Minus
  }
})

// 数字动画效果
const animateValue = (start: number, end: number, duration: number = 1000) => {
  if (!props.animated) {
    displayValue.value = end
    return
  }

  const startTime = Date.now()
  const animate = () => {
    const now = Date.now()
    const progress = Math.min((now - startTime) / duration, 1)
    const easeOutQuart = 1 - Math.pow(1 - progress, 4)
    
    displayValue.value = Math.floor(start + (end - start) * easeOutQuart)
    
    if (progress < 1) {
      requestAnimationFrame(animate)
    }
  }
  
  requestAnimationFrame(animate)
}

// 监听值变化
watch(() => props.value, (newValue) => {
  if (typeof newValue === 'number') {
    const currentValue = typeof displayValue.value === 'number' ? displayValue.value : 0
    animateValue(currentValue, newValue)
  } else {
    displayValue.value = newValue
  }
}, { immediate: true })

onMounted(() => {
  if (typeof props.value === 'number') {
    animateValue(0, props.value)
  } else {
    displayValue.value = props.value
  }
})
</script>

<style scoped>
.stat-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* 尺寸变体 */
.size-sm {
  padding: 16px;
  min-height: 120px;
}

.size-md {
  padding: 24px;
  min-height: 140px;
}

.size-lg {
  padding: 32px;
  min-height: 160px;
}

/* 颜色变体 */
.variant-primary {
  --card-color: #667eea;
  --card-color-light: #764ba2;
  --card-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.variant-success {
  --card-color: #48bb78;
  --card-color-light: #38a169;
  --card-bg: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
}

.variant-warning {
  --card-color: #ed8936;
  --card-color-light: #dd6b20;
  --card-bg: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
}

.variant-error {
  --card-color: #f56565;
  --card-color-light: #e53e3e;
  --card-bg: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
}

.variant-info {
  --card-color: #4299e1;
  --card-color-light: #3182ce;
  --card-bg: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
}

.variant-purple {
  --card-color: #9f7aea;
  --card-color-light: #805ad5;
  --card-bg: linear-gradient(135deg, #9f7aea 0%, #805ad5 100%);
}

/* 背景装饰 */
.card-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

.bg-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--card-bg);
  opacity: 0.9;
}

.bg-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
}

/* 卡片内容 */
.card-content {
  position: relative;
  z-index: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: white;
}

/* 图标区域 */
.icon-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.icon-container {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  transition: all 0.3s ease;
}

.trend-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.trend-up {
  color: #10b981;
  background: rgba(16, 185, 129, 0.2);
}

.trend-down {
  color: #f87171;
  background: rgba(248, 113, 113, 0.2);
}

.trend-neutral {
  color: #94a3b8;
  background: rgba(148, 163, 184, 0.2);
}

/* 数据区域 */
.data-section {
  flex: 1;
}

.value-container {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 8px;
}

.value {
  font-size: 36px;
  font-weight: 700;
  line-height: 1;
  transition: all 0.3s ease;
}

.value.counting {
  animation: pulse 0.5s ease-in-out;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.unit {
  font-size: 18px;
  font-weight: 500;
  opacity: 0.8;
}

.label {
  font-size: 14px;
  font-weight: 500;
  opacity: 0.9;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.description {
  font-size: 12px;
  opacity: 0.7;
  line-height: 1.4;
}

/* 进度条 */
.progress-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 3px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-text {
  font-size: 12px;
  font-weight: 600;
  opacity: 0.9;
  min-width: 32px;
  text-align: right;
}

/* 悬浮效果 */
.hover-effect {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.1);
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 0;
}

.stat-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.stat-card:hover .hover-effect {
  opacity: 1;
}

.stat-card:hover .icon-container {
  transform: scale(1.1);
  background: rgba(255, 255, 255, 0.3);
}

/* 动画效果 */
.animated {
  animation: slideInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .size-lg {
    padding: 20px;
    min-height: 140px;
  }
  
  .value {
    font-size: 28px;
  }
  
  .icon-container {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .size-md {
    padding: 16px;
    min-height: 120px;
  }
  
  .value {
    font-size: 24px;
  }
  
  .icon-container {
    width: 36px;
    height: 36px;
    font-size: 18px;
  }
  
  .trend-indicator {
    font-size: 10px;
    padding: 2px 6px;
  }
}
</style>