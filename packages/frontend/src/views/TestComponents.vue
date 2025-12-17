<template>
  <div class="test-container">
    <h1>组件测试页面</h1>
    
    <div class="test-section">
      <h2>ModernCard 测试</h2>
      <ModernCard title="测试卡片" subtitle="这是一个测试卡片">
        <p>卡片内容</p>
      </ModernCard>
    </div>

    <div class="test-section">
      <h2>ModernInput 测试</h2>
      <ModernInput
        v-model="testInput"
        label="测试输入框"
        placeholder="请输入内容"
      />
    </div>

    <div class="test-section">
      <h2>ModernButton 测试</h2>
      <ModernButton variant="primary">测试按钮</ModernButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ModernCard from '@/components/ui/ModernCard.vue'
import ModernInput from '@/components/ui/ModernInput.vue'
import ModernButton from '@/components/ui/ModernButton.vue'

const testInput = ref('')
</script>

<style scoped>
.test-container {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.test-section {
  margin-bottom: 2rem;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

h1, h2 {
  color: #2d3748;
  margin-bottom: 1rem;
}
</style>