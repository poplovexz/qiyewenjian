#!/bin/bash
echo "🔍 监控合同作废请求..."
echo "请在前端点击作废按钮，我将捕获详细的错误信息"
echo "按 Ctrl+C 停止监控"
echo ""
tail -f /tmp/backend_new.log | grep --line-buffered -A 20 "void\|ERROR\|Exception\|Traceback"

