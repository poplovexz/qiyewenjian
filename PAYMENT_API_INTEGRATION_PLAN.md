# 微信支付和支付宝商户收款API接入方案

## 📋 项目概述

接入微信支付和支付宝的商户收款API，实现在线支付功能。

### 参考文档
- **微信支付**: https://pay.weixin.qq.com/doc/v3/merchant/4012062524
- **支付宝**: https://opendocs.alipay.com/open/direct-payment/qadp9d

---

## 🎯 功能需求

### 核心功能
1. **支付配置管理**
   - 微信支付商户配置（商户号、API密钥、证书）
   - 支付宝商户配置（APPID、私钥、公钥）
   - 支持多商户配置

2. **支付订单管理**
   - 创建支付订单
   - 查询订单状态
   - 关闭订单
   - 订单列表查询

3. **支付回调处理**
   - 微信支付回调验证
   - 支付宝支付回调验证
   - 异步通知处理
   - 回调日志记录

4. **退款管理**
   - 申请退款
   - 查询退款状态
   - 退款回调处理

5. **账单管理**
   - 下载交易账单
   - 下载资金账单
   - 账单对账

---

## 🏗️ 技术架构

### 后端架构

```
packages/backend/src/
├── models/
│   └── zhifu_guanli/           # 支付管理模块
│       ├── zhifu_peizhi.py     # 支付配置表
│       ├── zhifu_dingdan.py    # 支付订单表（已存在）
│       ├── zhifu_huidiaozhifu_tuikuan.py      # 退款记录表
│       └── zhifu_zhangdan.py   # 账单记录表
├── schemas/
│   └── zhifu_guanli/
│       ├── zhifu_peizhi_schemas.py
│       ├── zhifu_dingdan_schemas.py
│       ├── zhifu_tuikuan_schemas.py
│       └── zhifu_zhangdan_schemas.py
├── services/
│   └── zhifu_guanli/
│       ├── weixin_pay_service.py    # 微信支付服务
│       ├── alipay_service.py        # 支付宝服务
│       ├── zhifu_config_service.py  # 支付配置服务
│       └── zhifu_order_service.py   # 支付订单服务
├── api/
│   └── api_v1/
│       └── endpoints/
│           └── zhifu_guanli/
│               ├── zhifu_peizhi.py  # 支付配置API
│               ├── zhifu_dingdan.py # 支付订单API
│               ├── zhifu_huidiaozhifu_tuikuan.py  # 退款API
│               └── zhifu_zhangdan.py # 账单API
└── utils/
    └── payment/
        ├── weixin_pay.py       # 微信支付工具类
        ├── alipay.py           # 支付宝工具类
        └── signature.py        # 签名验证工具
```

### 前端架构

```
packages/frontend/src/
├── views/
│   └── payment/
│       ├── PaymentConfig.vue       # 支付配置管理
│       ├── PaymentConfigForm.vue   # 支付配置表单
│       ├── PaymentOrder.vue        # 支付订单列表
│       ├── PaymentOrderDetail.vue  # 订单详情
│       ├── RefundManagement.vue    # 退款管理
│       └── BillManagement.vue      # 账单管理
├── api/
│   └── modules/
│       └── payment.ts              # 支付API接口
└── stores/
    └── modules/
        └── payment.ts              # 支付状态管理
```

---

## 📊 数据库设计

### 1. 支付配置表 (zhifu_peizhi)

```sql
CREATE TABLE zhifu_peizhi (
    id VARCHAR(36) PRIMARY KEY,
    peizhi_mingcheng VARCHAR(100) NOT NULL COMMENT '配置名称',
    zhifu_leixing VARCHAR(20) NOT NULL COMMENT '支付类型: weixin, zhifubao',
    
    -- 微信支付配置
    weixin_shanghu_hao VARCHAR(50) COMMENT '微信商户号',
    weixin_appid VARCHAR(50) COMMENT '微信APPID',
    weixin_api_miyao TEXT COMMENT '微信API密钥（加密存储）',
    weixin_api_v3_miyao TEXT COMMENT '微信APIv3密钥（加密存储）',
    weixin_shanghu_zhengshu TEXT COMMENT '微信商户证书（加密存储）',
    weixin_shanghu_siyao TEXT COMMENT '微信商户私钥（加密存储）',
    weixin_zhengshu_xuliehao VARCHAR(100) COMMENT '微信证书序列号',
    
    -- 支付宝配置
    zhifubao_appid VARCHAR(50) COMMENT '支付宝APPID',
    zhifubao_shanghu_siyao TEXT COMMENT '支付宝商户私钥（加密存储）',
    zhifubao_zhifubao_gongyao TEXT COMMENT '支付宝公钥（加密存储）',
    zhifubao_yingyong_gongyao TEXT COMMENT '应用公钥',
    
    -- 通用配置
    huidiaourl VARCHAR(500) COMMENT '支付回调URL',
    tongzhi_url VARCHAR(500) COMMENT '异步通知URL',
    shi_moren CHAR(1) DEFAULT 'N' COMMENT '是否默认配置',
    zhuangtai VARCHAR(20) DEFAULT 'active' COMMENT '状态: active, inactive',
    beizhu TEXT COMMENT '备注',
    
    -- 审计字段
    is_deleted CHAR(1) DEFAULT 'N',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(36),
    updated_by VARCHAR(36),
    
    INDEX idx_zhifu_leixing (zhifu_leixing),
    INDEX idx_shi_moren (shi_moren),
    INDEX idx_zhuangtai (zhuangtai)
) COMMENT='支付配置表';
```

### 2. 支付订单表 (zhifu_dingdan) - 扩展现有表

需要添加的字段：
```sql
ALTER TABLE zhifu_dingdan ADD COLUMN zhifu_peizhi_id VARCHAR(36) COMMENT '支付配置ID';
ALTER TABLE zhifu_dingdan ADD COLUMN disan_fang_dingdan_hao VARCHAR(100) COMMENT '第三方订单号';
ALTER TABLE zhifu_dingdan ADD COLUMN zhifu_shijian TIMESTAMP COMMENT '支付时间';
ALTER TABLE zhifu_dingdan ADD COLUMN huidiaozhifu_tuikuan_jine DECIMAL(15,2) DEFAULT 0 COMMENT '退款金额';
ALTER TABLE zhifu_dingdan ADD COLUMN huidiaozhifu_tuikuan_cishu INT DEFAULT 0 COMMENT '退款次数';
```

### 3. 支付回调日志表 (zhifu_huidiao_rizhi)

```sql
CREATE TABLE zhifu_huidiao_rizhi (
    id VARCHAR(36) PRIMARY KEY,
    dingdan_id VARCHAR(36) COMMENT '订单ID',
    zhifu_leixing VARCHAR(20) NOT NULL COMMENT '支付类型',
    huidiao_leixing VARCHAR(20) NOT NULL COMMENT '回调类型: payment, refund',
    qingqiu_shuju TEXT COMMENT '请求数据',
    xiangying_shuju TEXT COMMENT '响应数据',
    qianming_yanzheng CHAR(1) DEFAULT 'N' COMMENT '签名验证结果',
    chuli_zhuangtai VARCHAR(20) COMMENT '处理状态',
    cuowu_xinxi TEXT COMMENT '错误信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_dingdan_id (dingdan_id),
    INDEX idx_zhifu_leixing (zhifu_leixing),
    INDEX idx_created_at (created_at)
) COMMENT='支付回调日志表';
```

### 4. 退款记录表 (zhifu_tuikuan)

```sql
CREATE TABLE zhifu_tuikuan (
    id VARCHAR(36) PRIMARY KEY,
    dingdan_id VARCHAR(36) NOT NULL COMMENT '原订单ID',
    tuikuan_danhao VARCHAR(50) UNIQUE NOT NULL COMMENT '退款单号',
    disan_fang_tuikuan_hao VARCHAR(100) COMMENT '第三方退款号',
    tuikuan_jine DECIMAL(15,2) NOT NULL COMMENT '退款金额',
    tuikuan_yuanyin VARCHAR(500) COMMENT '退款原因',
    tuikuan_zhuangtai VARCHAR(20) DEFAULT 'pending' COMMENT '退款状态: pending, success, failed',
    tuikuan_shijian TIMESTAMP COMMENT '退款时间',
    daozhang_shijian TIMESTAMP COMMENT '到账时间',
    beizhu TEXT COMMENT '备注',
    
    -- 审计字段
    is_deleted CHAR(1) DEFAULT 'N',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(36),
    
    INDEX idx_dingdan_id (dingdan_id),
    INDEX idx_tuikuan_danhao (tuikuan_danhao),
    INDEX idx_tuikuan_zhuangtai (tuikuan_zhuangtai)
) COMMENT='退款记录表';
```

---

## 🔧 技术实现

### 依赖包

**后端 (requirements-production.txt)**:
```
# 微信支付
wechatpayv3==1.2.6

# 支付宝
alipay-sdk-python==3.7.4

# 加密
cryptography==41.0.7
```

### 微信支付核心代码示例

```python
# packages/backend/src/utils/payment/weixin_pay.py

from wechatpayv3 import WeChatPay, WeChatPayType
from cryptography.hazmat.primitives import serialization
import json

class WeixinPayUtil:
    """微信支付工具类"""
    
    def __init__(self, config):
        self.mchid = config.weixin_shanghu_hao
        self.appid = config.weixin_appid
        self.api_v3_key = config.weixin_api_v3_miyao
        self.cert_serial_no = config.weixin_zhengshu_xuliehao
        self.private_key = config.weixin_shanghu_siyao
        self.notify_url = config.tongzhi_url
        
        # 初始化微信支付客户端
        self.wxpay = WeChatPay(
            wechatpay_type=WeChatPayType.JSAPI,
            mchid=self.mchid,
            private_key=self.private_key,
            cert_serial_no=self.cert_serial_no,
            apiv3_key=self.api_v3_key,
            appid=self.appid,
            notify_url=self.notify_url
        )
    
    def create_order(self, out_trade_no, description, amount, payer_openid):
        """创建JSAPI支付订单"""
        code, message = self.wxpay.pay(
            description=description,
            out_trade_no=out_trade_no,
            amount={'total': amount, 'currency': 'CNY'},
            payer={'openid': payer_openid}
        )
        return code, message
    
    def query_order(self, out_trade_no):
        """查询订单"""
        code, message = self.wxpay.query(out_trade_no=out_trade_no)
        return code, message
    
    def close_order(self, out_trade_no):
        """关闭订单"""
        code, message = self.wxpay.close(out_trade_no=out_trade_no)
        return code, message
    
    def refund(self, out_trade_no, out_refund_no, refund_amount, total_amount, reason=''):
        """申请退款"""
        code, message = self.wxpay.refund(
            out_trade_no=out_trade_no,
            out_refund_no=out_refund_no,
            amount={
                'refund': refund_amount,
                'total': total_amount,
                'currency': 'CNY'
            },
            reason=reason
        )
        return code, message
    
    def verify_notify(self, headers, body):
        """验证回调签名"""
        return self.wxpay.verify_sign(headers, body)
```

### 支付宝核心代码示例

```python
# packages/backend/src/utils/payment/alipay.py

from alipay import AliPay
import json

class AlipayUtil:
    """支付宝工具类"""
    
    def __init__(self, config):
        self.alipay = AliPay(
            appid=config.zhifubao_appid,
            app_notify_url=config.tongzhi_url,
            app_private_key_string=config.zhifubao_shanghu_siyao,
            alipay_public_key_string=config.zhifubao_zhifubao_gongyao,
            sign_type="RSA2",
            debug=False  # 生产环境设为False
        )
    
    def create_order(self, out_trade_no, subject, total_amount, body=''):
        """创建支付订单"""
        order_string = self.alipay.api_alipay_trade_page_pay(
            out_trade_no=out_trade_no,
            total_amount=str(total_amount / 100),  # 转换为元
            subject=subject,
            body=body,
            return_url=None,
            notify_url=None
        )
        return order_string
    
    def query_order(self, out_trade_no):
        """查询订单"""
        result = self.alipay.api_alipay_trade_query(
            out_trade_no=out_trade_no
        )
        return result
    
    def close_order(self, out_trade_no):
        """关闭订单"""
        result = self.alipay.api_alipay_trade_close(
            out_trade_no=out_trade_no
        )
        return result
    
    def refund(self, out_trade_no, refund_amount, refund_reason=''):
        """申请退款"""
        result = self.alipay.api_alipay_trade_refund(
            out_trade_no=out_trade_no,
            refund_amount=str(refund_amount / 100),
            refund_reason=refund_reason
        )
        return result
    
    def verify_notify(self, data, signature):
        """验证回调签名"""
        return self.alipay.verify(data, signature)
```

---

## 📝 实施步骤

### 阶段1：基础架构搭建（2-3天）
- [ ] 创建数据库表结构
- [ ] 安装依赖包
- [ ] 创建基础模型和Schema
- [ ] 创建工具类（微信支付、支付宝）

### 阶段2：支付配置管理（1-2天）
- [ ] 支付配置CRUD API
- [ ] 前端配置管理页面
- [ ] 密钥加密存储
- [ ] 配置验证功能

### 阶段3：支付订单功能（3-4天）
- [ ] 创建支付订单API
- [ ] 查询订单状态API
- [ ] 关闭订单API
- [ ] 前端支付订单页面
- [ ] 支付状态轮询

### 阶段4：支付回调处理（2-3天）
- [ ] 微信支付回调接口
- [ ] 支付宝回调接口
- [ ] 签名验证
- [ ] 回调日志记录
- [ ] 订单状态更新

### 阶段5：退款功能（2-3天）
- [ ] 申请退款API
- [ ] 查询退款状态API
- [ ] 退款回调处理
- [ ] 前端退款管理页面

### 阶段6：账单管理（1-2天）
- [ ] 下载账单API
- [ ] 账单解析
- [ ] 前端账单查看页面

### 阶段7：测试和优化（2-3天）
- [ ] 单元测试
- [ ] 集成测试
- [ ] 沙箱环境测试
- [ ] 性能优化
- [ ] 安全加固

---

## 🔒 安全考虑

1. **密钥安全**
   - 所有密钥使用AES加密存储
   - 密钥不在日志中输出
   - 定期轮换密钥

2. **签名验证**
   - 所有回调必须验证签名
   - 防止重放攻击
   - 记录验证失败的请求

3. **HTTPS**
   - 所有支付相关接口必须使用HTTPS
   - 配置SSL证书

4. **权限控制**
   - 支付配置管理需要管理员权限
   - 退款操作需要审批流程
   - 敏感操作记录审计日志

---

## 📈 监控和告警

1. **支付成功率监控**
2. **回调处理成功率**
3. **退款处理时效**
4. **异常订单告警**
5. **账单对账差异告警**

---

## 🎓 参考资料

### 微信支付
- [JSAPI支付产品介绍](https://pay.weixin.qq.com/doc/v3/merchant/4012062524)
- [API列表](https://pay.weixin.qq.com/doc/v3/merchant/4012791855)
- [Python SDK](https://github.com/wechatpay-apiv3/wechatpay-python)

### 支付宝
- [手机网站支付](https://opendocs.alipay.com/open/direct-payment/qadp9d)
- [Python SDK](https://github.com/fzlee/alipay)
- [开发者中心](https://open.alipay.com/)

---

## ❓ 常见问题

### Q1: 如何获取微信支付商户号和密钥？
A: 需要在微信支付商户平台申请，详见[微信支付接入指引](https://pay.weixin.qq.com/)

### Q2: 支付宝密钥如何生成？
A: 使用支付宝提供的密钥生成工具，详见[支付宝密钥生成](https://opendocs.alipay.com/common/02kipl)

### Q3: 如何测试支付功能？
A: 微信支付和支付宝都提供沙箱环境用于测试

---

## 📞 联系方式

如有问题，请联系开发团队。

