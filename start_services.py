#!/usr/bin/env python3
"""启动开发环境服务"""

import subprocess
import time
import sys
import os
import signal
import tempfile
import shlex

def kill_processes():
    """清理旧进程"""
    print("清理旧进程...")
    # BAN-B602: 使用列表参数替代 shell=True
    # BAN-B607: 使用完整路径
    for proc_name in ["node", "uvicorn", "python3"]:
        try:
            subprocess.run(["/usr/bin/pkill", "-9", proc_name],
                         capture_output=True, check=False)
        except Exception:
            pass  # 忽略进程不存在的错误
    time.sleep(3)
    print("✅ 进程已清理\n")

def start_backend():
    """启动后端服务"""
    print("启动后端服务 (端口 8000)...")

    # BAN-B108: 使用 tempfile 获取临时目录
    temp_dir = tempfile.gettempdir()
    backend_log = os.path.join(temp_dir, "backend_dev.log")

    # 注意: 这里需要 shell=True 因为需要 source 虚拟环境
    # 这是开发脚本，输入是硬编码的，不存在注入风险
    backend_cmd = """
    cd /var/www/packages/backend && \
    source venv/bin/activate && \
    export PYTHONPATH=/var/www/packages/backend/src && \
    python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    """

    with open(backend_log, 'w') as log:
        proc = subprocess.Popen(
            backend_cmd,
            shell=True,  # nosec B602 - 硬编码命令，无注入风险
            stdout=log,
            stderr=subprocess.STDOUT,
            executable='/bin/bash'
        )

    print(f"后端进程 PID: {proc.pid}")
    time.sleep(8)

    # 检查健康状态
    # BAN-B607: 使用完整路径
    try:
        # PYL-W1510: 故意不使用 check=True，因为需要检查输出内容判断健康状态
        result = subprocess.run(
            ["/usr/bin/curl", "-s", "http://localhost:8000/health"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        if "healthy" in result.stdout:
            print("✅ 后端启动成功")
            print("   地址: http://localhost:8000\n")
            return proc.pid
        else:
            print("❌ 后端启动失败")
            print(f"   查看日志: tail -f {backend_log}\n")
            return None
    except Exception as e:
        print(f"❌ 后端健康检查失败: {e}")
        return None

def start_frontend():
    """启动前端服务"""
    print("启动前端服务...")

    # BAN-B108: 使用 tempfile 获取临时目录
    temp_dir = tempfile.gettempdir()
    frontend_log = os.path.join(temp_dir, "frontend_dev.log")

    # 注意: 这里需要 shell=True 因为需要 cd 和 npm 命令组合
    # 这是开发脚本，输入是硬编码的，不存在注入风险
    frontend_cmd = "cd /var/www/packages/frontend && npm run dev"

    with open(frontend_log, 'w') as log:
        proc = subprocess.Popen(
            frontend_cmd,
            shell=True,  # nosec B602 - 硬编码命令，无注入风险
            stdout=log,
            stderr=subprocess.STDOUT,
            executable='/bin/bash'
        )

    print(f"前端进程 PID: {proc.pid}")
    time.sleep(10)

    # 检查日志
    try:
        with open(frontend_log, 'r') as f:
            log_content = f.read()

        if "ready in" in log_content:
            print("✅ 前端启动成功")
            # 尝试提取URL
            for line in log_content.split('\n'):
                if 'Local:' in line and 'http' in line:
                    print(f"   {line.strip()}")
            print()
            return proc.pid
        elif "already in use" in log_content:
            print("❌ 前端启动失败: 端口被占用")
            print(f"   查看日志: tail -f {frontend_log}\n")
            return None
        else:
            print("⚠️  前端可能还在启动中...")
            print(f"   查看日志: tail -f {frontend_log}\n")
            return proc.pid
    except Exception as e:
        print(f"❌ 读取前端日志失败: {e}")
        return None

def main():
    print("=" * 50)
    print("重启本地开发环境")
    print("=" * 50)
    print()
    
    # 清理进程
    kill_processes()
    
    # 启动后端
    backend_pid = start_backend()
    if not backend_pid:
        print("后端启动失败，退出")
        sys.exit(1)
    
    # 启动前端
    frontend_pid = start_frontend()
    
    # 显示总结
    print("=" * 50)
    print("✅ 开发环境启动完成")
    print("=" * 50)
    print()
    print("📊 服务状态:")
    print("   后端: http://localhost:8000")
    print("   前端: http://localhost:5174")
    print()
    print("📝 日志文件:")
    print("   后端: tail -f /tmp/backend_dev.log")
    print("   前端: tail -f /tmp/frontend_dev.log")
    print()
    print("🔍 进程信息:")
    if backend_pid:
        print(f"   后端 PID: {backend_pid}")
    if frontend_pid:
        print(f"   前端 PID: {frontend_pid}")
    print()
    print("🛑 停止服务:")
    print("   pkill -9 node; pkill -9 uvicorn")
    print()
    
    # 显示进程列表
    print("当前运行的服务进程:")
    # BAN-B602: 使用 Python 实现进程过滤，避免 shell=True
    try:
        # PYL-W1510: 故意不使用 check=True，因为只是获取进程列表用于显示
        ps_result = subprocess.run(
            ["/bin/ps", "aux"],
            capture_output=True,
            text=True,
            check=False
        )
        for line in ps_result.stdout.split('\n'):
            if ('uvicorn' in line or 'vite' in line) and 'grep' not in line:
                print(line)
    except Exception:
        pass

if __name__ == "__main__":
    main()

