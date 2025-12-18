<template>
  <div class="leave-form-container">
    <van-nav-bar
      :title="isEdit ? '编辑请假申请' : '新建请假申请'"
      left-arrow
      fixed
      placeholder
      @click-left="onBack"
    />

    <van-form @submit="onSubmit">
      <!-- 请假类型 -->
      <van-cell-group inset title="基本信息">
        <van-field
          v-model="formData.qingjia_leixing_text"
          label="请假类型"
          placeholder="请选择请假类型"
          readonly
          required
          right-icon="arrow"
          @click="showLeaveTypePicker = true"
        />

        <!-- 开始时间 -->
        <van-field
          v-model="formData.kaishi_shijian_text"
          label="开始时间"
          placeholder="请选择开始时间"
          readonly
          required
          right-icon="arrow"
          @click="showStartTimePicker = true"
        />

        <!-- 结束时间 -->
        <van-field
          v-model="formData.jieshu_shijian_text"
          label="结束时间"
          placeholder="请选择结束时间"
          readonly
          required
          right-icon="arrow"
          @click="showEndTimePicker = true"
        />

        <!-- 请假天数 -->
        <van-field
          v-model="formData.qingjia_tianshu"
          label="请假天数"
          type="number"
          placeholder="自动计算"
          readonly
          required
        />
      </van-cell-group>

      <!-- 请假原因 -->
      <van-cell-group inset title="请假原因">
        <van-field
          v-model="formData.qingjia_yuanyin"
          type="textarea"
          placeholder="请输入请假原因"
          rows="4"
          maxlength="500"
          show-word-limit
          required
        />
      </van-cell-group>

      <!-- 附件上传 -->
      <van-cell-group inset title="附件（选填）">
        <van-field label="上传附件">
          <template #input>
            <van-uploader
              v-model="fileList"
              :max-count="5"
              :after-read="afterRead"
              :before-delete="beforeDelete"
            />
          </template>
        </van-field>
      </van-cell-group>

      <!-- 备注 -->
      <van-cell-group inset title="备注（选填）">
        <van-field
          v-model="formData.beizhu"
          type="textarea"
          placeholder="请输入备注信息"
          rows="3"
          maxlength="200"
          show-word-limit
        />
      </van-cell-group>

      <!-- 提交按钮 -->
      <div class="submit-buttons">
        <van-button round block type="default" @click="onSaveDraft">
          保存草稿
        </van-button>
        <van-button
          round
          block
          type="primary"
          native-type="submit"
          :loading="submitting"
        >
          提交申请
        </van-button>
      </div>
    </van-form>

    <!-- 请假类型选择器 -->
    <van-popup v-model:show="showLeaveTypePicker" position="bottom" round>
      <van-picker
        :columns="leaveTypeOptions"
        @confirm="onLeaveTypeConfirm"
        @cancel="showLeaveTypePicker = false"
      />
    </van-popup>

    <!-- 开始时间选择器 -->
    <van-popup v-model:show="showStartTimePicker" position="bottom" round>
      <van-datetime-picker
        v-model="startTime"
        type="datetime"
        title="选择开始时间"
        @confirm="onStartTimeConfirm"
        @cancel="showStartTimePicker = false"
      />
    </van-popup>

    <!-- 结束时间选择器 -->
    <van-popup v-model:show="showEndTimePicker" position="bottom" round>
      <van-datetime-picker
        v-model="endTime"
        type="datetime"
        title="选择结束时间"
        :min-date="startTime"
        @confirm="onEndTimeConfirm"
        @cancel="showEndTimePicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { showToast, showConfirmDialog } from "vant";
import {
  getLeaveDetail,
  createLeave,
  updateLeave,
  type LeaveApplication,
} from "@/api/office";
import dayjs from "dayjs";
import type { UploaderFileListItem } from "vant";

const router = useRouter();
const route = useRoute();

const isEdit = computed(() => Boolean(route.params.id));
const leaveId = computed(() => route.params.id as string);

const formData = ref({
  qingjia_leixing: "",
  qingjia_leixing_text: "",
  kaishi_shijian: "",
  kaishi_shijian_text: "",
  jieshu_shijian: "",
  jieshu_shijian_text: "",
  qingjia_tianshu: 0,
  qingjia_yuanyin: "",
  fujian_lujing: "",
  beizhu: "",
});

const fileList = ref<UploaderFileListItem[]>([]);
const submitting = ref(false);
const showLeaveTypePicker = ref(false);
const showStartTimePicker = ref(false);
const showEndTimePicker = ref(false);
const startTime = ref(new Date());
const endTime = ref(new Date());

// 请假类型选项
const leaveTypeOptions = [
  { text: "事假", value: "shijia" },
  { text: "病假", value: "bingjia" },
  { text: "年假", value: "nianjia" },
  { text: "调休", value: "tiaoxiu" },
  { text: "婚假", value: "hunjia" },
  { text: "产假", value: "chanjia" },
  { text: "陪产假", value: "peichanjia" },
  { text: "丧假", value: "sangjia" },
];

// 加载详情（编辑模式）
const loadDetail = async () => {
  try {
    const detail = await getLeaveDetail(leaveId.value);
    formData.value = {
      qingjia_leixing: detail.qingjia_leixing,
      qingjia_leixing_text: getLeaveTypeText(detail.qingjia_leixing),
      kaishi_shijian: detail.kaishi_shijian,
      kaishi_shijian_text: dayjs(detail.kaishi_shijian).format(
        "YYYY-MM-DD HH:mm",
      ),
      jieshu_shijian: detail.jieshu_shijian,
      jieshu_shijian_text: dayjs(detail.jieshu_shijian).format(
        "YYYY-MM-DD HH:mm",
      ),
      qingjia_tianshu: detail.qingjia_tianshu,
      qingjia_yuanyin: detail.qingjia_yuanyin,
      fujian_lujing: detail.fujian_lujing || "",
      beizhu: detail.beizhu || "",
    };

    startTime.value = new Date(detail.kaishi_shijian);
    endTime.value = new Date(detail.jieshu_shijian);

    // 加载附件
    if (detail.fujian_lujing) {
      const files = detail.fujian_lujing.split(",");
      fileList.value = files.map((url) => ({ url }));
    }
  } catch (error) {
    console.error("Load leave detail error:", error);
    showToast("加载失败");
  }
};

// 请假类型确认
const onLeaveTypeConfirm = ({ selectedOptions }: any) => {
  formData.value.qingjia_leixing = selectedOptions[0].value;
  formData.value.qingjia_leixing_text = selectedOptions[0].text;
  showLeaveTypePicker.value = false;
};

// 开始时间确认
const onStartTimeConfirm = (value: Date) => {
  startTime.value = value;
  formData.value.kaishi_shijian = dayjs(value).format("YYYY-MM-DD HH:mm:ss");
  formData.value.kaishi_shijian_text = dayjs(value).format("YYYY-MM-DD HH:mm");
  showStartTimePicker.value = false;
  calculateDays();
};

// 结束时间确认
const onEndTimeConfirm = (value: Date) => {
  endTime.value = value;
  formData.value.jieshu_shijian = dayjs(value).format("YYYY-MM-DD HH:mm:ss");
  formData.value.jieshu_shijian_text = dayjs(value).format("YYYY-MM-DD HH:mm");
  showEndTimePicker.value = false;
  calculateDays();
};

// 计算请假天数
const calculateDays = () => {
  if (formData.value.kaishi_shijian && formData.value.jieshu_shijian) {
    const start = dayjs(formData.value.kaishi_shijian);
    const end = dayjs(formData.value.jieshu_shijian);
    const days = end.diff(start, "day", true);
    formData.value.qingjia_tianshu = Math.ceil(days);
  }
};

// 文件上传后
const afterRead = (file: any) => {
  // TODO: 实现文件上传到服务器
  
};

// 删除文件前
const beforeDelete = () => {
  return showConfirmDialog({
    title: "确认删除",
    message: "确定要删除这个附件吗？",
  });
};

// 保存草稿
const onSaveDraft = async () => {
  try {
    const data: any = {
      qingjia_leixing: formData.value.qingjia_leixing,
      kaishi_shijian: formData.value.kaishi_shijian,
      jieshu_shijian: formData.value.jieshu_shijian,
      qingjia_tianshu: formData.value.qingjia_tianshu,
      qingjia_yuanyin: formData.value.qingjia_yuanyin,
      beizhu: formData.value.beizhu,
    };

    if (isEdit.value) {
      await updateLeave(leaveId.value, data);
    } else {
      await createLeave(data);
    }

    showToast("保存成功");
    router.back();
  } catch (error) {
    console.error("Save draft error:", error);
  }
};

// 提交表单
const onSubmit = async () => {
  if (!formData.value.qingjia_leixing) {
    showToast("请选择请假类型");
    return;
  }
  if (!formData.value.kaishi_shijian || !formData.value.jieshu_shijian) {
    showToast("请选择请假时间");
    return;
  }
  if (!formData.value.qingjia_yuanyin) {
    showToast("请输入请假原因");
    return;
  }

  submitting.value = true;
  try {
    const data: any = {
      qingjia_leixing: formData.value.qingjia_leixing,
      kaishi_shijian: formData.value.kaishi_shijian,
      jieshu_shijian: formData.value.jieshu_shijian,
      qingjia_tianshu: formData.value.qingjia_tianshu,
      qingjia_yuanyin: formData.value.qingjia_yuanyin,
      beizhu: formData.value.beizhu,
    };

    if (isEdit.value) {
      await updateLeave(leaveId.value, data);
      showToast("更新成功");
    } else {
      await createLeave(data);
      showToast("提交成功");
    }

    router.back();
  } catch (error) {
    console.error("Submit error:", error);
  } finally {
    submitting.value = false;
  }
};

// 返回
const onBack = () => {
  router.back();
};

// 获取请假类型文本
const getLeaveTypeText = (type: string) => {
  const option = leaveTypeOptions.find((o) => o.value === type);
  return option?.text || type;
};

onMounted(() => {
  if (isEdit.value) {
    loadDetail();
  }
});
</script>

<style scoped>
.leave-form-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f2f5 0%, #ffffff 100%);
  padding-bottom: 100px;
}

:deep(.van-cell-group) {
  margin: 16px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

:deep(.van-cell-group__title) {
  padding: 16px 16px 8px;
  color: #323233;
  font-size: 15px;
  font-weight: 600;
}

:deep(.van-field__label) {
  color: #646566;
  font-weight: 500;
}

:deep(.van-field__control) {
  color: #323233;
}

.submit-buttons {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.95) 20%,
    #ffffff 100%
  );
  backdrop-filter: blur(10px);
  box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.06);
  display: flex;
  gap: 12px;
  z-index: 100;
}

.submit-buttons .van-button {
  flex: 1;
  height: 44px;
  font-size: 16px;
  font-weight: 600;
}

.submit-buttons .van-button--default {
  background-color: #f7f8fa;
  border-color: #f7f8fa;
  color: #646566;
}

.submit-buttons .van-button--primary {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4);
}
</style>
