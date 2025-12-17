<template>
  <div 
    class="modern-card" 
    :class="[
      `variant-${variant}`,
      `size-${size}`,
      { 
        'hoverable': hoverable,
        'clickable': clickable,
        'loading': loading,
        'elevated': elevated
      }
    ]"
    @click="handleClick"
  >
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>

    <!-- 卡片头部 -->
    <div v-if="$slots.header || title || subtitle" class="card-header">
      <slot name="header">
        <div class="header-content">
          <div v-if="icon" class="header-icon">
            <el-icon><component :is="icon" /></el-icon>
          </div>
          <div class="header-text">
            <h3 v-if="title" class="card-title">{{ title }}</h3>
            <p v-if="subtitle" class="card-subtitle">{{ subtitle }}</p>
          </div>
        </div>
      </slot>
      <div v-if="$slots.actions" class="header-actions">
        <slot name="actions"></slot>
      </div>
    </div>

    <!-- 卡片内容 -->
    <div class="card-body">
      <slot></slot>
    </div>

    <!-- 卡片底部 -->
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </div>

    <!-- 装饰性元素 -->
    <div v-if="decorative" class="card-decoration">
      <div class="decoration-circle decoration-1"></div>
      <div class="decoration-circle decoration-2"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'error' | 'glass'
  size?: 'sm' | 'md' | 'lg'
  title?: string
  subtitle?: string
  icon?: string
  hoverable?: boolean
  clickable?: boolean
  loading?: boolean
  elevated?: boolean
  decorative?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
  hoverable: true,
  clickable: false,
  loading: false,
  elevated: false,
  decorative: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const handleClick = (event: MouseEvent) => {
  if (props.clickable && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
.modern-card {
  position: relative;
  border-radius: var(--radius-lg);
  background: var(--bg-primary);
  border: 1px solid var(--gray-200);
  transition: all var(--transition-normal);
  overflow: hidden;
}

/* 变体样式 */
.variant-default {
  background: var(--bg-primary);
  border-color: var(--gray-200);
}

.variant-primary {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  border-color: rgba(102, 126, 234, 0.2);
}

.variant-success {
  background: linear-gradient(135deg, rgba(72, 187, 120, 0.05), rgba(16, 185, 129, 0.05));
  border-color: rgba(72, 187, 120, 0.2);
}

.variant-warning {
  background: linear-gradient(135deg, rgba(237, 137, 54, 0.05), rgba(245, 158, 11, 0.05));
  border-color: rgba(237, 137, 54, 0.2);
}

.variant-error {
  background: linear-gradient(135deg, rgba(245, 101, 101, 0.05), rgba(239, 68, 68, 0.05));
  border-color: rgba(245, 101, 101, 0.2);
}

.variant-glass {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* 尺寸样式 */
.size-sm {
  padding: var(--spacing-md);
}

.size-md {
  padding: var(--spacing-lg);
}

.size-lg {
  padding: var(--spacing-xl);
}

/* 状态样式 */
.hoverable:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-color);
}

.clickable {
  cursor: pointer;
}

.clickable:active {
  transform: translateY(-2px);
}

.elevated {
  box-shadow: var(--shadow-md);
}

.loading {
  pointer-events: none;
}

/* 加载状态 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  backdrop-filter: blur(2px);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--gray-200);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--gray-100);
}

.header-content {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  flex: 1;
}

.header-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  flex-shrink: 0;
}

.header-text {
  flex: 1;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  line-height: 1.3;
}

.card-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.4;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-shrink: 0;
}

/* 卡片内容 */
.card-body {
  flex: 1;
}

/* 卡片底部 */
.card-footer {
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--gray-100);
}

/* 装饰性元素 */
.card-decoration {
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  pointer-events: none;
  overflow: hidden;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: var(--primary-gradient);
  opacity: 0.1;
}

.decoration-1 {
  width: 60px;
  height: 60px;
  top: -30px;
  right: -30px;
}

.decoration-2 {
  width: 40px;
  height: 40px;
  top: 20px;
  right: 10px;
  opacity: 0.05;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .size-lg {
    padding: var(--spacing-lg);
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .variant-default {
    background: var(--gray-800);
    border-color: var(--gray-700);
  }
  
  .variant-glass {
    background: rgba(30, 30, 30, 0.8);
    border-color: rgba(255, 255, 255, 0.1);
  }
  
  .loading-overlay {
    background: rgba(30, 30, 30, 0.8);
  }
  
  .card-header,
  .card-footer {
    border-color: var(--gray-700);
  }
}
</style>