#!/usr/bin/env python3
"""
初始化系统设置相关权限的脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from core.config import settings

def init_system_permissions():
    """初始化系统设置相关权限"""
    
    engine = create_engine(str(settings.DATABASE_URL))
    
    try:
        with engine.connect() as conn:
            # 系统设置权限数据
            permissions_sql = """
            INSERT INTO quanxian (
                id, quanxian_ming, quanxian_bianma, miaoshu,
                ziyuan_leixing, ziyuan_lujing, zhuangtai,
                created_by, created_at, updated_at, is_deleted
            ) VALUES
            -- 系统设置主权限
            (
                'perm_system_settings', '系统设置', 'system:settings', '系统设置模块主权限',
                'menu', '/settings/system', 'active',
                'system', NOW(), NOW(), 'N'
            ),

            -- 系统配置权限
            (
                'perm_system_config_read', '查看系统配置', 'system:config:read', '查看系统配置信息',
                'api', '/api/v1/system/configs', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'perm_system_config_update', '更新系统配置', 'system:config:update', '更新系统配置',
                'api', '/api/v1/system/configs', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            
            -- 系统信息权限
            (
                'perm_system_info_read', '查看系统信息', 'system:info:read', '查看系统基本信息',
                'api', '/api/v1/system/info', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            
            -- 缓存管理权限
            (
                'perm_system_cache_clear', '清除系统缓存', 'system:cache:clear', '清除系统缓存',
                'api', '/api/v1/system/cache/clear', 'active',
                'system', NOW(), NOW(), 'N'
            )
            ON CONFLICT (quanxian_bianma) DO NOTHING;
            """
            
            conn.execute(text(permissions_sql))
            conn.commit()
            
            # 为管理员角色分配权限
            role_permissions_sql = """
            INSERT INTO jiaose_quanxian (id, jiaose_id, quanxian_id, created_at, updated_at, is_deleted)
            SELECT 
                'rp_admin_' || q.id,
                (SELECT id FROM jiaose WHERE jiaose_bianma = 'admin' LIMIT 1),
                q.id,
                NOW(),
                NOW(),
                'N'
            FROM quanxian q
            WHERE q.quanxian_bianma LIKE 'system:%'
            AND NOT EXISTS (
                SELECT 1 FROM jiaose_quanxian rp
                WHERE rp.jiaose_id = (SELECT id FROM jiaose WHERE jiaose_bianma = 'admin' LIMIT 1)
                AND rp.quanxian_id = q.id
            );
            """
            
            conn.execute(text(role_permissions_sql))
            conn.commit()
            
    except Exception as e:
        raise

if __name__ == "__main__":
    init_system_permissions()
