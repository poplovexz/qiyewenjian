<template>
  <div class="reimbursement-list-container">
    <van-nav-bar title="报销申请" fixed placeholder>
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
          v-for="item in reimbursementList"
          :key="item.id"
          class="reimbursement-item"
          @click="goToDetail(item.id!)"
        >
          <van-cell-group inset>
            <van-cell>
              <template #title>
                <div class="reimbursement-title">
                  <span class="reimbursement-number">{{ item.shenqing_bianhao }}</span>
                  <van-tag :type="getStatusType(item.shenhe_zhuangtai!)">
                    {{ getStatusText(item.shenhe_zhuangtai!) }}
                  </van-tag>
                </div>
              </template>
              <template #label>
                <div class="reimbursement-info">
                  <div class="info-row">
                    <van-icon name="user-o" />
                    <span>{{ item.shenqing_ren_xingming || '-' }}</span>
                  </div>
                  <div class="info-row">
                    <van-icon name="label-o" />
                    <span>{{ getReimbursementTypeText(item.baoxiao_leixing) }}</span>
                  </div>
                  <div class="info-row amount">
                    <van-icon name="gold-coin-o" />
                    <span class="amount-text">¥{{ item.baoxiao_jine.toFixed(2) }}</span>
                  </div>
                  <div class="info-row">
                    <van-icon name="clock-o" />
                    <span>{{ formatDate(item.baoxiao_shijian) }}</span>
                  </div>
                  <div class="info-row reason">
                    <van-icon name="comment-o" />
                    <span>{{ item.baoxiao_yuanyin }}</span>
                  </div>
                </div>
              </template>
            </van-cell>
          </van-cell-group>
        </div>

        <van-empty v-if="!loading && reimbursementList.length === 0" description="暂无报销申请" />
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { getReimbursementList, type ReimbursementApplication } from '@/api/office'
import dayjs from 'dayjs'

const router = useRouter()

const searchText = ref('')
const activeTab = ref('')
const reimbursementList = ref<ReimbursementApplication[]>([])
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

    const res = await getReimbursementList(params)

    if (page.value === 1) {
      reimbursementList.value = res.items
    } else {
      reimbursementList.value.push(...res.items)
    }

    loading.value = false

    if (reimbursementList.value.length >= res.total) {
      finished.value = true
    } else {
      page.value++
    }
  } catch (error) {
    console.error('Load reimbursement list error:', error)
    loading.value = false
  }
}

// 下拉刷新
const onRefresh = () => {
  page.value = 1
  finished.value = false
  reimbursementList.value = []
  refreshing.value = false
  onLoad()
}

// 切换标签
const onTabChange = () => {
  page.value = 1
  finished.value = false
  reimbursementList.value = []
  onLoad()
}

// 搜索
const onSearch = () => {
  page.value = 1
  finished.value = false
  reimbursementList.value = []
  onLoad()
}

// 清除搜索
const onClear = () => {
  searchText.value = ''
  onSearch()
}

// 跳转到详情
const goToDetail = (id: string) => {
  router.push(`/office/reimbursement/${id}`)
}

// 跳转到新建
const goToCreate = () => {
  router.push('/office/reimbursement/create')
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

// 获取报销类型文本
const getReimbursementTypeText = (type: string) => {
  const map: Record<string, string> = {
    chailvfei: '差旅费',
    canyinfei: '餐饮费',
    jiaotongfei: '交通费',
    banggongyongpin: '办公用品',
    qita: '其他'
  }
  return map[type] || type
}

// 格式化日期
const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD')
}
</script>

<style scoped>
.reimbursement-list-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 20px;
}

.reimbursement-item {
  margin-bottom: 12px;
  cursor: pointer;
}

.reimbursement-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.reimbursement-number {
  font-size: 16px;
  font-weight: 500;
  color: #323233;
}

.reimbursement-info {
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

.info-row.amount {
  color: #ee0a24;
  font-weight: 500;
}

.amount-text {
  font-size: 16px;
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

