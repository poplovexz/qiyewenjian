<template>
  <div class="permission-auto-import">
    <el-card class="header-card">
      <div class="header">
        <div class="title">
          <el-icon><MagicStick /></el-icon>
          <h2>权限自动识别与导入</h2>
        </div>
        <div class="description">自动扫描系统路由和API，识别所有权限并一键导入</div>
      </div>
    </el-card>

    <el-row :gutter="20">
      <!-- 左侧：扫描控制 -->
      <el-col :span="8">
        <el-card class="scan-card">
          <template #header>
            <div class="card-header">
              <el-icon><Search /></el-icon>
              <span>扫描设置</span>
            </div>
          </template>

          <el-form label-width="100px">
            <el-form-item label="扫描范围">
              <el-checkbox-group v-model="scanOptions">
                <el-checkbox label="routes">前端路由</el-checkbox>
                <el-checkbox label="api">后端API</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="默认状态">
              <el-radio-group v-model="defaultStatus">
                <el-radio label="active">启用</el-radio>
                <el-radio label="inactive">禁用</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                :icon="Search"
                @click="scanPermissions"
                :loading="scanning"
                style="width: 100%"
              >
                开始扫描
              </el-button>
            </el-form-item>
          </el-form>

          <el-divider />

          <div class="stats">
            <div class="stat-item">
              <div class="stat-label">已扫描</div>
              <div class="stat-value">{{ scannedPermissions.length }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">已选择</div>
              <div class="stat-value">{{ selectedPermissions.length }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">已导入</div>
              <div class="stat-value">{{ importedCount }}</div>
            </div>
          </div>

          <el-button
            type="success"
            :icon="Upload"
            @click="importPermissions"
            :disabled="selectedPermissions.length === 0"
            :loading="importing"
            style="width: 100%; margin-top: 20px"
          >
            批量导入 ({{ selectedPermissions.length }})
          </el-button>
        </el-card>
      </el-col>

      <!-- 右侧：扫描结果 -->
      <el-col :span="16">
        <el-card class="result-card">
          <template #header>
            <div class="card-header">
              <div>
                <el-icon><List /></el-icon>
                <span>扫描结果</span>
              </div>
              <div>
                <el-button
                  size="small"
                  @click="selectAll"
                  :disabled="scannedPermissions.length === 0"
                >
                  全选
                </el-button>
                <el-button
                  size="small"
                  @click="selectNone"
                  :disabled="scannedPermissions.length === 0"
                >
                  取消全选
                </el-button>
              </div>
            </div>
          </template>

          <el-empty
            v-if="scannedPermissions.length === 0"
            description="点击开始扫描按钮扫描系统权限"
          />

          <el-table
            v-else
            :data="scannedPermissions"
            style="width: 100%"
            max-height="600"
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="quanxian_ming" label="权限名称" min-width="150" />
            <el-table-column prop="quanxian_bianma" label="权限编码" min-width="150" />
            <el-table-column prop="ziyuan_leixing" label="资源类型" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.ziyuan_leixing === 'menu'" type="primary" size="small">
                  菜单
                </el-tag>
                <el-tag v-else-if="row.ziyuan_leixing === 'button'" type="success" size="small">
                  按钮
                </el-tag>
                <el-tag v-else type="info" size="small"> 接口 </el-tag>
              </template>
            </el-table-column>
            <el-table-column
              prop="ziyuan_lujing"
              label="资源路径"
              min-width="200"
              show-overflow-tooltip
            />
            <el-table-column prop="miaoshu" label="描述" min-width="200" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MagicStick, Search, Upload, List } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { permissionAPI } from '@/api/modules/permission'

const router = useRouter()

// 响应式数据
const scanning = ref(false)
const importing = ref(false)
const scanOptions = ref(['routes', 'api'])
const defaultStatus = ref('active')
const scannedPermissions = ref<any[]>([])
const selectedPermissions = ref<any[]>([])
const importedCount = ref(0)

// 权限名称映射
const permissionNameMap: Record<string, string> = {
  'user:read': '查看用户',
  'user:create': '创建用户',
  'user:update': '编辑用户',
  'user:delete': '删除用户',
  'role:read': '查看角色',
  'role:create': '创建角色',
  'role:update': '编辑角色',
  'role:delete': '删除角色',
  'permission:read': '查看权限',
  'permission:create': '创建权限',
  'permission:update': '编辑权限',
  'permission:delete': '删除权限',
  'customer:read': '查看客户',
  'customer:create': '创建客户',
  'customer:update': '编辑客户',
  'customer:delete': '删除客户',
  'service_record:read': '查看服务记录',
  'product_category:read': '查看产品分类',
  'product:read': '查看产品',
  'xiansuo:read': '查看线索',
  'xiansuo:source_read': '查看线索来源',
  'xiansuo:status_read': '查看线索状态',
  contract_manage: '管理合同',
  contract_template_manage: '管理合同模板',
  audit_manage: '管理审核',
  audit_config: '配置审核',
  'audit_record:read': '查看审核记录',
  finance_manage: '管理财务',
  'invoice:read': '查看开票',
  'invoice:create': '创建开票',
  'invoice:update': '编辑开票',
  'cost:read': '查看成本',
  'cost:create': '创建成本',
  'cost:update': '编辑成本',
  'service_order:read': '查看服务工单',
  'service_order:write': '编辑服务工单',
  'compliance:read': '查看合规',
  'compliance:manage': '管理合规',
}

// 权限项类型
interface PermissionItem {
  quanxian_ming: string
  quanxian_bianma: string
  miaoshu: string
  ziyuan_leixing: string
  ziyuan_lujing: string
  zhuangtai: string
}

// 扫描权限
const scanPermissions = () => {
  scanning.value = true
  scannedPermissions.value = []

  try {
    const permissions: PermissionItem[] = []
    const permissionSet = new Set<string>()

    // 扫描路由
    if (scanOptions.value.includes('routes')) {
      const routes = router.getRoutes()

      routes.forEach((route) => {
        if (route.meta?.permissions && Array.isArray(route.meta.permissions)) {
          route.meta.permissions.forEach((perm: string) => {
            if (!permissionSet.has(perm)) {
              permissionSet.add(perm)

              const permission = {
                quanxian_ming: permissionNameMap[perm] || perm,
                quanxian_bianma: perm,
                miaoshu: `${permissionNameMap[perm] || perm}的权限`,
                ziyuan_leixing: 'menu',
                ziyuan_lujing: route.path,
                zhuangtai: defaultStatus.value,
              }

              permissions.push(permission)
            }
          })
        }
      })
    }

    scannedPermissions.value = permissions
    ElMessage.success(`扫描完成，发现 ${permissions.length} 个权限`)
  } catch (error) {
    console.error('扫描失败:', error)
    ElMessage.error('扫描失败')
  } finally {
    scanning.value = false
  }
}

// 处理选择变化
const handleSelectionChange = (selection: PermissionItem[]) => {
  selectedPermissions.value = selection
}

// 全选
const selectAll = () => {
  selectedPermissions.value = [...scannedPermissions.value]
}

// 取消全选
const selectNone = () => {
  selectedPermissions.value = []
}

// 批量导入权限
const importPermissions = async () => {
  if (selectedPermissions.value.length === 0) {
    ElMessage.warning('请先选择要导入的权限')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要导入 ${selectedPermissions.value.length} 个权限吗？`,
      '确认导入',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    importing.value = true
    let successCount = 0
    let failCount = 0
    const failedPermissions: string[] = []

    for (const permission of selectedPermissions.value) {
      try {
        await permissionAPI.createPermission(permission)
        successCount++
      } catch (error: unknown) {
        const axiosError = error as { response?: { data?: { detail?: string } }; message?: string }
        console.error(`❌ 导入权限失败: ${permission.quanxian_bianma}`, error)
        console.error('错误详情:', axiosError.response?.data)

        if (axiosError.response?.data?.detail?.includes('已存在')) {
          // 权限已存在，不算失败
          successCount++
          console.log(`⚠️ 权限已存在，跳过: ${permission.quanxian_bianma}`)
        } else {
          failCount++
          failedPermissions.push(
            `${permission.quanxian_ming} (${permission.quanxian_bianma}): ${axiosError.response?.data?.detail || axiosError.message}`
          )
        }
      }
    }

    importedCount.value += successCount

    if (failCount === 0) {
      ElMessage.success({
        message: `成功导入 ${successCount} 个权限！请返回权限管理页面刷新查看`,
        duration: 5000,
      })

      // 提示用户刷新权限列表页面
      ElMessageBox.alert(
        '权限导入成功！请切换到权限管理页面并刷新页面（按F5）查看导入的权限。',
        '导入完成',
        {
          confirmButtonText: '我知道了',
          type: 'success',
        }
      )
    } else {
      ElMessage.warning({
        message: `成功导入 ${successCount} 个权限，失败 ${failCount} 个。请查看控制台了解详情`,
        duration: 5000,
      })

      // 显示失败详情
      const failedList = failedPermissions.join('\n')
      ElMessageBox.alert(
        `导入完成！\n\n成功: ${successCount} 个\n失败: ${failCount} 个\n\n失败的权限:\n${failedList}\n\n请打开浏览器控制台（F12）查看详细错误信息。`,
        '导入结果',
        {
          confirmButtonText: '我知道了',
          type: 'warning',
        }
      )
    }

    // 清空选择
    selectedPermissions.value = []
  } catch (error) {
    if (error !== 'cancel') {
      console.error('导入失败:', error)
      ElMessage.error('导入失败')
    }
  } finally {
    importing.value = false
  }
}
</script>

<style scoped lang="scss">
.permission-auto-import {
  padding: 20px;

  .header-card {
    margin-bottom: 20px;

    .header {
      .title {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;

        h2 {
          margin: 0;
          font-size: 24px;
        }
      }

      .description {
        color: #666;
        font-size: 14px;
      }
    }
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;

    > div {
      display: flex;
      align-items: center;
      gap: 10px;
    }
  }

  .stats {
    display: flex;
    justify-content: space-around;
    margin-top: 20px;

    .stat-item {
      text-align: center;

      .stat-label {
        font-size: 12px;
        color: #999;
        margin-bottom: 5px;
      }

      .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #409eff;
      }
    }
  }
}
</style>
