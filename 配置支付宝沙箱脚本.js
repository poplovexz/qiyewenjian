// 在浏览器控制台执行此脚本来配置支付宝沙箱
// 前提: 你已经登录到系统 (http://localhost:5174)

async function configureAlipaySandbox() {
  try {
    console.log('🚀 开始配置支付宝沙箱...');
    
    // 支付宝沙箱配置数据
    const config = {
      peizhi_mingcheng: "支付宝沙箱环境",
      peizhi_leixing: "zhifubao",
      huanjing: "shachang",
      zhuangtai: "qiyong",
      zhifubao_appid: "9021000157698401",
      zhifubao_wangguan: "https://openapi-sandbox.dl.alipaydev.com/gateway.do",
      zhifubao_yingyong_siyao: "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCD28PhQ0UT/cZwrAuFP2QyzpPfr1Tdfv557OJ9nd5Q6e4bQMcqcICDeM92WsnDbo9UNpXkyDP6EJ4thPr5UGIR4Rv5rHEQUPQ4nlTMtBCS/FW5PkSzGTgrPljZG/MRQgeuVHrlc/7slE6YdiWGrTYT5WtoGb7oyxp+bfA+Z9G+IPxypgFoqSkQebEVQKwpDVUmYDeW9GzZR2vmr/RajOzWP3inH4FOQFUzrVo4CNBJ+dG0iFdJ0ABbsnNgd4ryPM/KE4WWH3EvMxs9s72AYEaq4Ilu6Q04nNtLkmbVwQVj0Gb0XMLetG0nufFOgM58JTTlSlyz4t4OkBa1hN9qmc6lAgMBAAECggEAdSk4i1eycWj0gfjc47DH3z0et4qa5ZSJmNybAvLbLxosr5qHXXZJOoiGDqvsyvHZ+QHnfjlFtdQ+OEQInK6H9UsICHjonY7Q8d39i0YT1AbSRJ7HfDvUZNgpKgBjodoB6Sy3ZloDEUNV8rJH9brCajtXjFAUCdUt3VjiNxEYlM54LR23gE84BcjfPXzbcrgpbB/4dWEgwd0Var+muVnVUGxzScSf71dl4GzIniKIJCqOtSFq1e5byEm+s/xotGWzDBXr9+eVl2zcJrK4dnRM1G3dB54ws/e5XUtafghthgELsVdhd22u91eFOa4H8Ybk68M92K7ln3RFZhUMwxFoAQKBgQDwSFdP4JMzLNd5aCNWdz/b44b7kEGzI241rrZEtbNZWFtMym44L4PfWoieZOw2PtBNb+1JJI/fKdJQCTiuQJM4P8M9Buehd3sA37O9HX2w25MmqyWKZ27XKOmrjHJw/Kg14lnJFBXACrRj8rCO5HxLo4BHt7t1xxoS/Ebj3HZE5QKBgQCMe84FxYhmsQVEsjs5j4gQ0tO6VQOWtBB3bIgd5X1C+n1apUP4h2durKRlHlxoNsK8/38qdb+luFcNFqAM6Ha9MvuqPDO1Ijy/TBqF65qUFVAxZca1xLpR1pn/Fl5R8G40/7W7FtYTVFmobxt4HK01bD0LZs18Z0f9xQNgoeCGwQKBgBAljFh9yuaBeOlbqiRBVzU7kPKOuxuCogFRgEYVv7udSGVcpRN5fe8gclXSil0K04ygnN1xa4mfkdZ3CCwNgtcg0cnkEOS01rs0TSvEM5IS70yF67vlP3mN8kXo5jfZgqQ8VbRBeUSyc3TT9jFkAUZD8nbfTeWYP5RPB6SASCJRAoGADeExgrp4doTo21esqEw5Ckh6KL+7ggk6U0JC1IlW7eYnumv3ojdmjbW67E6qnJVEej3YB47op2vmFeH1YDEbgifmW3RlO3EthUz0leSoOhc8/BRtJIpSSkGkp2JDYV8a1FurTde8wN4lmZGYqi5TIqMWCOlYRgFCSJ1Nbx+vOkECgYAFnk12gncR5Z+mmy8b/Q2h+uyIK8ygkY+2lDlyGxjA46AkRkiI5AHVR99qjjwhcDidCuYja+4piRWCiOXpTjcP2eFFxTBoWBPz91IxUE52Kz74slxbWu9Afi0mU9dQEicKX85sCwCxwNMYqYZKaij2omQgE7B+uinA78qCIQpPcA==",
      zhifubao_gongyao: "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA7bFHB2ZiVrzVuwE2YIkrh7Cz0yrY4xUp+6fdCdq91LKrvsBJQeXYVsnZWQm57TctiWbZTQpqLPxBHOdfDdpdt0v9k6XOubWSwjXpAE0iEYpZ1oNZMP7wgpDXN/UGR/o8+QORUypFUeSlFX+n6RzIjPaD2dcjVnE6m5iTWX0PL3chkSgJY/AnOd2IGGOQsVhcci4jcAJ3gOi/4E+ZN0xMTSUPCMTdhvBYGNMkqMT741MyAPGOJvZ1/TuROZqxnIvGH3ZUkGsPWS7cC6dRz/NspkTdh69kq6Y03FKhw0XnGv25mzrPp/zFW6lRIT51Uq3GupDxcWBxkBBgSfqHp3zTXwIDAQAB",
      beizhu: "支付宝沙箱测试环境，用于开发测试"
    };

    // 获取token (从localStorage或sessionStorage)
    const token = localStorage.getItem('token') || sessionStorage.getItem('token');
    
    if (!token) {
      console.error('❌ 未找到登录token，请先登录系统');
      return;
    }

    console.log('📡 发送配置请求...');
    
    // 发送POST请求
    const response = await fetch('http://localhost:8000/api/v1/payment-configs/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(config)
    });

    if (!response.ok) {
      const error = await response.json();
      console.error('❌ 配置失败:', error);
      throw new Error(JSON.stringify(error));
    }

    const result = await response.json();
    console.log('✅ 支付宝沙箱配置成功!');
    console.log('配置详情:', result);
    
    alert('✅ 支付宝沙箱配置成功！\n\n现在可以在合同签署页面测试支付功能了。');
    
    return result;
    
  } catch (error) {
    console.error('❌ 配置过程出错:', error);
    alert('❌ 配置失败: ' + error.message);
    throw error;
  }
}

// 执行配置
configureAlipaySandbox();

