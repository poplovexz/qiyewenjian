# 支付接入快速开始指南

## 🚀 立即开始

这个指南将帮助您在30分钟内完成支付功能的基础搭建。

---

## 步骤1：安装依赖包（5分钟）

### 后端依赖

编辑 `packages/backend/requirements-production.txt`，添加：

```txt
# 微信支付SDK
wechatpayv3==1.2.6

# 支付宝SDK  
alipay-sdk-python==3.7.4

# 加密库
cryptography==41.0.7
```

安装依赖：
```bash
cd /var/www/packages/backend
source venv/bin/activate
pip install -r requirements-production.txt
```

---

## 步骤2：创建数据库表（5分钟）

创建迁移脚本 `packages/backend/src/scripts/create_payment_tables.sql`:

```sql
-- 支付配置表
CREATE TABLE IF NOT EXISTS zhifu_peizhi (
    id VARCHAR(36) PRIMARY KEY DEFAULT (gen_random_uuid()::text),
    peizhi_mingcheng VARCHAR(100) NOT NULL COMMENT '配置名称',
    zhifu_leixing VARCHAR(20) NOT NULL COMMENT '支付类型: weixin, zhifubao',
    
    -- 微信支付配置
    weixin_shanghu_hao VARCHAR(50),
    weixin_appid VARCHAR(50),
    weixin_api_v3_miyao TEXT,
    weixin_shanghu_siyao TEXT,
    weixin_zhengshu_xuliehao VARCHAR(100),
    
    -- 支付宝配置
    zhifubao_appid VARCHAR(50),
    zhifubao_shanghu_siyao TEXT,
    zhifubao_zhifubao_gongyao TEXT,
    
    -- 通用配置
    huidiao_url VARCHAR(500),
    tongzhi_url VARCHAR(500),
    shi_moren CHAR(1) DEFAULT 'N',
    zhuangtai VARCHAR(20) DEFAULT 'active',
    beizhu TEXT,
    
    -- 审计字段
    is_deleted CHAR(1) DEFAULT 'N',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36)
);

COMMENT ON TABLE zhifu_peizhi IS '支付配置表';
COMMENT ON COLUMN zhifu_peizhi.peizhi_mingcheng IS '配置名称';
COMMENT ON COLUMN zhifu_peizhi.zhifu_leixing IS '支付类型: weixin, zhifubao';

-- 支付回调日志表
CREATE TABLE IF NOT EXISTS zhifu_huidiao_rizhi (
    id VARCHAR(36) PRIMARY KEY DEFAULT (gen_random_uuid()::text),
    dingdan_id VARCHAR(36),
    zhifu_leixing VARCHAR(20) NOT NULL,
    huidiao_leixing VARCHAR(20) NOT NULL,
    qingqiu_shuju TEXT,
    xiangying_shuju TEXT,
    qianming_yanzheng CHAR(1) DEFAULT 'N',
    chuli_zhuangtai VARCHAR(20),
    cuowu_xinxi TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE zhifu_huidiao_rizhi IS '支付回调日志表';

-- 退款记录表
CREATE TABLE IF NOT EXISTS zhifu_tuikuan (
    id VARCHAR(36) PRIMARY KEY DEFAULT (gen_random_uuid()::text),
    dingdan_id VARCHAR(36) NOT NULL,
    tuikuan_danhao VARCHAR(50) UNIQUE NOT NULL,
    disan_fang_tuikuan_hao VARCHAR(100),
    tuikuan_jine DECIMAL(15,2) NOT NULL,
    tuikuan_yuanyin VARCHAR(500),
    tuikuan_zhuangtai VARCHAR(20) DEFAULT 'pending',
    tuikuan_shijian TIMESTAMP,
    daozhang_shijian TIMESTAMP,
    beizhu TEXT,
    
    is_deleted CHAR(1) DEFAULT 'N',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36)
);

COMMENT ON TABLE zhifu_tuikuan IS '退款记录表';

-- 扩展现有支付订单表
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS zhifu_peizhi_id VARCHAR(36);
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS disan_fang_dingdan_hao VARCHAR(100);
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS zhifu_shijian TIMESTAMP;
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS tuikuan_jine DECIMAL(15,2) DEFAULT 0;
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS tuikuan_cishu INT DEFAULT 0;

COMMENT ON COLUMN zhifu_dingdan.zhifu_peizhi_id IS '支付配置ID';
COMMENT ON COLUMN zhifu_dingdan.disan_fang_dingdan_hao IS '第三方订单号';
COMMENT ON COLUMN zhifu_dingdan.zhifu_shijian IS '支付时间';
COMMENT ON COLUMN zhifu_dingdan.tuikuan_jine IS '退款金额';
COMMENT ON COLUMN zhifu_dingdan.tuikuan_cishu IS '退款次数';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_zhifu_peizhi_leixing ON zhifu_peizhi(zhifu_leixing);
CREATE INDEX IF NOT EXISTS idx_zhifu_huidiao_dingdan ON zhifu_huidiao_rizhi(dingdan_id);
CREATE INDEX IF NOT EXISTS idx_zhifu_tuikuan_dingdan ON zhifu_tuikuan(dingdan_id);
```

执行迁移：
```bash
cd /var/www/packages/backend
source venv/bin/activate
psql -U proxy_user -d proxy_db -f src/scripts/create_payment_tables.sql
```

---

## 步骤3：创建基础工具类（10分钟）

### 微信支付工具类

创建 `packages/backend/src/utils/payment/weixin_pay.py`:

```python
from wechatpayv3 import WeChatPay, WeChatPayType
from typing import Dict, Tuple

class WeixinPayUtil:
    """微信支付工具类"""
    
    def __init__(self, config):
        """初始化微信支付客户端"""
        self.wxpay = WeChatPay(
            wechatpay_type=WeChatPayType.JSAPI,
            mchid=config.weixin_shanghu_hao,
            private_key=config.weixin_shanghu_siyao,
            cert_serial_no=config.weixin_zhengshu_xuliehao,
            apiv3_key=config.weixin_api_v3_miyao,
            appid=config.weixin_appid,
            notify_url=config.tongzhi_url
        )
    
    def create_jsapi_order(
        self, 
        out_trade_no: str, 
        description: str, 
        amount: int,  # 单位：分
        payer_openid: str
    ) -> Tuple[int, Dict]:
        """创建JSAPI支付订单"""
        code, message = self.wxpay.pay(
            description=description,
            out_trade_no=out_trade_no,
            amount={'total': amount, 'currency': 'CNY'},
            payer={'openid': payer_openid}
        )
        return code, message
    
    def query_order(self, out_trade_no: str) -> Tuple[int, Dict]:
        """查询订单"""
        return self.wxpay.query(out_trade_no=out_trade_no)
    
    def close_order(self, out_trade_no: str) -> Tuple[int, Dict]:
        """关闭订单"""
        return self.wxpay.close(out_trade_no=out_trade_no)
    
    def refund(
        self, 
        out_trade_no: str, 
        out_refund_no: str, 
        refund_amount: int,
        total_amount: int,
        reason: str = ''
    ) -> Tuple[int, Dict]:
        """申请退款"""
        return self.wxpay.refund(
            out_trade_no=out_trade_no,
            out_refund_no=out_refund_no,
            amount={
                'refund': refund_amount,
                'total': total_amount,
                'currency': 'CNY'
            },
            reason=reason
        )
    
    def verify_notify(self, headers: Dict, body: str) -> bool:
        """验证回调签名"""
        try:
            return self.wxpay.verify_sign(headers, body)
        except Exception:
            return False
```

### 支付宝工具类

创建 `packages/backend/src/utils/payment/alipay.py`:

```python
from alipay import AliPay
from typing import Dict, Optional

class AlipayUtil:
    """支付宝工具类"""
    
    def __init__(self, config):
        """初始化支付宝客户端"""
        self.alipay = AliPay(
            appid=config.zhifubao_appid,
            app_notify_url=config.tongzhi_url,
            app_private_key_string=config.zhifubao_shanghu_siyao,
            alipay_public_key_string=config.zhifubao_zhifubao_gongyao,
            sign_type="RSA2",
            debug=False
        )
    
    def create_page_order(
        self, 
        out_trade_no: str, 
        subject: str, 
        total_amount: int,  # 单位：分
        body: str = ''
    ) -> str:
        """创建网页支付订单"""
        order_string = self.alipay.api_alipay_trade_page_pay(
            out_trade_no=out_trade_no,
            total_amount=str(total_amount / 100),  # 转换为元
            subject=subject,
            body=body
        )
        return order_string
    
    def query_order(self, out_trade_no: str) -> Dict:
        """查询订单"""
        return self.alipay.api_alipay_trade_query(
            out_trade_no=out_trade_no
        )
    
    def close_order(self, out_trade_no: str) -> Dict:
        """关闭订单"""
        return self.alipay.api_alipay_trade_close(
            out_trade_no=out_trade_no
        )
    
    def refund(
        self, 
        out_trade_no: str, 
        refund_amount: int,  # 单位：分
        refund_reason: str = ''
    ) -> Dict:
        """申请退款"""
        return self.alipay.api_alipay_trade_refund(
            out_trade_no=out_trade_no,
            refund_amount=str(refund_amount / 100),
            refund_reason=refund_reason
        )
    
    def verify_notify(self, data: Dict, signature: str) -> bool:
        """验证回调签名"""
        try:
            return self.alipay.verify(data, signature)
        except Exception:
            return False
```

创建 `packages/backend/src/utils/payment/__init__.py`:

```python
from .weixin_pay import WeixinPayUtil
from .alipay import AlipayUtil

__all__ = ['WeixinPayUtil', 'AlipayUtil']
```

---

## 步骤4：测试工具类（5分钟）

创建测试脚本 `test_payment_utils.py`:

```python
#!/usr/bin/env python3
"""测试支付工具类"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'packages' / 'backend' / 'src'))

# 测试配置对象
class MockWeixinConfig:
    weixin_shanghu_hao = "YOUR_MCHID"
    weixin_appid = "YOUR_APPID"
    weixin_api_v3_miyao = "YOUR_API_V3_KEY"
    weixin_shanghu_siyao = "YOUR_PRIVATE_KEY"
    weixin_zhengshu_xuliehao = "YOUR_CERT_SERIAL_NO"
    tongzhi_url = "https://your-domain.com/api/v1/payment/weixin/notify"

class MockAlipayConfig:
    zhifubao_appid = "YOUR_APPID"
    zhifubao_shanghu_siyao = "YOUR_PRIVATE_KEY"
    zhifubao_zhifubao_gongyao = "ALIPAY_PUBLIC_KEY"
    tongzhi_url = "https://your-domain.com/api/v1/payment/alipay/notify"

def test_weixin_pay():
    """测试微信支付"""
    from utils.payment import WeixinPayUtil
    
    config = MockWeixinConfig()
    wxpay = WeixinPayUtil(config)
    
    print("✓ 微信支付工具类初始化成功")
    print(f"  商户号: {config.weixin_shanghu_hao}")
    print(f"  APPID: {config.weixin_appid}")

def test_alipay():
    """测试支付宝"""
    from utils.payment import AlipayUtil
    
    config = MockAlipayConfig()
    alipay = AlipayUtil(config)
    
    print("✓ 支付宝工具类初始化成功")
    print(f"  APPID: {config.zhifubao_appid}")

if __name__ == "__main__":
    print("=" * 60)
    print("测试支付工具类")
    print("=" * 60)
    print()
    
    try:
        test_weixin_pay()
        print()
        test_alipay()
        print()
        print("=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
```

---

## 步骤5：下一步计划（5分钟）

现在您已经完成了基础搭建，接下来可以：

### 立即可做的事情：

1. **配置商户信息**
   - 申请微信支付商户号
   - 申请支付宝商户账号
   - 获取API密钥和证书

2. **创建支付配置管理页面**
   - 参考 `PaymentMethodForm.vue` 的实现
   - 添加密钥输入和验证

3. **实现支付订单创建API**
   - 创建 `packages/backend/src/api/api_v1/endpoints/zhifu_guanli/zhifu_dingdan.py`
   - 调用工具类创建订单

### 推荐阅读：

- 📖 [PAYMENT_API_INTEGRATION_PLAN.md](./PAYMENT_API_INTEGRATION_PLAN.md) - 完整的实施方案
- 📖 [微信支付开发文档](https://pay.weixin.qq.com/doc/v3/merchant/4012062524)
- 📖 [支付宝开发文档](https://opendocs.alipay.com/open/direct-payment/qadp9d)

---

## 🎯 快速检查清单

- [ ] 安装了支付SDK依赖包
- [ ] 创建了数据库表
- [ ] 创建了支付工具类
- [ ] 测试工具类初始化成功
- [ ] 阅读了完整实施方案
- [ ] 准备好商户配置信息

---

## 💡 提示

1. **沙箱环境测试**：在正式接入前，先使用沙箱环境测试
2. **密钥安全**：不要将密钥提交到Git仓库
3. **HTTPS必须**：支付回调必须使用HTTPS
4. **日志记录**：记录所有支付相关操作的日志

---

## 📞 需要帮助？

如果遇到问题，请：
1. 查看 [PAYMENT_API_INTEGRATION_PLAN.md](./PAYMENT_API_INTEGRATION_PLAN.md) 的常见问题部分
2. 查看微信支付/支付宝官方文档
3. 联系开发团队

---

**恭喜！您已经完成了支付功能的基础搭建！** 🎉

