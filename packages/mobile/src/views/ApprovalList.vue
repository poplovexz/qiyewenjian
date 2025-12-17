<template>
  <div class="approval-container">
    <van-nav-bar title="待我审批" fixed placeholder />

    <!-- 标签页 -->
    <van-tabs v-model:active="activeTab" @change="onTabChange" sticky>
      <van-tab title="请假申请" name="leave">
        <van-pull-refresh v-model="leaveRefreshing" @refresh="onLeaveRefresh">
          <van-list
            v-model:loading="leaveLoading"
            :finished="leaveFinished"
            finished-text="没有更多了"
            @load="loadLeaveList"
          >
            <div v-if="leaveList.length === 0" class="empty-container">
              <van-empty description="暂无待审批的请假申请" />
            </div>
            <div v-else class="approval-list">
              <div
                v-for="item in leaveList"
                :key="item.id"
                class="approval-item"
                @click="router.push(`/office/leave/${item.id}`)"
              >
                <div class="item-header">
                  <span class="item-title">{{ item.shenqing_ren_xingming }}</span>
                  <van-tag :type="getStatusType(item.shenhe_zhuangtai)">
                    {{ getStatusText(item.shenhe_zhuangtai) }}
                  </van-tag>
                </div>
                <div class="item-content">
                  <div class="item-row">
                    <span class="label">请假类型：</span>
                    <span>{{ item.qingjia_leixing }}</span>
                  </div>
                  <div class="item-row">
                    <span class="label">请假时间：</span>
                    <span>{{ formatDate(item.kaishi_shijian) }} 至 {{ formatDate(item.jieshu_shijian) }}</span>
                  </div>
                  <div class="item-row">
                    <span class="label">请假天数：</span>
                    <span>{{ item.qingjia_tianshu }} 天</span>
                  </div>
                </div>
                <div class="item-footer">
                  <span class="time">{{ formatDateTime(item.created_at) }}</span>
                </div>
              </div>
            </div>
          </van-list>
        </van-pull-refresh>
      </van-tab>

      <van-tab title="报销申请" name="reimbursement">
        <van-pull-refresh v-model="reimbursementRefreshing" @refresh="onReimbursementRefresh">
          <van-list
            v-model:loading="reimbursementLoading"
            :finished="reimbursementFinished"
            finished-text="没有更多了"
            @load="loadReimbursementList"
          >
            <div v-if="reimbursementList.length === 0" class="empty-container">
              <van-empty description="暂无待审批的报销申请" />
            </div>
            <div v-else class="approval-list">
              <div
                v-for="item in reimbursementList"
                :key="item.id"
                class="approval-item"
                @click="router.push(`/office/reimbursement/${item.id}`)"
              >
                <div class="item-header">
                  <span class="item-title">{{ item.shenqing_ren_xingming }}</span>
                  <van-tag :type="getStatusType(item.shenhe_zhuangtai)">
                    {{ getStatusText(item.shenhe_zhuangtai) }}
                  </van-tag>
                </div>
                <div class="item-content">
                  <div class="item-row">
                    <span class="label">报销类型：</span>
                    <span>{{ item.baoxiao_leixing }}</span>
                  </div>
                  <div class="item-row">
                    <span class="label">报销金额：</span>
                    <span class="amount">¥{{ item.baoxiao_jine }}</span>
                  </div>
                  <div class="item-row">
                    <span class="label">报销时间：</span>
                    <span>{{ formatDate(item.baoxiao_shijian) }}</span>
                  </div>
                </div>
                <div class="item-footer">
                  <span class="time">{{ formatDateTime(item.created_at) }}</span>
                </div>
              </div>
            </div>
          </van-list>
        </van-pull-refresh>
      </van-tab>
    </van-tabs>

    <van-tabbar v-model="active" fixed placeholder>
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="todo-list-o" to="/tasks">任务</van-tabbar-item>
      <van-tabbar-item icon="orders-o" to="/orders">工单</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { getLeaveList, type LeaveApplication } from '@/api/office'
import { getReimbursementList, type ReimbursementApplication } from '@/api/office'
import { formatDate, formatDateTime } from '@/utils/format'

const router = useRouter()
const active = ref(1)
const activeTab = ref('leave')

// 请假申请列表
const leaveList = ref<LeaveApplication[]>([])
const leaveLoading = ref(false)
const leaveFinished = ref(false)
const leaveRefreshing = ref(false)
const leavePage = ref(1)

// 报销申请列表
const reimbursementList = ref<ReimbursementApplication[]>([])
const reimbursementLoading = ref(false)
const reimbursementFinished = ref(false)
const reimbursementRefreshing = ref(false)
const reimbursementPage = ref(1)

// 加载请假申请列表
const loadLeaveList = async () => {
  try {
    const res = await getLeaveList({
      page: leavePage.value,
      size: 20,
      shenhe_zhuangtai: 'pending'  // 只查询待审批的
    })

    if (leavePage.value === 1) {
      leaveList.value = res.items
    } else {
      leaveList.value.push(...res.items)
    }

    leaveLoading.value = false
    leaveFinished.value = leavePage.value >= res.pages

    if (!leaveFinished.value) {
      leavePage.value++
    }
  } catch (error) {
    console.error('Load leave list error:', error)
    leaveLoading.value = false
    showToast({ message: '加载失败', type: 'fail' })
  }
}

// 加载报销申请列表
const loadReimbursementList = async () => {
  try {
    const res = await getReimbursementList({
      page: reimbursementPage.value,
      size: 20,
      shenhe_zhuangtai: 'pending'  // 只查询待审批的
    })

    if (reimbursementPage.value === 1) {
      reimbursementList.value = res.items
    } else {
      reimbursementList.value.push(...res.items)
    }

    reimbursementLoading.value = false
    reimbursementFinished.value = reimbursementPage.value >= res.pages

    if (!reimbursementFinished.value) {
      reimbursementPage.value++
    }
  } catch (error) {
    console.error('Load reimbursement list error:', error)
    reimbursementLoading.value = false
    showToast({ message: '加载失败', type: 'fail' })
  }
}

// 下拉刷新 - 请假
const onLeaveRefresh = async () => {
  leavePage.value = 1
  leaveFinished.value = false
  await loadLeaveList()
  leaveRefreshing.value = false
}

// 下拉刷新 - 报销
const onReimbursementRefresh = async () => {
  reimbursementPage.value = 1
  reimbursementFinished.value = false
  await loadReimbursementList()
  reimbursementRefreshing.value = false
}

// 切换标签页
const onTabChange = (name: string | number) => {
  if (name === 'leave' && leaveList.value.length === 0) {
    loadLeaveList()
  } else if (name === 'reimbursement' && reimbursementList.value.length === 0) {
    loadReimbursementList()
  }
}

// 获取状态类型
const getStatusType = (status?: string) => {
  switch (status) {
    case 'pending':
      return 'warning'
    case 'approved':
      return 'success'
    case 'rejected':
      return 'danger'
    default:
      return 'default'
  }
}

// 获取状态文本
const getStatusText = (status?: string) => {
  switch (status) {
    case 'pending':
      return '待审批'
    case 'approved':
      return '已通过'
    case 'rejected':
      return '已拒绝'
    default:
      return '未知'
  }
}

onMounted(() => {
  loadLeaveList()
})
</script>

<style scoped>
.approval-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f2f5 0%, #ffffff 100%);
  padding-bottom: 60px;
}

.empty-container {
  padding: 40px 0;
}

.approval-list {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.approval-item {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
}

.approval-item:active {
  transform: scale(0.98);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.item-title {
  font-size: 16px;
  font-weight: 500;
  color: #323233;
}

.item-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.item-row {
  display: flex;
  font-size: 14px;
  color: #646566;
}

.item-row .label {
  color: #969799;
  min-width: 80px;
}

.item-row .amount {
  color: #ee0a24;
  font-weight: 500;
}

.item-footer {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
  border-top: 1px solid #ebedf0;
}

.item-footer .time {
  font-size: 12px;
  color: #969799;
}
</style>

