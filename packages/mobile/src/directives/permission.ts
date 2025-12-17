/**
 * 权限指令
 * 用法：v-permission="'office:baoxiao:approve'"
 * 或：v-permission="['office:baoxiao:approve', 'office:qingjia:approve']"
 */
import type { Directive, DirectiveBinding } from 'vue'
import { useUserStore } from '@/stores/user'

export const permission: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding) {
    const userStore = useUserStore()
    const value = binding.value

    if (!value) {
      console.warn('v-permission directive requires a permission string or array')
      return
    }

    let hasPermission = false

    if (typeof value === 'string') {
      // 单个权限
      hasPermission = userStore.hasPermission(value)
    } else if (Array.isArray(value)) {
      // 权限数组，满足任一即可
      hasPermission = userStore.hasAnyPermission(value)
    } else {
      console.warn('v-permission directive value must be a string or array')
      return
    }

    if (!hasPermission) {
      // 没有权限，移除元素
      el.parentNode?.removeChild(el)
    }
  }
}

/**
 * 角色指令
 * 用法：v-role="'admin'"
 * 或：v-role="['admin', 'manager']"
 */
export const role: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding) {
    const userStore = useUserStore()
    const value = binding.value

    if (!value) {
      console.warn('v-role directive requires a role string or array')
      return
    }

    let hasRole = false

    if (typeof value === 'string') {
      // 单个角色
      hasRole = userStore.hasRole(value)
    } else if (Array.isArray(value)) {
      // 角色数组，满足任一即可
      hasRole = userStore.hasAnyRole(value)
    } else {
      console.warn('v-role directive value must be a string or array')
      return
    }

    if (!hasRole) {
      // 没有角色，移除元素
      el.parentNode?.removeChild(el)
    }
  }
}

