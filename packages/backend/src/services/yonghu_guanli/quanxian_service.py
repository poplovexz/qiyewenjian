"""
权限管理业务逻辑服务
"""
import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from models.yonghu_guanli.quanxian import Quanxian
from models.yonghu_guanli.jiaose_quanxian import JiaoseQuanxian
from schemas.yonghu_guanli.quanxian_schemas import (
    QuanxianCreate,
    QuanxianUpdate,
    QuanxianResponse,
    QuanxianListResponse,
    QuanxianListItem,
    QuanxianTreeResponse,
    QuanxianStatistics
)


class QuanxianService:
    """权限管理服务类"""

    @staticmethod
    async def get_quanxian_list(
        db: Session,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        ziyuan_leixing: Optional[str] = None,
        zhuangtai: Optional[str] = None
    ) -> QuanxianListResponse:
        """获取权限列表"""
        
        # 构建查询条件
        conditions = ["q.is_deleted = 'N'"]
        params = {}
        
        if search:
            conditions.append("(q.quanxian_ming ILIKE :search OR q.quanxian_bianma ILIKE :search)")
            params["search"] = f"%{search}%"
        
        if ziyuan_leixing:
            conditions.append("q.ziyuan_leixing = :ziyuan_leixing")
            params["ziyuan_leixing"] = ziyuan_leixing
        
        if zhuangtai:
            conditions.append("q.zhuangtai = :zhuangtai")
            params["zhuangtai"] = zhuangtai
        
        where_clause = " AND ".join(conditions)
        
        # 查询总数
        count_query = f"""
            SELECT COUNT(DISTINCT q.id)
            FROM quanxian q
            WHERE {where_clause}
        """
        total = db.execute(text(count_query), params).scalar()
        
        # 查询数据
        offset = (page - 1) * size
        data_query = f"""
            SELECT 
                q.id,
                q.quanxian_ming,
                q.quanxian_bianma,
                q.miaoshu,
                q.ziyuan_leixing,
                q.ziyuan_lujing,
                q.zhuangtai,
                q.created_at,
                q.updated_at,
                COALESCE(role_count.cnt, 0) as role_count
            FROM quanxian q
            LEFT JOIN (
                SELECT jq.quanxian_id, COUNT(*) as cnt
                FROM jiaose_quanxian jq
                WHERE jq.is_deleted = 'N'
                GROUP BY jq.quanxian_id
            ) role_count ON q.id = role_count.quanxian_id
            WHERE {where_clause}
            ORDER BY q.ziyuan_leixing, q.quanxian_bianma
            LIMIT :size OFFSET :offset
        """
        params.update({"size": size, "offset": offset})
        
        result = db.execute(text(data_query), params).fetchall()
        
        items = []
        for row in result:
            items.append(QuanxianListItem(
                id=row.id,
                quanxian_ming=row.quanxian_ming,
                quanxian_bianma=row.quanxian_bianma,
                miaoshu=row.miaoshu,
                ziyuan_leixing=row.ziyuan_leixing,
                ziyuan_lujing=row.ziyuan_lujing,
                zhuangtai=row.zhuangtai,
                created_at=row.created_at,
                updated_at=row.updated_at,
                role_count=row.role_count
            ))
        
        pages = (total + size - 1) // size
        
        return QuanxianListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )

    @staticmethod
    async def get_quanxian_tree(
        db: Session,
        zhuangtai: Optional[str] = "active"
    ) -> List[QuanxianTreeResponse]:
        """获取权限树形结构"""
        
        # 查询所有权限
        conditions = ["is_deleted = 'N'"]
        params = {}
        
        if zhuangtai:
            conditions.append("zhuangtai = :zhuangtai")
            params["zhuangtai"] = zhuangtai
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT id, quanxian_ming, quanxian_bianma, ziyuan_leixing
            FROM quanxian
            WHERE {where_clause}
            ORDER BY ziyuan_leixing, quanxian_bianma
        """
        
        result = db.execute(text(query), params).fetchall()
        
        # 构建树形结构
        tree = {}
        
        for row in result:
            # 按模块分组（从权限编码中提取模块名）
            parts = row.quanxian_bianma.split(':')
            module = parts[0] if len(parts) > 1 else 'system'
            
            if module not in tree:
                tree[module] = {
                    'id': f'module_{module}',
                    'label': f'{module.title()}模块',
                    'children': {},
                    'is_permission': False
                }
            
            # 按资源类型分组
            resource_type = row.ziyuan_leixing
            if resource_type not in tree[module]['children']:
                type_labels = {
                    'menu': '菜单权限',
                    'button': '按钮权限',
                    'api': '接口权限'
                }
                tree[module]['children'][resource_type] = {
                    'id': f'{module}_{resource_type}',
                    'label': type_labels.get(resource_type, resource_type),
                    'children': [],
                    'is_permission': False
                }
            
            # 添加权限节点
            tree[module]['children'][resource_type]['children'].append({
                'id': row.id,
                'label': row.quanxian_ming,
                'quanxian_bianma': row.quanxian_bianma,
                'ziyuan_leixing': row.ziyuan_leixing,
                'children': [],
                'is_permission': True
            })
        
        # 转换为列表格式
        tree_list = []
        for module_key, module_data in tree.items():
            children = []
            for type_key, type_data in module_data['children'].items():
                children.append(QuanxianTreeResponse(
                    id=type_data['id'],
                    label=type_data['label'],
                    children=[
                        QuanxianTreeResponse(**perm) 
                        for perm in type_data['children']
                    ],
                    is_permission=False
                ))
            
            tree_list.append(QuanxianTreeResponse(
                id=module_data['id'],
                label=module_data['label'],
                children=children,
                is_permission=False
            ))
        
        return tree_list

    @staticmethod
    async def get_quanxian_by_id(db: Session, quanxian_id: str) -> Optional[QuanxianResponse]:
        """根据ID获取权限详情"""
        query = """
            SELECT * FROM quanxian 
            WHERE id = :quanxian_id AND is_deleted = 'N'
        """
        
        result = db.execute(text(query), {"quanxian_id": quanxian_id}).fetchone()
        if not result:
            return None
        
        return QuanxianResponse(
            id=result.id,
            quanxian_ming=result.quanxian_ming,
            quanxian_bianma=result.quanxian_bianma,
            miaoshu=result.miaoshu,
            ziyuan_leixing=result.ziyuan_leixing,
            ziyuan_lujing=result.ziyuan_lujing,
            zhuangtai=result.zhuangtai,
            created_at=result.created_at,
            updated_at=result.updated_at,
            created_by=result.created_by,
            updated_by=result.updated_by
        )

    @staticmethod
    async def get_quanxian_by_bianma(db: Session, quanxian_bianma: str) -> Optional[dict]:
        """根据编码获取权限"""
        query = """
            SELECT * FROM quanxian 
            WHERE quanxian_bianma = :quanxian_bianma AND is_deleted = 'N'
        """
        result = db.execute(text(query), {"quanxian_bianma": quanxian_bianma}).fetchone()
        return result

    @staticmethod
    async def create_quanxian(
        db: Session,
        quanxian_data: QuanxianCreate,
        created_by: str
    ) -> QuanxianResponse:
        """创建权限"""
        quanxian_id = str(uuid.uuid4())
        now = datetime.now()
        
        query = """
            INSERT INTO quanxian (
                id, quanxian_ming, quanxian_bianma, miaoshu, ziyuan_leixing, 
                ziyuan_lujing, zhuangtai, created_by, created_at, updated_at, is_deleted
            ) VALUES (
                :id, :quanxian_ming, :quanxian_bianma, :miaoshu, :ziyuan_leixing,
                :ziyuan_lujing, :zhuangtai, :created_by, :created_at, :updated_at, 'N'
            )
        """
        
        db.execute(text(query), {
            "id": quanxian_id,
            "quanxian_ming": quanxian_data.quanxian_ming,
            "quanxian_bianma": quanxian_data.quanxian_bianma,
            "miaoshu": quanxian_data.miaoshu,
            "ziyuan_leixing": quanxian_data.ziyuan_leixing,
            "ziyuan_lujing": quanxian_data.ziyuan_lujing,
            "zhuangtai": quanxian_data.zhuangtai,
            "created_by": created_by,
            "created_at": now,
            "updated_at": now
        })
        
        db.commit()
        
        # 返回创建的权限
        return await QuanxianService.get_quanxian_by_id(db, quanxian_id)

    @staticmethod
    async def update_quanxian(
        db: Session,
        quanxian_id: str,
        quanxian_data: QuanxianUpdate,
        updated_by: str
    ) -> QuanxianResponse:
        """更新权限"""
        update_fields = []
        params = {"quanxian_id": quanxian_id, "updated_by": updated_by, "updated_at": datetime.now()}
        
        if quanxian_data.quanxian_ming is not None:
            update_fields.append("quanxian_ming = :quanxian_ming")
            params["quanxian_ming"] = quanxian_data.quanxian_ming
        
        if quanxian_data.quanxian_bianma is not None:
            update_fields.append("quanxian_bianma = :quanxian_bianma")
            params["quanxian_bianma"] = quanxian_data.quanxian_bianma
        
        if quanxian_data.miaoshu is not None:
            update_fields.append("miaoshu = :miaoshu")
            params["miaoshu"] = quanxian_data.miaoshu
        
        if quanxian_data.ziyuan_leixing is not None:
            update_fields.append("ziyuan_leixing = :ziyuan_leixing")
            params["ziyuan_leixing"] = quanxian_data.ziyuan_leixing
        
        if quanxian_data.ziyuan_lujing is not None:
            update_fields.append("ziyuan_lujing = :ziyuan_lujing")
            params["ziyuan_lujing"] = quanxian_data.ziyuan_lujing
        
        if quanxian_data.zhuangtai is not None:
            update_fields.append("zhuangtai = :zhuangtai")
            params["zhuangtai"] = quanxian_data.zhuangtai
        
        if update_fields:
            update_fields.append("updated_by = :updated_by")
            update_fields.append("updated_at = :updated_at")
            
            query = f"""
                UPDATE quanxian 
                SET {', '.join(update_fields)}
                WHERE id = :quanxian_id AND is_deleted = 'N'
            """
            
            db.execute(text(query), params)
            db.commit()
        
        return await QuanxianService.get_quanxian_by_id(db, quanxian_id)

    @staticmethod
    async def delete_quanxian(db: Session, quanxian_id: str) -> None:
        """删除权限（软删除）"""
        query = """
            UPDATE quanxian 
            SET is_deleted = 'Y', updated_at = :updated_at
            WHERE id = :quanxian_id AND is_deleted = 'N'
        """
        
        db.execute(text(query), {
            "quanxian_id": quanxian_id,
            "updated_at": datetime.now()
        })
        db.commit()

    @staticmethod
    async def get_quanxian_role_count(db: Session, quanxian_id: str) -> int:
        """获取权限关联的角色数量"""
        query = """
            SELECT COUNT(*) 
            FROM jiaose_quanxian jq
            JOIN jiaose j ON jq.jiaose_id = j.id
            WHERE jq.quanxian_id = :quanxian_id 
            AND jq.is_deleted = 'N' 
            AND j.is_deleted = 'N'
        """
        
        result = db.execute(text(query), {"quanxian_id": quanxian_id}).scalar()
        return result or 0

    @staticmethod
    async def get_quanxian_by_resource_type(
        db: Session,
        ziyuan_leixing: str,
        zhuangtai: Optional[str] = "active"
    ) -> List[QuanxianResponse]:
        """按资源类型获取权限列表"""
        conditions = ["ziyuan_leixing = :ziyuan_leixing", "is_deleted = 'N'"]
        params = {"ziyuan_leixing": ziyuan_leixing}
        
        if zhuangtai:
            conditions.append("zhuangtai = :zhuangtai")
            params["zhuangtai"] = zhuangtai
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT * FROM quanxian
            WHERE {where_clause}
            ORDER BY quanxian_bianma
        """
        
        result = db.execute(text(query), params).fetchall()
        
        return [
            QuanxianResponse(
                id=row.id,
                quanxian_ming=row.quanxian_ming,
                quanxian_bianma=row.quanxian_bianma,
                miaoshu=row.miaoshu,
                ziyuan_leixing=row.ziyuan_leixing,
                ziyuan_lujing=row.ziyuan_lujing,
                zhuangtai=row.zhuangtai,
                created_at=row.created_at,
                updated_at=row.updated_at,
                created_by=row.created_by,
                updated_by=row.updated_by
            )
            for row in result
        ]

    @staticmethod
    async def get_quanxian_statistics(db: Session) -> QuanxianStatistics:
        """获取权限统计信息"""
        query = """
            SELECT 
                COUNT(*) as total_permissions,
                COUNT(*) FILTER (WHERE ziyuan_leixing = 'menu') as menu_permissions,
                COUNT(*) FILTER (WHERE ziyuan_leixing = 'button') as button_permissions,
                COUNT(*) FILTER (WHERE ziyuan_leixing = 'api') as api_permissions,
                COUNT(*) FILTER (WHERE zhuangtai = 'active') as active_permissions,
                COUNT(*) FILTER (WHERE zhuangtai = 'inactive') as inactive_permissions,
                COUNT(DISTINCT jq.quanxian_id) as permissions_with_roles
            FROM quanxian q
            LEFT JOIN jiaose_quanxian jq ON q.id = jq.quanxian_id AND jq.is_deleted = 'N'
            WHERE q.is_deleted = 'N'
        """
        
        result = db.execute(text(query)).fetchone()
        
        return QuanxianStatistics(
            total_permissions=result.total_permissions or 0,
            menu_permissions=result.menu_permissions or 0,
            button_permissions=result.button_permissions or 0,
            api_permissions=result.api_permissions or 0,
            active_permissions=result.active_permissions or 0,
            inactive_permissions=result.inactive_permissions or 0,
            permissions_with_roles=result.permissions_with_roles or 0
        )
