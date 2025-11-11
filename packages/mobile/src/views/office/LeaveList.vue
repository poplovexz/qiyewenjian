<template>
  <div class="leave-list-container">
    <van-nav-bar title="请假申请" fixed placeholder>
      <template #right>
        <van-icon name="plus" size="20" @click="goToCreate" />
      </template>
    </van-nav-bar>

    <!-- 搜索栏 -->
    <van-search
      v-model="searchText"
      placeholder="搜索申请编号"
      @search="onSearch"
      @clear="onClear"
    />

    <!-- 筛选标签 -->
    <van-tabs v-model:active="activeTab" @change="onTabChange" sticky>
      <van-tab title="全部" name="" />
      <van-tab title="待审核" name="daishehe" />
      <van-tab title="审核中" name="shenhezhong" />
      <van-tab title="已通过" name="tongguo" />
      <van-tab title="已拒绝" name="jujue" />
    </van-tabs>

    <!-- 列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <div
          v-for="item in leaveList"
          :key="item.id"
          class="leave-item"
          @click="goToDetail(item.id!)"
        >
          <van-cell-group inset>
            <van-cell>
              <template #title>
                <div class="leave-title">
                  <span class="leave-number">{{ item.shenqing_bianhao }}</span>
                  <van-tag :type="getStatusType(item.shenhe_zhuangtai!)">
                    {{ getStatusText(item.shenhe_zhuangtai!) }}
                  </van-tag>
                </div>
              </template>
              <template #label>
                <div class="leave-info">
                  <div class="info-row">
                    <van-icon name="user-o" />
                    <span>{{ item.shenqing_ren_xingming || '-' }}</span>
                  </div>
                  <div class="info-row">
                    <van-icon name="label-o" />
                    <span>{{ getLeaveTypeText(item.qingjia_leixing) }}</span>
                  </div>
                  <div class="info-row">
                    <van-icon name="clock-o" />
                    <span>{{ formatDate(item.kaishi_shijian) }} 至 {{ formatDate(item.jieshu_shijian) }}</span>
                  </div>
                  <div class="info-row">
                    <van-icon name="calendar-o" />
                    <span>{{ item.qingjia_tianshu }} 天</span>
                  </div>
                  <div class="info-row reason">
                    <van-icon name="comment-o" />
                    <span>{{ item.qingjia_yuanyin }}</span>
                  </div>
                </div>
              </template>
            </van-cell>
          </van-cell-group>
        </div>

        <van-empty v-if="!loading && leaveList.length === 0" description="暂无请假申请" />
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { getLeaveList, type LeaveApplication } from '@/api/office'
import dayjs from 'dayjs'

const router = useRouter()

const searchText = ref('')
const activeTab = ref('')
const leaveList = ref<LeaveApplication[]>([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const page = ref(1)
const pageSize = 20

// 加载数据
const onLoad = async () => {
  try {
    const params: any = {
      page: page.value,
      size: pageSize
    }

    if (activeTab.value) {
      params.shenhe_zhuangtai = activeTab.value
    }

    if (searchText.value) {
      params.search = searchText.value
    }

    const res = await getLeaveList(params)

    if (page.value === 1) {
      leaveList.value = res.items
    } else {
      leaveList.value.push(...res.items)
    }

    loading.value = false

    if (leaveList.value.length >= res.total) {
      finished.value = true
    } else {
      page.value++
    }
  } catch (error) {
    console.error('Load leave list error:', error)
    loading.value = false
  }
}

// 下拉刷新
const onRefresh = () => {
  page.value = 1
  finished.value = false
  leaveList.value = []
  refreshing.value = false
  onLoad()
}

// 切换标签
const onTabChange = () => {
  page.value = 1
  finished.value = false
  leaveList.value = []
  onLoad()
}

// 搜索
const onSearch = () => {
  page.value = 1
  finished.value = false
  leaveList.value = []
  onLoad()
}

// 清除搜索
const onClear = () => {
  searchText.value = ''
  onSearch()
}

// 跳转到详情
const goToDetail = (id: string) => {
  router.push(`/office/leave/${id}`)
}

// 跳转到新建
const goToCreate = () => {
  router.push('/office/leave/create')
}

// 获取状态类型
const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    daishehe: 'default',
    shenhezhong: 'primary',
    tongguo: 'success',
    jujue: 'danger'
  }
  return map[status] || 'default'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    daishehe: '待审核',
    shenhezhong: '审核中',
    tongguo: '已通过',
    jujue: '已拒绝'
  }
  return map[status] || status
}

// 获取请假类型文本
const getLeaveTypeText = (type: string) => {
  const map: Record<string, string> = {
    shijia: '事假',
    bingjia: '病假',
    nianjia: '年假',
    tiaoxiu: '调休',
    hunjia: '婚假',
    chanjia: '产假',
    peichanjia: '陪产假',
    sangjia: '丧假'
  }
  return map[type] || type
}

// 格式化日期
const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD')
}
</script>

<style scoped>
.leave-list-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 20px;
}

.leave-item {
  margin-bottom: 12px;
  cursor: pointer;
}

.leave-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.leave-number {
  font-size: 16px;
  font-weight: 500;
  color: #323233;
}

.leave-info {
  margin-top: 8px;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
  font-size: 14px;
  color: #646566;
}

.info-row .van-icon {
  margin-right: 6px;
  color: #969799;
}

.info-row.reason {
  color: #969799;
  font-size: 13px;
}

.info-row.reason span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>

