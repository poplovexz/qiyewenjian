<template>
  <button
    class="modern-button"
    :class="[
      `variant-${variant}`,
      `size-${size}`,
      {
        'loading': loading,
        'disabled': disabled,
        'icon-only': iconOnly,
        'rounded': rounded,
        'elevated': elevated,
        'gradient': gradient
      }
    ]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <!-- 背景效果 -->
    <div class="button-background">
      <div class="ripple-effect" ref="rippleRef"></div>
      <div class="gradient-overlay"></div>
    </div>

    <!-- 按钮内容 -->
    <div class="button-content">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-spinner">
        <div class="spinner"></div>
      </div>

      <!-- 图标 -->
      <el-icon v-if="icon && !loading" class="button-icon" :class="{ 'icon-left': $slots.default }">
        <component :is="icon" />
      </el-icon>

      <!-- 文本内容 -->
      <span v-if="$slots.default && !iconOnly" class="button-text">
        <slot></slot>
      </span>

      <!-- 右侧图标 -->
      <el-icon v-if="rightIcon" class="button-icon icon-right">
        <component :is="rightIcon" />
      </el-icon>
    </div>

    <!-- 悬浮效果 -->
    <div class="hover-overlay"></div>
  </button>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'ghost' | 'outline'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  icon?: string
  rightIcon?: string
  loading?: boolean
  disabled?: boolean
  iconOnly?: boolean
  rounded?: boolean
  elevated?: boolean
  gradient?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  loading: false,
  disabled: false,
  iconOnly: false,
  rounded: false,
  elevated: false,
  gradient: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const rippleRef = ref<HTMLElement>()

const handleClick = (event: MouseEvent) => {
  if (props.disabled || props.loading) return

  // 创建涟漪效果
  createRipple(event)
  
  emit('click', event)
}

const createRipple = (event: MouseEvent) => {
  const button = event.currentTarget as HTMLElement
  const rect = button.getBoundingClientRect()
  const size = Math.max(rect.width, rect.height)
  const x = event.clientX - rect.left - size / 2
  const y = event.clientY - rect.top - size / 2

  const ripple = document.createElement('div')
  ripple.className = 'ripple'
  ripple.style.width = ripple.style.height = size + 'px'
  ripple.style.left = x + 'px'
  ripple.style.top = y + 'px'

  if (rippleRef.value) {
    rippleRef.value.appendChild(ripple)
    
    setTimeout(() => {
      ripple.remove()
    }, 600)
  }
}
</script>

<style scoped>
.modern-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  outline: none;
  cursor: pointer;
  font-family: inherit;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  user-select: none;
  border-radius: var(--radius-md);
}

/* 尺寸变体 */
.size-xs {
  padding: 6px 12px;
  font-size: 12px;
  min-height: 28px;
  gap: 4px;
}

.size-sm {
  padding: 8px 16px;
  font-size: 13px;
  min-height: 32px;
  gap: 6px;
}

.size-md {
  padding: 10px 20px;
  font-size: 14px;
  min-height: 40px;
  gap: 8px;
}

.size-lg {
  padding: 12px 24px;
  font-size: 16px;
  min-height: 48px;
  gap: 10px;
}

.size-xl {
  padding: 16px 32px;
  font-size: 18px;
  min-height: 56px;
  gap: 12px;
}

/* 图标专用按钮 */
.icon-only.size-xs { padding: 6px; width: 28px; }
.icon-only.size-sm { padding: 8px; width: 32px; }
.icon-only.size-md { padding: 10px; width: 40px; }
.icon-only.size-lg { padding: 12px; width: 48px; }
.icon-only.size-xl { padding: 16px; width: 56px; }

/* 圆角变体 */
.rounded {
  border-radius: 50px;
}

/* 阴影变体 */
.elevated {
  box-shadow: var(--shadow-md);
}

.elevated:hover {
  box-shadow: var(--shadow-lg);
}

/* 颜色变体 */
.variant-primary {
  background: var(--primary-color);
  color: white;
}

.variant-primary.gradient {
  background: var(--primary-gradient);
}

.variant-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
}

.variant-secondary {
  background: var(--gray-100);
  color: var(--text-primary);
}

.variant-secondary:hover {
  background: var(--gray-200);
  transform: translateY(-2px);
}

.variant-success {
  background: var(--success-color);
  color: white;
}

.variant-success.gradient {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
}

.variant-success:hover {
  background: #38a169;
  transform: translateY(-2px);
}

.variant-warning {
  background: var(--warning-color);
  color: white;
}

.variant-warning.gradient {
  background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
}

.variant-warning:hover {
  background: #dd6b20;
  transform: translateY(-2px);
}

.variant-error {
  background: var(--error-color);
  color: white;
}

.variant-error.gradient {
  background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
}

.variant-error:hover {
  background: #e53e3e;
  transform: translateY(-2px);
}

.variant-ghost {
  background: transparent;
  color: var(--primary-color);
}

.variant-ghost:hover {
  background: rgba(102, 126, 234, 0.1);
  color: var(--primary-dark);
}

.variant-outline {
  background: transparent;
  color: var(--primary-color);
  border: 2px solid var(--primary-color);
}

.variant-outline:hover {
  background: var(--primary-color);
  color: white;
}

/* 状态样式 */
.loading,
.disabled {
  cursor: not-allowed;
  opacity: 0.6;
  transform: none !important;
}

.loading:hover,
.disabled:hover {
  transform: none !important;
}

/* 背景效果 */
.button-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

.ripple-effect {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%);
  transform: translateX(-100%);
  transition: transform 0.6s ease;
}

.modern-button:hover .gradient-overlay {
  transform: translateX(100%);
}

/* 按钮内容 */
.button-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: inherit;
}

.button-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.button-icon {
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.icon-right {
  order: 1;
}

/* 加载动画 */
.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 涟漪效果 */
.ripple {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: scale(0);
  animation: ripple-animation 0.6s ease-out;
  pointer-events: none;
}

@keyframes ripple-animation {
  to {
    transform: scale(2);
    opacity: 0;
  }
}

/* 悬浮覆盖层 */
.hover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.1);
  opacity: 0;
  transition: opacity 0.2s ease;
  z-index: 0;
}

.modern-button:hover .hover-overlay {
  opacity: 1;
}

/* 焦点状态 */
.modern-button:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

/* 激活状态 */
.modern-button:active {
  transform: translateY(0) scale(0.98);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .size-lg {
    padding: 10px 20px;
    font-size: 14px;
    min-height: 44px;
  }
  
  .size-xl {
    padding: 12px 24px;
    font-size: 16px;
    min-height: 48px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .variant-secondary {
    background: var(--gray-700);
    color: var(--gray-100);
  }
  
  .variant-secondary:hover {
    background: var(--gray-600);
  }
  
  .variant-ghost:hover {
    background: rgba(102, 126, 234, 0.2);
  }
}
</style>