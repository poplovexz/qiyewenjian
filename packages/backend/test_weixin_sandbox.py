#!/usr/bin/env python
"""
微信支付沙箱环境测试脚本
"""
import sys
sys.path.insert(0, 'src')

from utils.payment.weixin_pay_sandbox import WeixinPaySandboxUtil

def test_sandbox_util():
    """测试沙箱工具类基本功能"""
    print("=" * 60)
    print("微信支付沙箱环境工具类测试")
    print("=" * 60)
    
    # 初始化工具类 (使用测试参数)
    sandbox_util = WeixinPaySandboxUtil(
        appid="test_appid",
        mch_id="test_mch_id",
        api_key="test_api_key",
        notify_url="http://localhost:8000/api/v1/zhifu/huidiao/weixin/notify"
    )
    
    print("\n✅ 工具类初始化成功")
    print(f"   AppID: {sandbox_util.appid}")
    print(f"   商户号: {sandbox_util.mch_id}")
    print(f"   通知URL: {sandbox_util.notify_url}")
    
    # 测试生成随机字符串
    nonce_str = sandbox_util._generate_nonce_str()
    print(f"\n✅ 生成随机字符串: {nonce_str}")
    print(f"   长度: {len(nonce_str)}")
    
    # 测试签名生成
    test_params = {
        "appid": "test_appid",
        "mch_id": "test_mch_id",
        "nonce_str": "test_nonce",
        "body": "测试商品"
    }
    sign = sandbox_util._generate_sign(test_params, "test_key")
    print(f"\n✅ 生成签名: {sign}")
    print(f"   签名长度: {len(sign)}")
    
    # 测试字典转XML
    xml_str = sandbox_util._dict_to_xml(test_params)
    print("\n✅ 字典转XML:")
    print(f"   {xml_str[:100]}...")
    
    # 测试XML转字典
    test_xml = '<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>'
    result_dict = sandbox_util._xml_to_dict(test_xml)
    print("\n✅ XML转字典:")
    print(f"   {result_dict}")
    
    print("\n" + "=" * 60)
    print("所有基本功能测试通过!")
    print("=" * 60)

if __name__ == "__main__":
    test_sandbox_util()

