<template>
  <div class="modern-table" :class="tableClasses">
    <!-- 表格头部 -->
    <div v-if="title || $slots.header" class="table-header">
      <div class="table-title">
        <h3 v-if="title">{{ title }}</h3>
        <p v-if="description" class="table-description">{{ description }}</p>
      </div>
      <div class="table-actions">
        <slot name="header" />
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div v-if="searchable || filterable" class="table-controls">
      <div v-if="searchable" class="search-box">
        <ModernInput
          v-model="searchQuery"
          placeholder="搜索..."
          :prefix-icon="SearchIcon"
          clearable
          @input="handleSearch"
        />
      </div>
      <div v-if="filterable" class="filter-box">
        <slot name="filters" />
      </div>
    </div>

    <!-- 表格容器 -->
    <div class="table-container" :class="{ 'table-loading': loading }">
      <!-- 加载状态 -->
      <div v-if="loading" class="table-loading-overlay">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- 表格 -->
      <table class="table">
        <thead class="table-head">
          <tr>
            <!-- 选择列 -->
            <th v-if="selectable" class="table-cell select-cell">
              <input
                type="checkbox"
                :checked="isAllSelected"
                :indeterminate="isIndeterminate"
                @change="handleSelectAll"
                class="checkbox"
              />
            </th>
            
            <!-- 数据列 -->
            <th
              v-for="column in columns"
              :key="column.key"
              class="table-cell"
              :class="[
                `align-${column.align || 'left'}`,
                { 'sortable': column.sortable, 'sorted': sortBy === column.key }
              ]"
              :style="{ width: column.width }"
              @click="column.sortable && handleSort(column.key)"
            >
              <div class="cell-content">
                <span>{{ column.title }}</span>
                <div v-if="column.sortable" class="sort-icons">
                  <svg
                    class="sort-icon"
                    :class="{ active: sortBy === column.key && sortOrder === 'asc' }"
                    viewBox="0 0 24 24"
                  >
                    <path d="M7 14l5-5 5 5z"/>
                  </svg>
                  <svg
                    class="sort-icon"
                    :class="{ active: sortBy === column.key && sortOrder === 'desc' }"
                    viewBox="0 0 24 24"
                  >
                    <path d="M7 10l5 5 5-5z"/>
                  </svg>
                </div>
              </div>
            </th>
          </tr>
        </thead>
        
        <tbody class="table-body">
          <!-- 空状态 -->
          <tr v-if="!loading && filteredData.length === 0" class="empty-row">
            <td :colspan="totalColumns" class="empty-cell">
              <div class="empty-state">
                <div class="empty-icon">
                  <svg viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                  </svg>
                </div>
                <p>{{ emptyText || '暂无数据' }}</p>
              </div>
            </td>
          </tr>
          
          <!-- 数据行 -->
          <tr
            v-for="(row, index) in paginatedData"
            :key="getRowKey(row, index)"
            class="table-row"
            :class="{ 
              'selected': selectedRows.includes(getRowKey(row, index)),
              'clickable': rowClickable
            }"
            @click="handleRowClick(row, index)"
          >
            <!-- 选择列 -->
            <td v-if="selectable" class="table-cell select-cell">
              <input
                type="checkbox"
                :checked="selectedRows.includes(getRowKey(row, index))"
                @change="handleRowSelect(getRowKey(row, index))"
                @click.stop
                class="checkbox"
              />
            </td>
            
            <!-- 数据列 -->
            <td
              v-for="column in columns"
              :key="column.key"
              class="table-cell"
              :class="`align-${column.align || 'left'}`"
            >
              <div class="cell-content">
                <!-- 自定义渲染 -->
                <slot
                  v-if="$slots[`cell-${column.key}`]"
                  :name="`cell-${column.key}`"
                  :row="row"
                  :column="column"
                  :index="index"
                  :value="row[column.key]"
                />
                <!-- 默认渲染 -->
                <span v-else>{{ formatCellValue(row[column.key], column) }}</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div v-if="pagination && !loading" class="table-pagination">
      <div class="pagination-info">
        显示 {{ paginationStart }}-{{ paginationEnd }} 条，共 {{ filteredData.length }} 条
      </div>
      <div class="pagination-controls">
        <button
          class="pagination-btn"
          :disabled="currentPage === 1"
          @click="handlePageChange(currentPage - 1)"
        >
          上一页
        </button>
        
        <div class="page-numbers">
          <button
            v-for="page in visiblePages"
            :key="page"
            class="page-btn"
            :class="{ active: page === currentPage }"
            @click="handlePageChange(page)"
          >
            {{ page }}
          </button>
        </div>
        
        <button
          class="pagination-btn"
          :disabled="currentPage === totalPages"
          @click="handlePageChange(currentPage + 1)"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import ModernInput from './ModernInput.vue'

// 搜索图标组件
const SearchIcon = {
  template: `
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
    </svg>
  `
}

interface Column {
  key: string
  title: string
  width?: string
  align?: 'left' | 'center' | 'right'
  sortable?: boolean
  formatter?: (value: any) => string
}

interface Props {
  data: any[]
  columns: Column[]
  title?: string
  description?: string
  loading?: boolean
  selectable?: boolean
  searchable?: boolean
  filterable?: boolean
  pagination?: boolean
  pageSize?: number
  rowKey?: string | ((row: any) => string)
  rowClickable?: boolean
  emptyText?: string
  size?: 'small' | 'medium' | 'large'
  variant?: 'default' | 'striped' | 'bordered'
}

const props = withDefaults(defineProps<Props>(), {
  pageSize: 10,
  rowKey: 'id',
  size: 'medium',
  variant: 'default'
})

const emit = defineEmits<{
  'row-click': [row: any, index: number]
  'selection-change': [selectedRows: string[]]
  'sort-change': [sortBy: string, sortOrder: 'asc' | 'desc']
}>()

// 响应式数据
const searchQuery = ref('')
const sortBy = ref('')
const sortOrder = ref<'asc' | 'desc'>('asc')
const selectedRows = ref<string[]>([])
const currentPage = ref(1)

// 计算属性
const tableClasses = computed(() => [
  `table-${props.size}`,
  `table-${props.variant}`,
  {
    'table-selectable': props.selectable,
    'table-clickable': props.rowClickable
  }
])

const totalColumns = computed(() => {
  return props.columns.length + (props.selectable ? 1 : 0)
})

const filteredData = computed(() => {
  let result = [...props.data]
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(row =>
      props.columns.some(column =>
        String(row[column.key]).toLowerCase().includes(query)
      )
    )
  }
  
  // 排序
  if (sortBy.value) {
    result.sort((a, b) => {
      const aVal = a[sortBy.value]
      const bVal = b[sortBy.value]
      
      if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1
      if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1
      return 0
    })
  }
  
  return result
})

const totalPages = computed(() => {
  if (!props.pagination) return 1
  return Math.ceil(filteredData.value.length / props.pageSize)
})

const paginatedData = computed(() => {
  if (!props.pagination) return filteredData.value
  
  const start = (currentPage.value - 1) * props.pageSize
  const end = start + props.pageSize
  return filteredData.value.slice(start, end)
})

const paginationStart = computed(() => {
  if (!props.pagination || filteredData.value.length === 0) return 0
  return (currentPage.value - 1) * props.pageSize + 1
})

const paginationEnd = computed(() => {
  if (!props.pagination) return filteredData.value.length
  return Math.min(currentPage.value * props.pageSize, filteredData.value.length)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 3) {
      pages.push(1)
      pages.push('...')
      for (let i = total - 4; i <= total; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1)
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    }
  }
  
  return pages
})

const isAllSelected = computed(() => {
  return paginatedData.value.length > 0 && 
         paginatedData.value.every(row => selectedRows.value.includes(getRowKey(row, 0)))
})

const isIndeterminate = computed(() => {
  const selectedCount = paginatedData.value.filter(row => 
    selectedRows.value.includes(getRowKey(row, 0))
  ).length
  return selectedCount > 0 && selectedCount < paginatedData.value.length
})

// 方法
const getRowKey = (row: any, index: number): string => {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(row)
  }
  return row[props.rowKey] || String(index)
}

const formatCellValue = (value: any, column: Column): string => {
  if (column.formatter) {
    return column.formatter(value)
  }
  return String(value || '')
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleSort = (key: string) => {
  if (sortBy.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = key
    sortOrder.value = 'asc'
  }
  
  emit('sort-change', sortBy.value, sortOrder.value)
}

const handleRowClick = (row: any, index: number) => {
  if (props.rowClickable) {
    emit('row-click', row, index)
  }
}

const handleRowSelect = (rowKey: string) => {
  const index = selectedRows.value.indexOf(rowKey)
  if (index > -1) {
    selectedRows.value.splice(index, 1)
  } else {
    selectedRows.value.push(rowKey)
  }
  
  emit('selection-change', selectedRows.value)
}

const handleSelectAll = () => {
  if (isAllSelected.value) {
    // 取消选择当前页所有行
    paginatedData.value.forEach(row => {
      const rowKey = getRowKey(row, 0)
      const index = selectedRows.value.indexOf(rowKey)
      if (index > -1) {
        selectedRows.value.splice(index, 1)
      }
    })
  } else {
    // 选择当前页所有行
    paginatedData.value.forEach(row => {
      const rowKey = getRowKey(row, 0)
      if (!selectedRows.value.includes(rowKey)) {
        selectedRows.value.push(rowKey)
      }
    })
  }
  
  emit('selection-change', selectedRows.value)
}

const handlePageChange = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 监听数据变化，重置分页
watch(() => props.data, () => {
  currentPage.value = 1
})
</script>

<style scoped>
.modern-table {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.table-title h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.table-description {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.table-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  gap: 1rem;
}

.search-box {
  flex: 1;
  max-width: 300px;
}

.table-container {
  position: relative;
  overflow-x: auto;
}

.table-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--border-color);
  border-top: 2px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table-head {
  background: var(--bg-secondary);
}

.table-cell {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  transition: var(--transition-fast);
}

.table-head .table-cell {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.table-body .table-cell {
  color: var(--text-secondary);
}

.cell-content {
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.align-center .cell-content {
  justify-content: center;
}

.align-right .cell-content {
  justify-content: flex-end;
}

.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  background: var(--bg-tertiary);
}

.sort-icons {
  display: flex;
  flex-direction: column;
  margin-left: 0.5rem;
}

.sort-icon {
  width: 0.75rem;
  height: 0.75rem;
  fill: var(--text-tertiary);
  transition: var(--transition-fast);
}

.sort-icon.active {
  fill: var(--primary-color);
}

.select-cell {
  width: 3rem;
  text-align: center;
}

.checkbox {
  width: 1rem;
  height: 1rem;
  accent-color: var(--primary-color);
}

.table-row {
  transition: var(--transition-fast);
}

.table-row:hover {
  background: var(--bg-secondary);
}

.table-row.selected {
  background: rgba(102, 126, 234, 0.05);
}

.table-row.clickable {
  cursor: pointer;
}

.empty-row {
  height: 200px;
}

.empty-cell {
  text-align: center;
  vertical-align: middle;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--text-tertiary);
}

.empty-icon {
  width: 3rem;
  height: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
  fill: currentColor;
}

.table-pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
}

.pagination-info {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-btn,
.page-btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition-fast);
  font-size: 0.875rem;
}

.pagination-btn:hover:not(:disabled),
.page-btn:hover {
  background: var(--bg-secondary);
  border-color: var(--primary-color);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.page-numbers {
  display: flex;
  gap: 0.25rem;
}

/* 尺寸变体 */
.table-small .table-cell {
  padding: 0.5rem;
  font-size: 0.875rem;
}

.table-large .table-cell {
  padding: 1.5rem;
  font-size: 1.125rem;
}

/* 样式变体 */
.table-striped .table-row:nth-child(even) {
  background: var(--bg-secondary);
}

.table-bordered .table-cell {
  border-right: 1px solid var(--border-color);
}

.table-bordered .table-cell:last-child {
  border-right: none;
}

/* 深色模式 */
.dark .modern-table {
  background: var(--bg-secondary-dark);
}

.dark .table-head {
  background: var(--bg-tertiary-dark);
}

.dark .table-row:hover {
  background: var(--bg-tertiary-dark);
}

.dark .table-loading-overlay {
  background: rgba(30, 30, 30, 0.8);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .table-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    max-width: none;
  }
  
  .table-pagination {
    flex-direction: column;
    gap: 1rem;
  }
  
  .pagination-controls {
    justify-content: center;
  }
}
</style>