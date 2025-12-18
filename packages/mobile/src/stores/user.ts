import { defineStore } from "pinia";
import { ref, computed } from "vue";

export interface UserInfo {
  id: string;
  yonghu_ming: string;
  xingming: string;
  youxiang?: string;
  shouji?: string;
  zhuangtai?: string;
  zuihou_denglu?: string;
  denglu_cishu?: string;
  roles?: string[]; // 用户角色列表
  permissions?: string[]; // 用户权限列表
}

export const useUserStore = defineStore(
  "user",
  () => {
    const token = ref<string>("");
    const userInfo = ref<UserInfo | null>(null);

    // 计算属性：用户角色列表
    const roles = computed(() => userInfo.value?.roles || []);

    // 计算属性：用户权限列表
    const permissions = computed(() => userInfo.value?.permissions || []);

    // 设置Token
    function setToken(newToken: string) {
      token.value = newToken;
    }

    // 设置用户信息
    function setUserInfo(info: UserInfo) {
      userInfo.value = info;
    }

    // 清除用户信息
    function clearUserInfo() {
      token.value = "";
      userInfo.value = null;
    }

    // 检查是否有指定权限
    function hasPermission(permission: string): boolean {
      if (!userInfo.value?.permissions) return false;
      // 超级管理员拥有所有权限
      if (userInfo.value.yonghu_ming === "admin") return true;
      return userInfo.value.permissions.includes(permission);
    }

    // 检查是否有任一权限
    function hasAnyPermission(permissionList: string[]): boolean {
      if (!userInfo.value?.permissions) return false;
      if (userInfo.value.yonghu_ming === "admin") return true;
      return permissionList.some((p) =>
        userInfo.value!.permissions!.includes(p),
      );
    }

    // 检查是否有所有权限
    function hasAllPermissions(permissionList: string[]): boolean {
      if (!userInfo.value?.permissions) return false;
      if (userInfo.value.yonghu_ming === "admin") return true;
      return permissionList.every((p) =>
        userInfo.value!.permissions!.includes(p),
      );
    }

    // 检查是否有指定角色
    function hasRole(role: string): boolean {
      if (!userInfo.value?.roles) return false;
      return userInfo.value.roles.includes(role);
    }

    // 检查是否有任一角色
    function hasAnyRole(roleList: string[]): boolean {
      if (!userInfo.value?.roles) return false;
      return roleList.some((r) => userInfo.value!.roles!.includes(r));
    }

    // 检查是否是管理员
    function isAdmin(): boolean {
      return userInfo.value?.yonghu_ming === "admin" || hasRole("admin");
    }

    // 登录
    async function login(username: string, password: string) {
      // 这里会在后面实现API调用
    }

    // 退出登录
    function logout() {
      clearUserInfo();
    }

    return {
      token,
      userInfo,
      roles,
      permissions,
      setToken,
      setUserInfo,
      clearUserInfo,
      hasPermission,
      hasAnyPermission,
      hasAllPermissions,
      hasRole,
      hasAnyRole,
      isAdmin,
      login,
      logout,
    };
  },
  {
    persist: true, // 持久化存储
  },
);
