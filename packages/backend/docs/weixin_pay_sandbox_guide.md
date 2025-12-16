# 微信支付沙箱环境使用指南

## 概述

本系统已集成微信支付沙箱环境，用于测试微信支付功能。沙箱环境使用微信支付API v2，与正式环境的API v3有所不同。

## 功能特性

### 已实现功能

1. **沙箱密钥获取** - 自动从微信支付沙箱环境获取测试密钥
2. **Native扫码支付** - 创建Native支付订单，生成支付二维码
3. **订单查询** - 查询支付订单状态
4. **关闭订单** - 关闭未支付的订单
5. **支付回调** - 处理微信支付的异步通知回调

### 环境限制

- 沙箱环境目前只支持 **Native扫码支付**
- 不支持JSAPI、APP、H5等其他支付方式
- 使用API v2协议（正式环境使用API v3）

## 配置说明

### 1. 在支付配置中添加微信支付配置

访问：`http://localhost:5174/finance/payment-methods`

配置项说明：

| 字段 | 说明 | 沙箱环境 | 正式环境 |
|------|------|----------|----------|
| 配置名称 | 配置的名称 | 微信支付沙箱 | 微信支付正式 |
| 配置类型 | 选择支付平台 | 微信支付 | 微信支付 |
| 环境 | **重要** | **沙箱** | 生产 |
| 微信AppID | 公众号/小程序AppID | 测试AppID | 正式AppID |
| 微信商户号 | 商户号 | 测试商户号 | 正式商户号 |
| 微信API v3密钥 | API密钥 | 正式环境的API密钥* | 正式API v3密钥 |
| 通知URL | 回调地址 | http://your-domain/api/v1/zhifu/huidiao/weixin/notify | 同左 |

**注意：** 沙箱环境需要使用正式环境的API密钥来获取沙箱密钥，系统会自动处理。

### 2. 获取沙箱密钥

沙箱密钥会在第一次创建订单时自动获取，无需手动操作。

获取沙箱密钥的API：
```
POST https://api.mch.weixin.qq.com/xdc/apiv2getsignkey/sign/getsignkey
```

## 使用流程

### 1. 创建支付订单

**API端点：** `POST /api/v1/zhifu/api/create`

**请求参数：**
```json
{
  "dingdan_id": "订单ID",
  "zhifu_pingtai": "weixin",
  "zhifu_fangshi": "native"
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "code_url": "weixin://wxpay/bizpayurl/up?pr=xxxxx",
    "prepay_id": "wx20241127xxxxxx",
    "trade_type": "NATIVE"
  },
  "message": "创建订单成功"
}
```

### 2. 生成支付二维码

前端使用 `code_url` 生成二维码供用户扫码支付。

### 3. 支付回调处理

微信支付成功后会向配置的通知URL发送POST请求（XML格式）。

**回调URL：** `POST /api/v1/zhifu/huidiao/weixin/notify`

**回调数据格式（XML）：**
```xml
<xml>
  <return_code><![CDATA[SUCCESS]]></return_code>
  <result_code><![CDATA[SUCCESS]]></result_code>
  <appid><![CDATA[wx2421b1c4370ec43b]]></appid>
  <mch_id><![CDATA[10000100]]></mch_id>
  <out_trade_no><![CDATA[商户订单号]]></out_trade_no>
  <transaction_id><![CDATA[微信订单号]]></transaction_id>
  <total_fee>100</total_fee>
  <sign><![CDATA[签名]]></sign>
</xml>
```

**系统响应（XML）：**
```xml
<xml>
  <return_code><![CDATA[SUCCESS]]></return_code>
  <return_msg><![CDATA[OK]]></return_msg>
</xml>
```

### 4. 查询订单

**API端点：** `GET /api/v1/zhifu/api/query/{dingdan_id}`

**响应示例：**
```json
{
  "success": true,
  "data": {
    "trade_state": "SUCCESS",
    "trade_state_desc": "支付成功",
    "transaction_id": "微信订单号",
    "out_trade_no": "商户订单号",
    "total_fee": "100",
    "time_end": "20241127120000"
  },
  "message": "查询订单成功"
}
```

## 技术实现

### 核心文件

1. **工具类：** `packages/backend/src/utils/payment/weixin_pay_sandbox.py`
   - `WeixinPaySandboxUtil` - 沙箱环境工具类
   - 实现API v2的签名、加密、解密等功能

2. **服务层：** `packages/backend/src/services/zhifu_guanli/zhifu_api_service.py`
   - 根据配置的环境字段选择使用沙箱或正式工具类
   - 统一的业务逻辑处理

3. **回调处理：** `packages/backend/src/api/api_v1/endpoints/zhifu_guanli/zhifu_huidiao.py`
   - 支持API v2的XML格式回调
   - 自动识别环境并使用对应的验证方式

### 关键代码逻辑

```python
# 检查是否为沙箱环境
is_sandbox = peizhi.huanjing == "shachang"

if is_sandbox:
    # 使用沙箱工具类
    weixin_pay = WeixinPaySandboxUtil(...)
else:
    # 使用正式环境工具类
    weixin_pay = WeixinPayUtil(...)
```

## 测试建议

1. 在沙箱环境中测试完整的支付流程
2. 验证订单创建、支付、回调、查询等功能
3. 测试异常情况的处理（签名错误、订单不存在等）
4. 确认支付成功后订单状态和流水记录正确

## 常见问题

### Q: 沙箱环境支持哪些支付方式？
A: 目前只支持Native扫码支付。

### Q: 如何切换到正式环境？
A: 在支付配置中将"环境"字段改为"生产"，并填写正式环境的配置信息。

### Q: 沙箱密钥获取失败怎么办？
A: 检查商户号和API密钥是否正确，确保网络可以访问微信支付API。

### Q: 回调签名验证失败？
A: 确保使用的是沙箱密钥进行签名验证，系统会自动获取并使用沙箱密钥。

## 参考文档

- [微信支付沙箱环境文档](https://pay.weixin.qq.com/doc/v2/merchant/4011984810)
- [微信支付API v2统一下单](https://pay.weixin.qq.com/doc/v2/merchant/4011935214)

