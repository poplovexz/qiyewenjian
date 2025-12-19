<template>
  <div class="modern-input" :class="inputClasses">
    <div class="input-wrapper">
      <!-- 前置图标 -->
      <div v-if="prefixIcon" class="input-prefix">
        <component :is="prefixIcon" class="icon" />
      </div>
      
      <!-- 输入框 -->
      <input
        ref="inputRef"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :maxlength="maxlength"
        :class="['input-field', { 'has-prefix': prefixIcon, 'has-suffix': suffixIcon || clearable }]"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        @keydown="handleKeydown"
      />
      
      <!-- 清除按钮 -->
      <div v-if="clearable && modelValue && !disabled" class="input-suffix" @click="handleClear">
        <svg class="icon clear-icon" viewBox="0 0 24 24">
          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
        </svg>
      </div>
      
      <!-- 后置图标 -->
      <div v-else-if="suffixIcon" class="input-suffix">
        <component :is="suffixIcon" class="icon" />
      </div>
    </div>
    
    <!-- 标签 -->
    <label v-if="label" class="input-label" :class="{ active: focused || modelValue }">
      {{ label }}
      <span v-if="required" class="required">*</span>
    </label>
    
    <!-- 错误信息 -->
    <div v-if="error" class="input-error">
      {{ error }}
    </div>
    
    <!-- 帮助文本 -->
    <div v-if="helpText && !error" class="input-help">
      {{ helpText }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, DefineComponent } from 'vue'

interface Props {
  modelValue?: string | number
  type?: 'text' | 'password' | 'email' | 'number' | 'tel' | 'url'
  label?: string
  placeholder?: string
  prefixIcon?: DefineComponent | string
  suffixIcon?: DefineComponent | string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  clearable?: boolean
  maxlength?: number
  error?: string
  helpText?: string
  size?: 'small' | 'medium' | 'large'
  variant?: 'outlined' | 'filled' | 'underlined'
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: undefined,
  type: 'text',
  label: undefined,
  placeholder: undefined,
  prefixIcon: undefined,
  suffixIcon: undefined,
  disabled: false,
  readonly: false,
  required: false,
  clearable: false,
  maxlength: undefined,
  error: undefined,
  helpText: undefined,
  size: 'medium',
  variant: 'outlined'
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  'focus': [event: FocusEvent]
  'blur': [event: FocusEvent]
  'clear': []
  'keydown': [event: KeyboardEvent]
}>()

const inputRef = ref<HTMLInputElement>()
const focused = ref(false)

const inputClasses = computed(() => [
  `input-${props.size}`,
  `input-${props.variant}`,
  {
    'input-disabled': props.disabled,
    'input-readonly': props.readonly,
    'input-error': props.error,
    'input-focused': focused.value
  }
])

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

const handleFocus = (event: FocusEvent) => {
  focused.value = true
  emit('focus', event)
}

const handleBlur = (event: FocusEvent) => {
  focused.value = false
  emit('blur', event)
}

const handleClear = () => {
  emit('update:modelValue', '')
  emit('clear')
  nextTick(() => {
    inputRef.value?.focus()
  })
}

const handleKeydown = (event: KeyboardEvent) => {
  emit('keydown', event)
}

const focus = () => {
  inputRef.value?.focus()
}

const blur = () => {
  inputRef.value?.blur()
}

defineExpose({
  focus,
  blur
})
</script>

<style scoped>
.modern-input {
  position: relative;
  width: 100%;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-field {
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  font-size: 1rem;
  color: var(--text-primary);
  transition: var(--transition-normal);
  z-index: 1;
}

.input-field::placeholder {
  color: var(--text-tertiary);
  transition: var(--transition-normal);
}

.input-prefix,
.input-suffix {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: var(--transition-normal);
  z-index: 2;
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
  fill: currentColor;
}

.clear-icon {
  cursor: pointer;
  opacity: 0.6;
  transition: var(--transition-fast);
}

.clear-icon:hover {
  opacity: 1;
  color: var(--error-color);
}

.input-label {
  position: absolute;
  left: 0;
  color: var(--text-secondary);
  font-size: 1rem;
  transition: var(--transition-normal);
  pointer-events: none;
  z-index: 2;
}

.required {
  color: var(--error-color);
  margin-left: 0.25rem;
}

.input-error {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: var(--error-color);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.input-help {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-tertiary);
}

/* 尺寸变体 */
.input-small .input-field {
  font-size: 0.875rem;
  padding: 0.5rem;
}

.input-small .input-prefix,
.input-small .input-suffix {
  padding: 0 0.75rem;
}

.input-small .input-label {
  font-size: 0.875rem;
}

.input-medium .input-field {
  font-size: 1rem;
  padding: 0.75rem;
}

.input-medium .input-prefix,
.input-medium .input-suffix {
  padding: 0 1rem;
}

.input-large .input-field {
  font-size: 1.125rem;
  padding: 1rem;
}

.input-large .input-prefix,
.input-large .input-suffix {
  padding: 0 1.25rem;
}

/* 样式变体 */
.input-outlined .input-wrapper {
  border: 2px solid var(--border-color);
  border-radius: var(--radius-lg);
  background: var(--bg-primary);
  transition: var(--transition-normal);
}

.input-outlined.input-focused .input-wrapper {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-outlined.input-error .input-wrapper {
  border-color: var(--error-color);
  box-shadow: 0 0 0 3px rgba(245, 101, 101, 0.1);
}

.input-outlined .input-label {
  top: 50%;
  transform: translateY(-50%);
  left: 1rem;
  background: var(--bg-primary);
  padding: 0 0.5rem;
}

.input-outlined .input-label.active {
  top: 0;
  transform: translateY(-50%);
  font-size: 0.875rem;
  color: var(--primary-color);
}

.input-outlined .input-field.has-prefix {
  padding-left: 3rem;
}

.input-outlined .input-field.has-suffix {
  padding-right: 3rem;
}

.input-filled .input-wrapper {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  border-bottom: 2px solid var(--border-color);
  transition: var(--transition-normal);
}

.input-filled.input-focused .input-wrapper {
  background: var(--bg-primary);
  border-bottom-color: var(--primary-color);
}

.input-filled.input-error .input-wrapper {
  border-bottom-color: var(--error-color);
}

.input-filled .input-label {
  top: 1.5rem;
  left: 1rem;
}

.input-filled .input-label.active {
  top: 0.5rem;
  font-size: 0.875rem;
  color: var(--primary-color);
}

.input-underlined .input-wrapper {
  border-bottom: 2px solid var(--border-color);
  border-radius: 0;
  transition: var(--transition-normal);
}

.input-underlined.input-focused .input-wrapper {
  border-bottom-color: var(--primary-color);
}

.input-underlined.input-error .input-wrapper {
  border-bottom-color: var(--error-color);
}

.input-underlined .input-label {
  top: 50%;
  transform: translateY(-50%);
  left: 0;
}

.input-underlined .input-label.active {
  top: -1.5rem;
  transform: none;
  font-size: 0.875rem;
  color: var(--primary-color);
}

/* 状态样式 */
.input-disabled .input-wrapper {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-disabled .input-field {
  cursor: not-allowed;
}

.input-readonly .input-field {
  cursor: default;
}

/* 深色模式 */
.dark .input-outlined .input-wrapper {
  background: var(--bg-secondary-dark);
  border-color: var(--gray-600);
}

.dark .input-outlined .input-label {
  background: var(--bg-secondary-dark);
}

.dark .input-filled .input-wrapper {
  background: var(--bg-tertiary-dark);
}

.dark .input-filled.input-focused .input-wrapper {
  background: var(--bg-secondary-dark);
}

/* 动画 */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.input-error .input-wrapper {
  animation: shake 0.3s ease-in-out;
}
</style>