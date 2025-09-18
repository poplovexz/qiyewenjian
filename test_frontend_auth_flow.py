#!/usr/bin/env python3
"""
测试前端认证流程
"""

import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_frontend_auth_flow():
    """测试前端认证流程"""
    print("🌐 测试前端认证流程...")
    print("=" * 50)
    
    # 配置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = None
    
    try:
        # 启动浏览器
        print("🚀 启动浏览器...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        # 1. 访问客户列表页面（未登录）
        print("\n1️⃣ 访问客户列表页面（未登录状态）...")
        driver.get("http://localhost:5174/customers")
        time.sleep(2)
        
        current_url = driver.current_url
        print(f"当前URL: {current_url}")
        
        if "/login" in current_url:
            print("✅ 未登录用户被正确重定向到登录页面")
        else:
            print("⚠️ 未登录用户没有被重定向到登录页面")
        
        # 2. 执行登录
        print("\n2️⃣ 执行登录...")
        
        # 确保在登录页面
        if "/login" not in current_url:
            driver.get("http://localhost:5174/login")
            time.sleep(2)
        
        try:
            # 查找登录表单元素
            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'], input[placeholder*='用户名'], input[placeholder*='账号']"))
            )
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[placeholder*='密码']")
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button:contains('登录'), .el-button--primary")
            
            # 输入登录信息
            username_input.clear()
            username_input.send_keys("admin")
            
            password_input.clear()
            password_input.send_keys("admin123")
            
            print("✅ 找到登录表单，输入用户名和密码")
            
            # 点击登录按钮
            login_button.click()
            print("✅ 点击登录按钮")
            
            # 等待登录完成
            time.sleep(3)
            
            current_url = driver.current_url
            print(f"登录后URL: {current_url}")
            
            if "/login" not in current_url:
                print("✅ 登录成功，已跳转到主页面")
            else:
                print("❌ 登录可能失败，仍在登录页面")
                
                # 检查是否有错误消息
                try:
                    error_elements = driver.find_elements(By.CSS_SELECTOR, ".el-message--error, .error-message, .alert-danger")
                    if error_elements:
                        for error in error_elements:
                            if error.is_displayed():
                                print(f"错误消息: {error.text}")
                except:
                    pass
                
                return False
            
        except TimeoutException:
            print("❌ 无法找到登录表单元素")
            print("页面源码片段:")
            print(driver.page_source[:500] + "...")
            return False
        except Exception as e:
            print(f"❌ 登录过程中发生异常: {e}")
            return False
        
        # 3. 访问客户列表页面（已登录）
        print("\n3️⃣ 访问客户列表页面（已登录状态）...")
        driver.get("http://localhost:5174/customers")
        time.sleep(3)
        
        current_url = driver.current_url
        print(f"当前URL: {current_url}")
        
        if "/customers" in current_url:
            print("✅ 已登录用户可以正常访问客户列表页面")
            
            # 4. 检查页面内容
            print("\n4️⃣ 检查页面内容...")
            
            try:
                # 等待页面加载
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                page_text = driver.find_element(By.TAG_NAME, "body").text
                
                if "客户管理" in page_text or "客户列表" in page_text:
                    print("✅ 页面包含客户管理相关内容")
                else:
                    print("⚠️ 页面可能不包含客户管理内容")
                
                # 检查是否有客户数据
                if "北京科技创新" in page_text or "上海智能制造" in page_text:
                    print("✅ 页面显示了客户数据")
                elif "暂无数据" in page_text or "没有数据" in page_text:
                    print("⚠️ 页面显示暂无数据")
                elif "加载中" in page_text or "loading" in page_text.lower():
                    print("⚠️ 页面仍在加载中")
                else:
                    print("❓ 无法确定页面数据状态")
                
                # 检查是否有错误信息
                if "错误" in page_text or "error" in page_text.lower():
                    print("⚠️ 页面可能包含错误信息")
                
                # 检查表格元素
                try:
                    table_elements = driver.find_elements(By.CSS_SELECTOR, ".el-table, table, .table")
                    if table_elements:
                        print(f"✅ 找到 {len(table_elements)} 个表格元素")
                    else:
                        print("⚠️ 未找到表格元素")
                except:
                    pass
                
                print(f"\n页面文本长度: {len(page_text)} 字符")
                if len(page_text) > 100:
                    print("页面内容预览:")
                    print(page_text[:200] + "..." if len(page_text) > 200 else page_text)
                
                return True
                
            except Exception as e:
                print(f"❌ 检查页面内容时发生异常: {e}")
                return False
        else:
            print("❌ 已登录用户无法访问客户列表页面")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        return False
    finally:
        if driver:
            driver.quit()
            print("\n🔚 浏览器已关闭")

def main():
    """主函数"""
    print("🎯 前端认证流程测试")
    print("=" * 50)
    
    # 检查Selenium是否可用
    try:
        from selenium import webdriver
        print("✅ Selenium可用")
    except ImportError:
        print("❌ Selenium未安装，请运行: pip install selenium")
        print("💡 或者直接在浏览器中测试:")
        print("   1. 访问 http://localhost:5174/customers")
        print("   2. 如果跳转到登录页，使用 admin/admin123 登录")
        print("   3. 登录后再次访问客户列表页面")
        return False
    
    success = test_frontend_auth_flow()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 前端认证流程测试完成！")
        print("\n💡 如果客户列表仍然为空，请检查:")
        print("   1. 浏览器开发者工具的控制台错误")
        print("   2. 网络请求是否成功")
        print("   3. API响应数据格式是否正确")
    else:
        print("❌ 前端认证流程测试失败")
        print("\n💡 手动测试步骤:")
        print("   1. 打开 http://localhost:5174/login")
        print("   2. 使用 admin/admin123 登录")
        print("   3. 访问 http://localhost:5174/customers")
    
    return success

if __name__ == "__main__":
    main()
