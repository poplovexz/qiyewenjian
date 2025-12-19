<template>
  <div class="compliance-calendar">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>合规日历</h2>
        <p class="subtitle">税务申报、年报等合规事项日历视图</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建合规事项
        </el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card" shadow="never">
      <div class="filter-row">
        <div class="filter-item">
          <label>年份：</label>
          <el-date-picker
            v-model="currentYear"
            type="year"
            placeholder="选择年份"
            format="YYYY"
            value-format="YYYY"
            @change="handleYearChange"
          />
        </div>

        <div class="filter-item">
          <label>月份：</label>
          <el-select
            v-model="currentMonth"
            placeholder="选择月份（可选）"
            clearable
            @change="handleMonthChange"
          >
            <el-option
              v-for="month in monthOptions"
              :key="month.value"
              :label="month.label"
              :value="month.value"
            />
          </el-select>
        </div>

        <div class="filter-item">
          <label>客户：</label>
          <el-select
            v-model="selectedCustomer"
            placeholder="选择客户（可选）"
            filterable
            clearable
            @change="handleCustomerChange"
          >
            <el-option
              v-for="customer in customers"
              :key="customer.id"
              :label="customer.gongsi_mingcheng"
              :value="customer.id"
            />
          </el-select>
        </div>

        <div class="filter-item">
          <label>事项类型：</label>
          <el-select
            v-model="selectedType"
            placeholder="选择事项类型（可选）"
            clearable
            @change="handleTypeChange"
          >
            <el-option
              v-for="(label, value) in complianceStore.templateTypeMap"
              :key="value"
              :label="label"
              :value="value"
            />
          </el-select>
        </div>

        <div class="filter-item">
          <el-button type="primary" @click="loadCalendarData">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="resetFilters">重置</el-button>
        </div>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <div class="stats-cards" v-if="calendarData">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ calendarData.summary.total_count }}</div>
              <div class="stat-label">总事项数</div>
            </div>
            <el-icon class="stat-icon total"><Calendar /></el-icon>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ calendarData.summary.completed_count }}</div>
              <div class="stat-label">已完成</div>
            </div>
            <el-icon class="stat-icon completed"><CircleCheck /></el-icon>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ calendarData.summary.overdue_count }}</div>
              <div class="stat-label">已逾期</div>
            </div>
            <el-icon class="stat-icon overdue"><Warning /></el-icon>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ calendarData.summary.completion_rate }}%</div>
              <div class="stat-label">完成率</div>
            </div>
            <el-icon class="stat-icon rate"><TrendCharts /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 日历视图 -->
    <el-card class="calendar-card" shadow="never" v-loading="complianceStore.loading">
      <template #header>
        <div class="calendar-header">
          <span>{{ calendarData?.summary.period || '合规日历' }}</span>
          <div class="view-controls">
            <el-radio-group v-model="viewMode" @change="handleViewModeChange">
              <el-radio-button label="month">月视图</el-radio-button>
              <el-radio-button label="year">年视图</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>

      <!-- 月视图 -->
      <div v-if="viewMode === 'month' && calendarData" class="month-view">
        <el-calendar v-model="calendarValue">
          <template #date-cell="{ data }">
            <div class="calendar-cell">
              <div class="date-number">{{ data.day.split('-').pop() }}</div>
              <div class="compliance-items" v-if="getItemsForDate(data.day).length > 0">
                <div
                  v-for="item in getItemsForDate(data.day).slice(0, 3)"
                  :key="item.id"
                  :class="['compliance-item', getItemStatusClass(item)]"
                  @click="showItemDetail(item)"
                >
                  <span class="item-title">{{ item.shili_mingcheng }}</span>
                  <span class="item-customer">{{ item.kehu_mingcheng }}</span>
                </div>
                <div
                  v-if="getItemsForDate(data.day).length > 3"
                  class="more-items"
                  @click="showMoreItems(data.day)"
                >
                  +{{ getItemsForDate(data.day).length - 3 }} 更多
                </div>
              </div>
            </div>
          </template>
        </el-calendar>
      </div>

      <!-- 年视图 -->
      <div v-if="viewMode === 'year' && calendarData" class="year-view">
        <div class="year-grid">
          <div v-for="month in 12" :key="month" class="month-card" @click="selectMonth(month)">
            <div class="month-header">
              <h4>{{ month }}月</h4>
              <span class="month-stats">{{ getMonthStats(month) }}</span>
            </div>
            <div class="month-items">
              <div
                v-for="item in getMonthItems(month).slice(0, 5)"
                :key="item.id"
                :class="['month-item', getItemStatusClass(item)]"
              >
                <span class="item-date">{{ formatDate(item.jihua_jieshu_shijian) }}</span>
                <span class="item-name">{{ item.shili_mingcheng }}</span>
              </div>
              <div v-if="getMonthItems(month).length > 5" class="more-month-items">
                +{{ getMonthItems(month).length - 5 }} 更多
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 即将到期事项 -->
    <el-card class="upcoming-card" shadow="never">
      <template #header>
        <span>即将到期事项</span>
      </template>
      <div v-if="upcomingItems.length === 0" class="empty-state">
        <el-empty description="暂无即将到期的合规事项" />
      </div>
      <div v-else class="upcoming-list">
        <div
          v-for="item in upcomingItems"
          :key="item.id"
          :class="['upcoming-item', getItemStatusClass(item)]"
          @click="showItemDetail(item)"
        >
          <div class="item-info">
            <div class="item-title">{{ item.shili_mingcheng }}</div>
            <div class="item-meta">
              <span class="customer">{{ item.kehu_mingcheng }}</span>
              <span class="type">{{ complianceStore.templateTypeMap[item.shixiang_leixing] }}</span>
            </div>
          </div>
          <div class="item-deadline">
            <div class="days-remaining">{{ item.days_remaining }}天后到期</div>
            <div class="deadline-date">{{ formatDate(item.jihua_jieshu_shijian) }}</div>
          </div>
          <div class="item-status">
            <el-tag :type="getStatusTagType(item.status_info.urgency)">
              {{ item.status_info.message }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search, Calendar, CircleCheck, Warning, TrendCharts } from '@element-plus/icons-vue'
import { useComplianceStore } from '@/stores/modules/complianceManagement'
import { format } from 'date-fns'

// Store
const complianceStore = useComplianceStore()

// 响应式数据
const currentYear = ref(new Date().getFullYear().toString())
const currentMonth = ref<number | null>(null)
const selectedCustomer = ref('')
const selectedType = ref('')
const viewMode = ref('month')
const calendarValue = ref(new Date())
const showCreateDialog = ref(false)

const calendarData = ref(null)
const upcomingItems = ref([])
const customers = ref([])

// 计算属性
const monthOptions = computed(() => {
  return Array.from({ length: 12 }, (_, i) => ({
    value: i + 1,
    label: `${i + 1}月`,
  }))
})

// 方法
const loadCalendarData = async () => {
  try {
    const year = parseInt(currentYear.value)
    const data = await complianceStore.fetchCalendarData(
      year,
      currentMonth.value || undefined,
      selectedCustomer.value || undefined,
      selectedType.value || undefined
    )
    calendarData.value = data
  } catch (error) {
  }
}

const loadUpcomingItems = async () => {
  try {
    const items = await complianceStore.fetchUpcomingItems(7, selectedCustomer.value || undefined)
    upcomingItems.value = items
  } catch (error) {
  }
}

const loadCustomers = async () => {
  try {
    // 这里应该调用客户管理的API
    // customers.value = await customerStore.fetchCustomers()
    customers.value = [] // 临时空数组
  } catch (error) {
  }
}

// 合规事项类型
interface ComplianceCalendarItem {
  id: string
  status_info?: { status?: string; urgency?: string; message?: string }
  shili_zhuangtai?: string
}

const getItemsForDate = (date: string) => {
  if (!calendarData.value?.calendar_data) return []
  return calendarData.value.calendar_data[date] || []
}

const getItemStatusClass = (item: ComplianceCalendarItem) => {
  const status = item.status_info?.status || item.shili_zhuangtai
  return `status-${status}`
}

const getStatusTagType = (urgency: string) => {
  const typeMap = {
    critical: 'danger',
    urgent: 'danger',
    high: 'warning',
    medium: 'primary',
    low: 'info',
    none: 'success',
  }
  return typeMap[urgency] || 'info'
}

const getMonthStats = (month: number) => {
  if (!calendarData.value?.calendar_data) return '0项'

  let count = 0
  Object.keys(calendarData.value.calendar_data).forEach((date) => {
    const dateObj = new Date(date)
    if (dateObj.getMonth() + 1 === month) {
      count += calendarData.value.calendar_data[date].length
    }
  })

  return `${count}项`
}

const getMonthItems = (month: number) => {
  if (!calendarData.value?.calendar_data) return []

  const items = []
  Object.keys(calendarData.value.calendar_data).forEach((date) => {
    const dateObj = new Date(date)
    if (dateObj.getMonth() + 1 === month) {
      items.push(...calendarData.value.calendar_data[date])
    }
  })

  return items.sort(
    (a, b) =>
      new Date(a.jihua_jieshu_shijian).getTime() - new Date(b.jihua_jieshu_shijian).getTime()
  )
}

const formatDate = (dateString: string) => {
  return format(new Date(dateString), 'MM-dd')
}

const handleYearChange = () => {
  loadCalendarData()
}

const handleMonthChange = () => {
  if (currentMonth.value) {
    viewMode.value = 'month'
    calendarValue.value = new Date(parseInt(currentYear.value), currentMonth.value - 1, 1)
  }
  loadCalendarData()
}

const handleCustomerChange = () => {
  loadCalendarData()
  loadUpcomingItems()
}

const handleTypeChange = () => {
  loadCalendarData()
}

const handleViewModeChange = () => {
  if (viewMode.value === 'year') {
    currentMonth.value = null
    loadCalendarData()
  }
}

const selectMonth = (month: number) => {
  currentMonth.value = month
  viewMode.value = 'month'
  calendarValue.value = new Date(parseInt(currentYear.value), month - 1, 1)
  loadCalendarData()
}

const resetFilters = () => {
  currentYear.value = new Date().getFullYear().toString()
  currentMonth.value = null
  selectedCustomer.value = ''
  selectedType.value = ''
  viewMode.value = 'month'
  calendarValue.value = new Date()
  loadCalendarData()
  loadUpcomingItems()
}

const showItemDetail = (item: ComplianceCalendarItem) => {
  // 显示合规事项详情
}

const showMoreItems = (date: string) => {
  // 显示更多事项
}

// 生命周期
onMounted(() => {
  loadCalendarData()
  loadUpcomingItems()
  loadCustomers()
})
</script>

<style scoped>
.compliance-calendar {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left h2 {
  margin: 0 0 5px 0;
  color: #303133;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-item label {
  font-weight: 500;
  color: #606266;
  white-space: nowrap;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  position: relative;
  overflow: hidden;
}

.stat-content {
  position: relative;
  z-index: 2;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.stat-icon {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 40px;
  opacity: 0.1;
}

.calendar-card {
  margin-bottom: 20px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.calendar-cell {
  height: 100px;
  padding: 4px;
  position: relative;
}

.date-number {
  font-weight: bold;
  margin-bottom: 4px;
}

.compliance-items {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.compliance-item {
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.compliance-item:hover {
  transform: scale(1.02);
}

.status-completed {
  background-color: #f0f9ff;
  border-left: 3px solid #67c23a;
}

.status-overdue {
  background-color: #fef0f0;
  border-left: 3px solid #f56c6c;
}

.status-due_today {
  background-color: #fdf6ec;
  border-left: 3px solid #e6a23c;
}

.status-due_soon {
  background-color: #f4f4f5;
  border-left: 3px solid #909399;
}

.item-title {
  display: block;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-customer {
  display: block;
  color: #909399;
  font-size: 11px;
}

.more-items {
  padding: 2px 4px;
  background-color: #f5f7fa;
  border-radius: 3px;
  font-size: 11px;
  color: #606266;
  cursor: pointer;
  text-align: center;
}

.year-view {
  padding: 20px 0;
}

.year-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.month-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.month-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.month-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.month-header h4 {
  margin: 0;
  color: #303133;
}

.month-stats {
  color: #909399;
  font-size: 14px;
}

.month-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.month-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13px;
}

.item-date {
  color: #909399;
  font-size: 12px;
}

.item-name {
  flex: 1;
  margin-left: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.upcoming-card {
  margin-bottom: 20px;
}

.upcoming-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.upcoming-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.upcoming-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.item-info {
  flex: 1;
}

.item-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.item-meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: #909399;
}

.item-deadline {
  text-align: center;
  margin: 0 20px;
}

.days-remaining {
  font-weight: 500;
  color: #303133;
}

.deadline-date {
  font-size: 13px;
  color: #909399;
  margin-top: 2px;
}

.item-status {
  min-width: 100px;
  text-align: right;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}
</style>
