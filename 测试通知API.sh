#!/bin/bash

echo "=========================================="
echo "测试通知API"
echo "=========================================="
echo ""

# 获取token（需要先登录）
echo "1. 测试登录获取token..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "yonghu_ming": "admin",
    "mima": "admin123"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ 登录失败，无法获取token"
  echo "响应: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ 登录成功，获取到token"
echo ""

# 测试获取未读通知数量
echo "2. 测试获取未读通知数量..."
UNREAD_COUNT=$(curl -s -X GET "http://localhost:8000/api/v1/notifications/my/unread-count" \
  -H "Authorization: Bearer $TOKEN")

echo "响应: $UNREAD_COUNT"
echo ""

# 测试获取我的通知列表
echo "3. 测试获取我的通知列表..."
MY_NOTIFICATIONS=$(curl -s -X GET "http://localhost:8000/api/v1/notifications/my?page=1&size=10" \
  -H "Authorization: Bearer $TOKEN")

echo "响应: $MY_NOTIFICATIONS" | head -c 500
echo "..."
echo ""

# 测试获取所有通知列表（需要权限）
echo "4. 测试获取所有通知列表..."
ALL_NOTIFICATIONS=$(curl -s -X GET "http://localhost:8000/api/v1/notifications?page=1&size=10" \
  -H "Authorization: Bearer $TOKEN")

echo "响应: $ALL_NOTIFICATIONS" | head -c 500
echo "..."
echo ""

# 检查API文档
echo "5. 检查API文档中的通知相关接口..."
echo "请访问: http://localhost:8000/docs"
echo "搜索 'notifications' 查看所有通知相关接口"
echo ""

echo "=========================================="
echo "测试完成"
echo "=========================================="
echo ""
echo "API路径总结:"
echo "  - 获取未读数量: GET /api/v1/notifications/my/unread-count"
echo "  - 获取我的通知: GET /api/v1/notifications/my"
echo "  - 获取所有通知: GET /api/v1/notifications"
echo "  - 获取通知详情: GET /api/v1/notifications/{id}"
echo "  - 标记为已读:   POST /api/v1/notifications/{id}/read"
echo ""

