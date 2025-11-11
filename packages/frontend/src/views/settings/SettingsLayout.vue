<template>
  <div class="settings-layout">
    <div class="settings-sidebar">
      <el-menu
        :default-active="activeMenu"
        class="settings-menu"
        @select="handleMenuSelect"
      >
        <el-menu-item-group title="个人设置">
          <el-menu-item index="/settings/profile">
            <el-icon><User /></el-icon>
            <span>个人信息</span>
          </el-menu-item>
          <el-menu-item index="/settings/password">
            <el-icon><Lock /></el-icon>
            <span>修改密码</span>
          </el-menu-item>
          <el-menu-item index="/settings/notifications">
            <el-icon><Bell /></el-icon>
            <span>通知偏好</span>
          </el-menu-item>
        </el-menu-item-group>

        <!-- 系统设置（仅管理员可见） -->
        <el-menu-item-group v-if="isAdmin" title="系统设置">
          <el-menu-item index="/settings/system/basic">
            <el-icon><Setting /></el-icon>
            <span>基础信息</span>
          </el-menu-item>
          <el-menu-item index="/settings/system/security">
            <el-icon><Lock /></el-icon>
            <span>安全配置</span>
          </el-menu-item>
          <el-menu-item index="/settings/system/business">
            <el-icon><Document /></el-icon>
            <span>业务参数</span>
          </el-menu-item>
        </el-menu-item-group>
      </el-menu>
    </div>

    <div class="settings-content">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { User, Lock, Bell, Setting, Document } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 当前激活的菜单
const activeMenu = ref(route.path)

// 是否是管理员（TODO: 从用户权限中获取）
const isAdmin = computed(() => {
  // 这里应该从用户权限中判断
  return true
})

// 监听路由变化
watch(() => route.path, (newPath) => {
  activeMenu.value = newPath
})

// 菜单选择处理
const handleMenuSelect = (index: string) => {
  router.push(index)
}
</script>

<style scoped lang="scss">
.settings-layout {
  display: flex;
  height: calc(100vh - 60px);
  background-color: #f5f7fa;
}

.settings-sidebar {
  width: 240px;
  background-color: #fff;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;

  .settings-menu {
    border-right: none;
    padding: 20px 0;

    :deep(.el-menu-item-group__title) {
      padding: 15px 20px 10px;
      font-size: 12px;
      color: #909399;
      font-weight: 600;
    }

    :deep(.el-menu-item) {
      height: 44px;
      line-height: 44px;
      margin: 4px 12px;
      border-radius: 6px;

      &:hover {
        background-color: #f5f7fa;
      }

      &.is-active {
        background-color: #ecf5ff;
        color: #409eff;
      }

      .el-icon {
        margin-right: 8px;
      }
    }
  }
}

.settings-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
</style>

