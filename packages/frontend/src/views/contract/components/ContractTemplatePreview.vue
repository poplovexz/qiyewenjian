<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="emit('update:visible', $event)"
    title="合同模板预览"
    width="1200px"
    :before-close="handleClose"
    destroy-on-close
  >
    <div class="preview-container">
      <!-- 变量输入区域 -->
      <div class="variables-panel">
        <div class="panel-header">
          <h4>变量设置</h4>
          <el-button size="small" @click="loadDefaultVariables">
            加载默认值
          </el-button>
        </div>
        
        <div class="variables-form">
          <el-form label-width="120px" size="small">
            <el-form-item
              v-for="(variable, key) in availableVariables"
              :key="key"
              :label="variable.label || key"
            >
              <el-input
                v-if="variable.type === 'string' || !variable.type"
                v-model="variableValues[key]"
                :placeholder="`请输入${variable.label || key}`"
              />
              <el-input-number
                v-else-if="variable.type === 'number'"
                v-model="variableValues[key]"
                :placeholder="`请输入${variable.label || key}`"
                style="width: 100%"
              />
              <el-date-picker
                v-else-if="variable.type === 'date'"
                v-model="variableValues[key]"
                type="date"
                :placeholder="`请选择${variable.label || key}`"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            
            <!-- 如果没有配置变量，显示通用变量输入 -->
            <template v-if="Object.keys(availableVariables).length === 0">
              <el-form-item
                v-for="variable in commonVariables"
                :key="variable.name"
                :label="variable.desc"
              >
                <el-input
                  v-model="variableValues[variable.name]"
                  :placeholder="`请输入${variable.desc}`"
                />
              </el-form-item>
            </template>
          </el-form>
        </div>
        
        <div class="panel-actions">
          <el-button type="primary" @click="handlePreview">
            <el-icon><View /></el-icon>
            预览
          </el-button>
          <el-button @click="handleExport">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </div>
      </div>
      
      <!-- 预览区域 -->
      <div class="preview-panel">
        <div class="panel-header">
          <h4>预览效果</h4>
          <div class="preview-actions">
            <el-button size="small" @click="toggleFullscreen">
              <el-icon><FullScreen /></el-icon>
              全屏
            </el-button>
            <el-button size="small" @click="handlePrint">
              <el-icon><Printer /></el-icon>
              打印
            </el-button>
          </div>
        </div>
        
        <div 
          class="preview-content"
          :class="{ 'fullscreen': isFullscreen }"
          v-loading="previewLoading"
        >
          <div class="content-wrapper" v-html="sanitizeContractHtml(previewContent)"></div>
        </div>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="handleSaveAsTemplate">
          另存为模板
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { View, Download, FullScreen, Printer } from '@element-plus/icons-vue'
import { useContractStore } from '@/stores/modules/contract'
import type { ContractTemplate } from '@/api/modules/contract'
import { sanitizeContractHtml } from '@/utils/sanitize'

// Props
interface Props {
  visible: boolean
  template?: ContractTemplate | null
}

const props = withDefaults(defineProps<Props>(), {
  template: null
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

// Store
const contractStore = useContractStore()

// 响应式数据
const previewLoading = ref(false)
const isFullscreen = ref(false)
const previewContent = ref('')
const availableVariables = ref<Record<string, any>>({})
const variableValues = reactive<Record<string, any>>({})

// 常用变量
const commonVariables = [
  { name: 'kehu_mingcheng', desc: '客户名称' },
  { name: 'kehu_dizhi', desc: '客户地址' },
  { name: 'kehu_lianxi', desc: '客户联系方式' },
  { name: 'fuwu_neirong', desc: '服务内容' },
  { name: 'fuwu_jiage', desc: '服务价格' },
  { name: 'hetong_qixian', desc: '合同期限' },
  { name: 'qianyue_riqi', desc: '签约日期' },
  { name: 'shengxiao_riqi', desc: '生效日期' }
]

// 监听器
watch(() => props.visible, async (visible) => {
  if (visible && props.template) {
    await loadTemplateVariables()
    await handlePreview()
  }
})

// 方法
const loadTemplateVariables = async () => {
  if (!props.template) return
  
  try {
    // 获取模板变量配置
    const variables = await contractStore.getTemplateVariables(props.template.id)
    availableVariables.value = variables
    
    // 初始化变量值
    Object.keys(variables).forEach(key => {
      const variable = variables[key]
      variableValues[key] = variable.default || ''
    })
    
    // 如果没有配置变量，使用通用变量
    if (Object.keys(variables).length === 0) {
      commonVariables.forEach(variable => {
        variableValues[variable.name] = ''
      })
    }
  } catch (error) {
    console.error('加载模板变量失败:', error)
    // 使用通用变量作为备选
    commonVariables.forEach(variable => {
      variableValues[variable.name] = ''
    })
  }
}

const loadDefaultVariables = () => {
  // 加载默认变量值
  Object.keys(availableVariables.value).forEach(key => {
    const variable = availableVariables.value[key]
    variableValues[key] = variable.default || ''
  })
  
  // 如果没有配置变量，使用示例值
  if (Object.keys(availableVariables.value).length === 0) {
    Object.assign(variableValues, {
      kehu_mingcheng: '示例科技有限公司',
      kehu_dizhi: '北京市朝阳区示例路123号',
      kehu_lianxi: '010-12345678',
      fuwu_neirong: '代理记账服务',
      fuwu_jiage: '2000.00',
      hetong_qixian: '12个月',
      qianyue_riqi: new Date().toISOString().split('T')[0],
      shengxiao_riqi: new Date().toISOString().split('T')[0]
    })
  }
}

const handlePreview = async () => {
  if (!props.template) return
  
  try {
    previewLoading.value = true
    
    // 调用预览API
    const content = await contractStore.previewTemplate(props.template.id, variableValues)
    
    // 处理内容格式
    previewContent.value = formatPreviewContent(content)
  } catch (error) {
    console.error('预览失败:', error)
    ElMessage.error('预览失败')
  } finally {
    previewLoading.value = false
  }
}

const formatPreviewContent = (content: string) => {
  // 将换行符转换为HTML换行
  let formatted = content.replace(/\n/g, '<br>')
  
  // 添加基本样式
  formatted = `
    <div style="
      font-family: 'Microsoft YaHei', Arial, sans-serif;
      font-size: 14px;
      line-height: 1.6;
      color: #333;
      padding: 20px;
      background: white;
    ">
      ${formatted}
    </div>
  `
  
  return formatted
}

const handleExport = () => {
  if (!previewContent.value) {
    ElMessage.warning('请先预览内容')
    return
  }
  
  // 创建下载链接
  const blob = new Blob([previewContent.value], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${props.template?.moban_mingcheng || '合同模板'}.html`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  ElMessage.success('导出成功')
}

const handlePrint = () => {
  if (!previewContent.value) {
    ElMessage.warning('请先预览内容')
    return
  }
  
  // 打开新窗口进行打印
  const printWindow = window.open('', '_blank')
  if (printWindow) {
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>合同模板打印</title>
          <style>
            @media print {
              body { margin: 0; }
              .no-print { display: none; }
            }
          </style>
        </head>
        <body>
          ${previewContent.value}
        </body>
      </html>
    `)
    printWindow.document.close()
    printWindow.print()
  }
}

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

const handleSaveAsTemplate = () => {
  // TODO: 实现另存为模板功能
  ElMessage.info('功能开发中...')
}

const handleClose = () => {
  emit('update:visible', false)
  isFullscreen.value = false
}

// 生命周期
onMounted(() => {
  // 初始化
})
</script>

<style scoped>
.preview-container {
  display: flex;
  height: 600px;
  gap: 20px;
}

.variables-panel {
  width: 300px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
}

.preview-panel {
  flex: 1;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #f5f7fa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h4 {
  margin: 0;
  color: #303133;
  font-size: 14px;
}

.variables-form {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.panel-actions {
  padding: 12px 16px;
  border-top: 1px solid #e4e7ed;
  background-color: #f5f7fa;
  display: flex;
  gap: 8px;
}

.preview-content {
  flex: 1;
  overflow: auto;
  background-color: #fff;
}

.preview-content.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  background: white;
}

.content-wrapper {
  min-height: 100%;
}

.preview-actions {
  display: flex;
  gap: 8px;
}

:deep(.el-form-item) {
  margin-bottom: 16px;
}

:deep(.el-form-item__label) {
  font-size: 12px;
}

:deep(.el-input),
:deep(.el-input-number),
:deep(.el-date-editor) {
  font-size: 12px;
}
</style>
