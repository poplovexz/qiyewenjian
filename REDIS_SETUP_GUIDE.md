# Redis 配置和使用指南

## 📊 当前状态

✅ **Redis 已成功配置并运行！**

### 系统信息
- **Redis版本**: 7.0.15
- **运行地址**: localhost:6379
- **运行状态**: Active (运行中)
- **运行时间**: 4天+
- **内存使用**: 1.00M
- **缓存命中率**: 95.00%

### 缓存统计
- **总键数**: 1
- **缓存命中**: 76次
- **缓存未命中**: 4次
- **命中率**: 95.00%

---

## 🔧 Redis 配置

### 环境变量配置

在 `packages/backend/.env` 中：

```env
# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# 缓存配置
CACHE_DEFAULT_TTL=900    # 默认缓存时间 (15分钟)
CACHE_LONG_TTL=86400     # 长期缓存时间 (24小时)
CACHE_SHORT_TTL=60       # 短期缓存时间 (1分钟)
```

### 连接URL格式

系统会自动生成Redis连接URL：
```
redis://localhost:6379/0
```

如果设置了密码：
```
redis://:password@localhost:6379/0
```

---

## 🚀 Redis 服务管理

### 启动/停止/重启

```bash
# 启动Redis
sudo systemctl start redis-server

# 停止Redis
sudo systemctl stop redis-server

# 重启Redis
sudo systemctl restart redis-server

# 查看状态
sudo systemctl status redis-server

# 开机自启
sudo systemctl enable redis-server
```

### 测试连接

```bash
# 测试Redis是否运行
redis-cli ping
# 应该返回: PONG

# 查看Redis信息
redis-cli INFO

# 查看所有键
redis-cli KEYS "*"

# 查看键数量
redis-cli DBSIZE
```

---

## 📈 缓存使用情况

### 当前缓存的数据

系统目前缓存了以下数据：

1. **线索来源列表** (`xiansuo:laiyuan:active`)
   - 缓存时间: 24小时
   - 用途: 加速线索来源下拉列表加载

### 缓存键命名规范

系统使用以下缓存键（定义在 `packages/backend/src/core/redis_client.py`）：

```python
# 线索管理相关
xiansuo:laiyuan:active          # 活跃的线索来源
xiansuo:zhuangtai:active        # 活跃的线索状态
xiansuo:list                    # 线索列表
xiansuo:detail                  # 线索详情
xiansuo:statistics              # 线索统计

# 用户权限相关
user:permissions                # 用户权限
role:permissions                # 角色权限
user:roles                      # 用户角色

# 系统相关
system:online_users             # 在线用户
system:config                   # 系统配置
```

---

## 🔍 监控和调试

### 查看健康状态

```bash
# 通过API查看Redis健康状态
curl http://localhost:8000/health | python3 -m json.tool
```

返回示例：
```json
{
    "status": "healthy",
    "cache": {
        "status": "healthy",
        "message": "Redis运行正常",
        "stats": {
            "status": "connected",
            "redis_version": "7.0.15",
            "used_memory": "1.00M",
            "connected_clients": 1,
            "total_keys": 1,
            "keyspace_hits": 76,
            "keyspace_misses": 4,
            "hit_rate": "95.00%"
        },
        "fallback_mode": false
    }
}
```

### 查看缓存内容

```bash
# 查看所有缓存键
redis-cli KEYS "*"

# 查看特定键的值
redis-cli GET "xiansuo:laiyuan:active"

# 查看键的TTL（剩余生存时间）
redis-cli TTL "xiansuo:laiyuan:active"

# 查看键的类型
redis-cli TYPE "xiansuo:laiyuan:active"
```

### 清理缓存

```bash
# 删除特定键
redis-cli DEL "xiansuo:laiyuan:active"

# 删除所有键（谨慎使用！）
redis-cli FLUSHDB

# 删除所有数据库的所有键（非常谨慎！）
redis-cli FLUSHALL
```

### 实时监控

```bash
# 实时监控Redis命令
redis-cli MONITOR

# 查看Redis统计信息
redis-cli INFO stats

# 查看内存使用
redis-cli INFO memory

# 查看客户端连接
redis-cli CLIENT LIST
```

---

## 🎯 缓存策略

### 缓存时间设置

系统使用三级缓存时间：

1. **短期缓存** (60秒)
   - 用于频繁变化的数据
   - 例如：实时统计数据

2. **默认缓存** (15分钟)
   - 用于一般数据
   - 例如：列表数据

3. **长期缓存** (24小时)
   - 用于很少变化的数据
   - 例如：配置数据、字典数据

### 缓存失效策略

系统在以下情况会自动清除缓存：

1. **数据更新时**
   - 创建、更新、删除操作会自动清除相关缓存

2. **手动清除**
   - 通过API或命令行手动清除

3. **TTL过期**
   - 缓存到期自动清除

---

## 🛠 开发者指南

### 使用缓存装饰器

```python
from core.cache_decorator import cache_result
from core.redis_client import CacheKeys

# 使用缓存装饰器
@cache_result(CacheKeys.XIANSUO_LAIYUAN_ACTIVE, ttl=86400)
async def get_active_laiyuan_list(self):
    # 这个函数的结果会被缓存24小时
    return await self.db.query(XiansuoLaiyuan).all()
```

### 手动使用Redis客户端

```python
from core.redis_client import redis_client

# 设置缓存
await redis_client.set("my_key", {"data": "value"}, ttl=3600)

# 获取缓存
data = await redis_client.get("my_key")

# 删除缓存
await redis_client.delete("my_key")

# 检查键是否存在
exists = await redis_client.exists("my_key")
```

### 缓存失效

```python
from core.cache_decorator import invalidate_xiansuo_laiyuan_cache

# 清除线索来源缓存
await invalidate_xiansuo_laiyuan_cache()
```

---

## 🔒 安全配置

### 生产环境建议

1. **设置密码**
```bash
# 编辑Redis配置
sudo vim /etc/redis/redis.conf

# 添加或修改
requirepass your-strong-password

# 重启Redis
sudo systemctl restart redis-server
```

2. **更新环境变量**
```env
REDIS_PASSWORD=your-strong-password
```

3. **限制访问**
```bash
# 只允许本地访问
bind 127.0.0.1

# 或指定IP
bind 127.0.0.1 192.168.1.100
```

4. **禁用危险命令**
```bash
# 在redis.conf中
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

---

## 📊 性能优化

### 内存优化

```bash
# 设置最大内存
maxmemory 256mb

# 设置内存淘汰策略
maxmemory-policy allkeys-lru
```

### 持久化配置

Redis支持两种持久化方式：

1. **RDB（快照）**
```bash
# 每900秒（15分钟）至少1个键变化时保存
save 900 1
# 每300秒（5分钟）至少10个键变化时保存
save 300 10
# 每60秒至少10000个键变化时保存
save 60 10000
```

2. **AOF（追加文件）**
```bash
# 启用AOF
appendonly yes
# 每秒同步一次
appendfsync everysec
```

---

## 🐛 故障排查

### Redis无法启动

```bash
# 查看日志
sudo journalctl -u redis-server -n 50

# 检查配置文件
redis-server /etc/redis/redis.conf --test-memory 1024

# 检查端口占用
sudo netstat -tlnp | grep 6379
```

### 连接被拒绝

```bash
# 检查Redis是否运行
sudo systemctl status redis-server

# 检查防火墙
sudo ufw status

# 测试连接
telnet localhost 6379
```

### 内存不足

```bash
# 查看内存使用
redis-cli INFO memory

# 清理过期键
redis-cli --scan --pattern "*" | xargs redis-cli DEL

# 或设置最大内存限制
redis-cli CONFIG SET maxmemory 256mb
```

---

## 📝 常用命令速查

```bash
# 服务管理
sudo systemctl start redis-server      # 启动
sudo systemctl stop redis-server       # 停止
sudo systemctl restart redis-server    # 重启
sudo systemctl status redis-server     # 状态

# 连接测试
redis-cli ping                         # 测试连接
redis-cli INFO                         # 查看信息
redis-cli DBSIZE                       # 键数量

# 键操作
redis-cli KEYS "*"                     # 所有键
redis-cli GET key                      # 获取值
redis-cli SET key value                # 设置值
redis-cli DEL key                      # 删除键
redis-cli TTL key                      # 查看TTL
redis-cli EXISTS key                   # 检查存在

# 监控
redis-cli MONITOR                      # 实时监控
redis-cli INFO stats                   # 统计信息
redis-cli CLIENT LIST                  # 客户端列表

# 清理
redis-cli FLUSHDB                      # 清空当前数据库
redis-cli FLUSHALL                     # 清空所有数据库
```

---

## ✅ 验证清单

- [x] Redis服务已安装
- [x] Redis服务正在运行
- [x] 后端可以连接Redis
- [x] 缓存功能正常工作
- [x] 缓存命中率良好 (95%)
- [x] 健康检查通过

---

## 📚 相关文档

- [Redis官方文档](https://redis.io/documentation)
- [Redis命令参考](https://redis.io/commands)
- [后端配置文档](./docs/DEPLOYMENT.md)
- [测试配置](./test-config.md)

---

**最后更新**: 2025-10-31
**Redis版本**: 7.0.15
**状态**: ✅ 运行正常

