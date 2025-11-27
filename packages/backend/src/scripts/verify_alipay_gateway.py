#!/usr/bin/env python3
"""验证 AlipayUtil 的网关选择与支付URL构造逻辑

运行：
  python packages/backend/src/scripts/verify_alipay_gateway.py
"""

import sys
from pathlib import Path
import importlib
import importlib.util

# 确保可导入 backend 源码（指向 packages/backend/src）
sys.path.insert(0, str(Path(__file__).parent.parent))

# 直接按文件路径加载 alipay.py，避免触发 utils/payment/__init__.py 的依赖
ALIPAY_PATH = Path(__file__).parent.parent / 'utils' / 'payment' / 'alipay.py'
spec = importlib.util.spec_from_file_location('alipay_util_module', ALIPAY_PATH)
alipay_module = importlib.util.module_from_spec(spec)
sys.modules['alipay_util_module'] = alipay_module
assert spec and spec.loader
spec.loader.exec_module(alipay_module)

# 关闭真实SDK初始化，避免对环境和密钥的依赖
alipay_module.ALIPAY_SDK_AVAILABLE = False
AlipayUtil = alipay_module.AlipayUtil


class StubAlipay:
    """用于模拟支付宝SDK返回的 order_string"""

    def api_alipay_trade_page_pay(self, **kwargs):
        # 返回一个可拼接到网关后的订单串
        return "method=alipay.trade.page.pay&biz_content=%7B...%7D&timestamp=2025-01-01+00%3A00%3A00"

    def api_alipay_trade_wap_pay(self, **kwargs):
        return "method=alipay.trade.wap.pay&biz_content=%7B...%7D&timestamp=2025-01-01+00%3A00%3A00"


def assert_equal(name: str, actual: str, expected: str):
    if actual != expected:
        print(f"❌ {name} 不匹配\n   期望: {expected}\n   实际: {actual}")
        return False
    print(f"✓ {name} 正确: {actual}")
    return True


def main() -> int:
    ok = True

    # 用例A：沙箱环境（debug=True）即使提供生产网关也应强制使用官方沙箱网关
    util_sandbox = AlipayUtil(
        appid="test_appid",
        app_private_key="-----BEGIN RSA PRIVATE KEY-----\nMIIB...\n-----END RSA PRIVATE KEY-----",
        alipay_public_key="-----BEGIN PUBLIC KEY-----\nMIIB...\n-----END PUBLIC KEY-----",
        notify_url="https://example.com/notify",
        debug=True,
        gateway_url="https://openapi.alipay.com/gateway.do",  # 提供生产网关，期望被忽略
    )
    ok &= assert_equal(
        "沙箱环境网关",
        util_sandbox.gateway_url,
        "https://openapi.alipaydev.com/gateway.do",
    )

    # 用例B：生产环境（debug=False）使用自定义网关
    custom_gateway = "https://custom.alipay.gateway/gateway.do"
    util_prod_custom = AlipayUtil(
        appid="test_appid",
        app_private_key="-----BEGIN RSA PRIVATE KEY-----\nMIIB...\n-----END RSA PRIVATE KEY-----",
        alipay_public_key="-----BEGIN PUBLIC KEY-----\nMIIB...\n-----END PUBLIC KEY-----",
        notify_url="https://example.com/notify",
        debug=False,
        gateway_url=custom_gateway,
    )
    ok &= assert_equal(
        "生产环境自定义网关",
        util_prod_custom.gateway_url,
        custom_gateway,
    )

    # 用例C：生产环境（debug=False）未提供网关使用默认官方网关
    util_prod_default = AlipayUtil(
        appid="test_appid",
        app_private_key="-----BEGIN RSA PRIVATE KEY-----\nMIIB...\n-----END RSA PRIVATE KEY-----",
        alipay_public_key="-----BEGIN PUBLIC KEY-----\nMIIB...\n-----END PUBLIC KEY-----",
        notify_url="https://example.com/notify",
        debug=False,
        gateway_url=None,
    )
    ok &= assert_equal(
        "生产环境默认网关",
        util_prod_default.gateway_url,
        "https://openapi.alipay.com/gateway.do",
    )

    # 验证 URL 构造：沙箱环境下 page/wap 均需使用沙箱网关前缀
    util_sandbox.alipay = StubAlipay()  # 注入桩对象以生成订单串
    page_res = util_sandbox.create_page_pay(
        out_trade_no="ORDER123",
        subject="合同支付测试",
        total_amount=0.01,
        body="测试订单",
        return_url="https://example.com/return",
    )
    expected_prefix = "https://openapi.alipaydev.com/gateway.do?"
    actual_url = page_res.get("pay_url", "")
    if not actual_url.startswith(expected_prefix):
        print(
            f"❌ 网页支付URL网关前缀错误\n   期望前缀: {expected_prefix}\n   实际: {actual_url}"
        )
        ok = False
    else:
        print(f"✓ 网页支付URL前缀正确: {actual_url[:len(expected_prefix)+20]}...")

    wap_res = util_sandbox.create_wap_pay(
        out_trade_no="ORDER456",
        subject="合同支付测试",
        total_amount=0.02,
        body="测试订单",
        return_url="https://example.com/return",
        quit_url="https://example.com/quit",
    )
    actual_wap_url = wap_res.get("data", {}).get("pay_url", "")
    if not actual_wap_url.startswith(expected_prefix):
        print(
            f"❌ 手机网站支付URL网关前缀错误\n   期望前缀: {expected_prefix}\n   实际: {actual_wap_url}"
        )
        ok = False
    else:
        print(f"✓ 手机网站支付URL前缀正确: {actual_wap_url[:len(expected_prefix)+20]}...")

    print("\n验证结果：" + ("✅ 通过" if ok else "❌ 未通过"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
