<template>
  <van-dialog
    v-model:show="dialogVisible"
    :title="dialogTitle"
    show-cancel-button
    :before-close="beforeClose"
    @confirm="onConfirm"
    @cancel="onCancel"
  >
    <div class="approval-dialog-content">
      <van-radio-group v-model="form.shenhe_jieguo">
        <van-cell-group inset>
          <van-cell title="通过" clickable @click="form.shenhe_jieguo = 'tongguo'">
            <template #right-icon>
              <van-radio name="tongguo" />
            </template>
          </van-cell>
          <van-cell title="拒绝" clickable @click="form.shenhe_jieguo = 'jujue'">
            <template #right-icon>
              <van-radio name="jujue" />
            </template>
          </van-cell>
        </van-cell-group>
      </van-radio-group>

      <van-cell-group inset style="margin-top: 12px;">
        <van-field
          v-model="form.shenhe_yijian"
          type="textarea"
          label="审批意见"
          placeholder="请输入审批意见"
          rows="4"
          maxlength="200"
          show-word-limit
          :required="form.shenhe_jieguo === 'jujue'"
        />
      </van-cell-group>
    </div>
  </van-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { showToast } from 'vant'

interface Props {
  visible: boolean
  title?: string
  defaultAction?: 'tongguo' | 'jujue'
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: { shenhe_jieguo: string; shenhe_yijian: string }): void
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  title: '审批',
  defaultAction: 'tongguo'
})

const emit = defineEmits<Emits>()

const form = ref({
  shenhe_jieguo: props.defaultAction,
  shenhe_yijian: ''
})

const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const dialogTitle = computed(() => {
  return props.title || '审批'
})

// 关闭前验证
const beforeClose = (action: string) => {
  if (action === 'confirm') {
    if (form.value.shenhe_jieguo === 'jujue' && !form.value.shenhe_yijian) {
      showToast('拒绝时必须填写审批意见')
      return false
    }
  }
  return true
}

// 确认
const onConfirm = () => {
  if (form.value.shenhe_jieguo === 'jujue' && !form.value.shenhe_yijian) {
    showToast('拒绝时必须填写审批意见')
    return
  }

  emit('submit', {
    shenhe_jieguo: form.value.shenhe_jieguo,
    shenhe_yijian: form.value.shenhe_yijian
  })

  // 重置表单
  form.value = {
    shenhe_jieguo: props.defaultAction,
    shenhe_yijian: ''
  }
}

// 取消
const onCancel = () => {
  // 重置表单
  form.value = {
    shenhe_jieguo: props.defaultAction,
    shenhe_yijian: ''
  }
}

// 监听defaultAction变化
watch(() => props.defaultAction, (newVal) => {
  form.value.shenhe_jieguo = newVal
})

// 监听visible变化，重置表单
watch(() => props.visible, (newVal) => {
  if (newVal) {
    form.value = {
      shenhe_jieguo: props.defaultAction,
      shenhe_yijian: ''
    }
  }
})
</script>

<style scoped>
.approval-dialog-content {
  padding: 16px 0;
}
</style>

