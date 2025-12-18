<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";
import { useUserStore } from "@/stores/user";
import { setupRouterGuard, isLoggedIn } from "@/utils/auth";

onLaunch(() => {
  // 恢复登录状态
  const userStore = useUserStore();
  userStore.restoreLogin();

  // 设置路由拦截
  setupRouterGuard();

  // 检查登录状态
  if (!isLoggedIn()) {
    uni.reLaunch({ url: "/pages/login/index" });
  }
});

onShow(() => {});

onHide(() => {});
</script>

<style>
/* 全局样式 */
page {
  background-color: #f5f5f5;
  font-family:
    -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue",
    Arial, sans-serif;
}

/* 通用类 */
.text-primary {
  color: #1989fa;
}
.text-success {
  color: #07c160;
}
.text-warning {
  color: #fa8c16;
}
.text-danger {
  color: #ff4d4f;
}
.text-gray {
  color: #999999;
}
</style>
