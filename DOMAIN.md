# 领域模型文档 (DOMAIN.md)

> ⚠️ **本文件由 MCP (Model Context Protocol) v2.0 管理**
>
> **设计状态**: 🔒 已冻结 (FROZEN)
> **冻结时间**: 2025-12-19T16:00:00Z
> **允许操作**: ✅ READ ONLY

---

## 📋 目录

1. [用户管理域](#用户管理域-yonghu_guanli)
2. [客户管理域](#客户管理域-kehu_guanli)
3. [线索管理域](#线索管理域-xiansuo_guanli)
4. [合同管理域](#合同管理域-hetong_guanli)
5. [支付管理域](#支付管理域-zhifu_guanli)
6. [审核管理域](#审核管理域-shenhe_guanli)
7. [办公管理域](#办公管理域-bangong_guanli)
8. [产品管理域](#产品管理域-chanpin_guanli)

---

## 👤 用户管理域 (yonghu_guanli)

### 实体

| 实体                | 文件                  | 说明                             |
| ------------------- | --------------------- | -------------------------------- |
| **Yonghu**          | `yonghu.py`           | 用户实体，包含登录凭证、基本信息 |
| **Jiaose**          | `jiaose.py`           | 角色实体，定义权限组             |
| **Quanxian**        | `quanxian.py`         | 权限实体，最小权限单元           |
| **YonghuJiaose**    | `yonghu_jiaose.py`    | 用户-角色关联                    |
| **JiaoseQuanxian**  | `jiaose_quanxian.py`  | 角色-权限关联                    |
| **UserPreferences** | `user_preferences.py` | 用户偏好设置                     |

### 核心字段

```python
# Yonghu (用户)
- id: UUID
- yonghuming: str              # 用户名
- shouji: str                  # 手机号
- youxiang: str                # 邮箱
- mima_hash: str               # 密码哈希
- xingming: str                # 姓名
- shifou_qiyong: bool          # 是否启用
- shifou_guanliyuan: bool      # 是否管理员

# Jiaose (角色)
- id: UUID
- jiaose_mingcheng: str        # 角色名称
- jiaose_bianma: str           # 角色编码 (唯一)
- miaoshu: str                 # 描述

# Quanxian (权限)
- id: UUID
- quanxian_mingcheng: str      # 权限名称
- quanxian_bianma: str         # 权限编码 (唯一)
- quanxian_leixing: str        # 权限类型 (menu/button/api)
```

---

## 🏢 客户管理域 (kehu_guanli)

### 实体

| 实体         | 文件           | 说明     |
| ------------ | -------------- | -------- |
| **Kehu**     | `kehu.py`      | 客户实体 |
| **FuwuJilu** | `fuwu_jilu.py` | 服务记录 |

### 核心字段

```python
# Kehu (客户)
- id: UUID
- kehu_mingcheng: str          # 客户名称
- kehu_leixing: str            # 客户类型 (企业/个人)
- lianxiren: str               # 联系人
- lianxi_dianhua: str          # 联系电话
- dizhi: str                   # 地址
- fuzeren_id: UUID             # 负责人ID (关联 Yonghu)
- zhuangtai: str               # 状态
```

---

## 📈 线索管理域 (xiansuo_guanli)

### 实体

| 实体                 | 文件                   | 说明         |
| -------------------- | ---------------------- | ------------ |
| **Xiansuo**          | `xiansuo.py`           | 线索实体     |
| **XiansuoGenjin**    | `xiansuo_genjin.py`    | 跟进记录     |
| **XiansuoBaojia**    | `xiansuo_baojia.py`    | 报价单       |
| **XiansuoLaiyuan**   | `xiansuo_laiyuan.py`   | 线索来源配置 |
| **XiansuoZhuangtai** | `xiansuo_zhuangtai.py` | 线索状态配置 |

### 核心字段

```python
# Xiansuo (线索)
- id: UUID
- xiansuo_mingcheng: str       # 线索名称
- lianxiren: str               # 联系人
- shouji: str                  # 手机
- laiyuan_id: UUID             # 来源ID
- zhuangtai_id: UUID           # 状态ID
- fuzeren_id: UUID             # 负责人ID
- kehu_id: UUID                # 转换后的客户ID (可空)

# XiansuoBaojia (报价单)
- id: UUID
- xiansuo_id: UUID             # 线索ID
- baojia_bianhao: str          # 报价编号
- zong_jine: Decimal           # 总金额
- zhuangtai: str               # 状态
```

---

## 📄 合同管理域 (hetong_guanli)

### 实体

| 实体                   | 文件                      | 说明         |
| ---------------------- | ------------------------- | ------------ |
| **Hetong**             | `hetong.py`               | 合同实体     |
| **HetongMoban**        | `hetong_moban.py`         | 合同模板     |
| **HetongQianshu**      | `hetong_qianshu.py`       | 合同签署记录 |
| **HetongYifangZhuti**  | `hetong_yifang_zhuti.py`  | 乙方主体     |
| **HetongZhifuFangshi** | `hetong_zhifu_fangshi.py` | 支付方式配置 |

### 核心字段

````python
# Hetong (合同)
- id: UUID
- hetong_bianhao: str          # 合同编号
- hetong_mingcheng: str        # 合同名称


---

## ✅ 审核管理域 (shenhe_guanli)

### 实体

| 实体 | 文件 | 说明 |
|------|------|------|
| **ShenheGuize** | `shenhe_guize.py` | 审核规则 |
| **ShenheLiucheng** | `shenhe_liucheng.py` | 审核流程 |
| **ShenheJilu** | `shenhe_jilu.py` | 审核记录 |

### 核心字段

```python
# ShenheGuize (审核规则)
- id: UUID
- guize_mingcheng: str         # 规则名称
- yewu_leixing: str            # 业务类型 (payment/leave/expense...)
- tiaojian: JSON               # 条件配置
- shenpi_ren_ids: List[UUID]   # 审批人列表
- shifou_qiyong: bool          # 是否启用

# ShenheJilu (审核记录)
- id: UUID
- yewu_leixing: str            # 业务类型
- yewu_id: UUID                # 业务ID
- shenpi_ren_id: UUID          # 审批人ID
- shenpi_jieguo: str           # 审批结果 (approved/rejected)
- shenpi_yijian: str           # 审批意见
````

---

## 🏢 办公管理域 (bangong_guanli)

### 实体

| 实体                     | 文件                        | 说明         |
| ------------------------ | --------------------------- | ------------ |
| **QingjiaShenqing**      | `qingjia_shenqing.py`       | 请假申请     |
| **BaoxiaoShenqing**      | `baoxiao_shenqing.py`       | 报销申请     |
| **CaigouShenqing**       | `caigou_shenqing.py`        | 采购申请     |
| **DuiwaiFukuanShenqing** | `duiwai_fukuan_shenqing.py` | 对外付款申请 |
| **GongzuoJiaojie**       | `gongzuo_jiaojie.py`        | 工作交接     |

### 核心字段

```python
# QingjiaShenqing (请假申请)
- id: UUID
- shenqing_ren_id: UUID        # 申请人ID
- qingjia_leixing: str         # 请假类型
- kaishi_shijian: datetime     # 开始时间
- jieshu_shijian: datetime     # 结束时间
- qingjia_tianshu: float       # 请假天数
- shenpi_zhuangtai: str        # 审批状态

# BaoxiaoShenqing (报销申请)
- id: UUID
- shenqing_ren_id: UUID        # 申请人ID
- baoxiao_jine: Decimal        # 报销金额
- baoxiao_leixing: str         # 报销类型
- shenpi_zhuangtai: str        # 审批状态
```

---

## 📦 产品管理域 (chanpin_guanli)

### 实体

| 实体               | 文件                 | 说明     |
| ------------------ | -------------------- | -------- |
| **ChanpinXiangmu** | `chanpin_xiangmu.py` | 产品项目 |
| **ChanpinFenlei**  | `chanpin_fenlei.py`  | 产品分类 |
| **ChanpinBuzou**   | `chanpin_buzou.py`   | 产品步骤 |

### 核心字段

```python
# ChanpinXiangmu (产品项目)
- id: UUID
- chanpin_mingcheng: str       # 产品名称
- chanpin_bianma: str          # 产品编码
- fenlei_id: UUID              # 分类ID
- jia_ge: Decimal              # 价格
- miaoshu: str                 # 描述
- shifou_qiyong: bool          # 是否启用

# ChanpinBuzou (产品步骤)
- id: UUID
- chanpin_id: UUID             # 产品ID
- buzou_mingcheng: str         # 步骤名称
- buzou_shunxu: int            # 步骤顺序
- banshi_tianshu: int          # 办事天数
```

---

## 🔗 领域关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Yonghu (用户)                               │
│                         ┌─────────┴─────────┐                           │
│                         ↓                   ↓                           │
│                      Jiaose              Quanxian                       │
│                      (角色)               (权限)                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ↓                       ↓                       ↓
    ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
    │    Kehu      │       │   Xiansuo    │       │ BangongShenqing
    │   (客户)     │       │   (线索)     │       │  (办公申请)   │
    └──────────────┘       └──────────────┘       └──────────────┘
            │                      │                       │
            │                      ↓                       ↓
            │              ┌──────────────┐       ┌──────────────┐
            │              │ XiansuoBaojia│       │ ShenheJilu   │
            │              │   (报价单)   │       │  (审核记录)  │
            │              └──────────────┘       └──────────────┘
            │                      │
            └──────────┬───────────┘
                       ↓
               ┌──────────────┐
               │   Hetong     │
               │   (合同)     │
               └──────────────┘
                       │
                       ↓
               ┌──────────────┐
               │ HetongZhifu  │
               │  (合同支付)  │
               └──────────────┘
```

---

## 🔐 DESIGN_FREEZE

```yaml
design_locked: true
frozen_at: "2025-12-19T16:00:00Z"
```

**冻结后禁止**:

- ❌ 添加新实体
- ❌ 删除现有实体
- ❌ 修改实体关系
- ❌ 修改核心字段定义

**冻结后允许**:

- ✅ 在现有实体内添加可空字段
- ✅ 添加索引
- ✅ 添加计算属性
