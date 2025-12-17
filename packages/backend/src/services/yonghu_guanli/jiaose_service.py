"""
角色管理业务逻辑服务
"""
import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from models.yonghu_guanli.jiaose import Jiaose
from models.yonghu_guanli.quanxian import Quanxian
from models.yonghu_guanli.jiaose_quanxian import JiaoseQuanxian
from models.yonghu_guanli.yonghu_jiaose import YonghuJiaose
from schemas.yonghu_guanli.jiaose_schemas import (
    JiaoseCreate,
    JiaoseUpdate,
    JiaoseResponse,
    JiaoseListResponse,
    JiaoseListItem,
    JiaoseStatistics
)


class JiaoseService:
    """角色管理服务类"""

    @staticmethod
    async def get_jiaose_list(
        db: Session,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        zhuangtai: Optional[str] = None
    ) -> JiaoseListResponse:
        """获取角色列表"""
        
        # 构建查询条件
        conditions = ["j.is_deleted = 'N'"]
        params = {}
        
        if search:
            conditions.append("(j.jiaose_ming ILIKE :search OR j.jiaose_bianma ILIKE :search)")
            params["search"] = f"%{search}%"
        
        if zhuangtai:
            conditions.append("j.zhuangtai = :zhuangtai")
            params["zhuangtai"] = zhuangtai
        
        where_clause = " AND ".join(conditions)
        
        # 查询总数
        count_query = f"""
            SELECT COUNT(DISTINCT j.id)
            FROM jiaose j
            WHERE {where_clause}
        """
        total = db.execute(text(count_query), params).scalar()
        
        # 查询数据
        offset = (page - 1) * size
        data_query = f"""
            SELECT 
                j.id,
                j.jiaose_ming,
                j.jiaose_bianma,
                j.miaoshu,
                j.zhuangtai,
                j.created_at,
                j.updated_at,
                COALESCE(perm_count.cnt, 0) as permission_count,
                COALESCE(user_count.cnt, 0) as user_count
            FROM jiaose j
            LEFT JOIN (
                SELECT jq.jiaose_id, COUNT(*) as cnt
                FROM jiaose_quanxian jq
                WHERE jq.is_deleted = 'N'
                GROUP BY jq.jiaose_id
            ) perm_count ON j.id = perm_count.jiaose_id
            LEFT JOIN (
                SELECT yj.jiaose_id, COUNT(*) as cnt
                FROM yonghu_jiaose yj
                WHERE yj.is_deleted = 'N'
                GROUP BY yj.jiaose_id
            ) user_count ON j.id = user_count.jiaose_id
            WHERE {where_clause}
            ORDER BY j.created_at DESC
            LIMIT :size OFFSET :offset
        """
        params.update({"size": size, "offset": offset})
        
        result = db.execute(text(data_query), params).fetchall()
        
        items = []
        for row in result:
            items.append(JiaoseListItem(
                id=row.id,
                jiaose_ming=row.jiaose_ming,
                jiaose_bianma=row.jiaose_bianma,
                miaoshu=row.miaoshu,
                zhuangtai=row.zhuangtai,
                created_at=row.created_at,
                updated_at=row.updated_at,
                permission_count=row.permission_count,
                user_count=row.user_count
            ))
        
        pages = (total + size - 1) // size
        
        return JiaoseListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )

    @staticmethod
    async def get_jiaose_by_id(db: Session, jiaose_id: str) -> Optional[JiaoseResponse]:
        """根据ID获取角色详情"""
        query = """
            SELECT j.*, 
                   array_agg(DISTINCT q.id) FILTER (WHERE q.id IS NOT NULL) as permission_ids,
                   array_agg(DISTINCT y.id) FILTER (WHERE y.id IS NOT NULL) as user_ids
            FROM jiaose j
            LEFT JOIN jiaose_quanxian jq ON j.id = jq.jiaose_id AND jq.is_deleted = 'N'
            LEFT JOIN quanxian q ON jq.quanxian_id = q.id AND q.is_deleted = 'N'
            LEFT JOIN yonghu_jiaose yj ON j.id = yj.jiaose_id AND yj.is_deleted = 'N'
            LEFT JOIN yonghu y ON yj.yonghu_id = y.id AND y.is_deleted = 'N'
            WHERE j.id = :jiaose_id AND j.is_deleted = 'N'
            GROUP BY j.id
        """
        
        result = db.execute(text(query), {"jiaose_id": jiaose_id}).fetchone()
        if not result:
            return None
        
        # 获取权限详情
        permissions = []
        if result.permission_ids and result.permission_ids[0]:
            perm_query = """
                SELECT id, quanxian_ming, quanxian_bianma, ziyuan_leixing, zhuangtai
                FROM quanxian
                WHERE id = ANY(:permission_ids) AND is_deleted = 'N'
            """
            perm_result = db.execute(text(perm_query), {"permission_ids": result.permission_ids}).fetchall()
            permissions = [
                {
                    "id": row.id,
                    "quanxian_ming": row.quanxian_ming,
                    "quanxian_bianma": row.quanxian_bianma,
                    "ziyuan_leixing": row.ziyuan_leixing,
                    "zhuangtai": row.zhuangtai
                }
                for row in perm_result
            ]
        
        # 获取用户详情
        users = []
        if result.user_ids and result.user_ids[0]:
            user_query = """
                SELECT id, yonghu_ming, xingming, zhuangtai
                FROM yonghu
                WHERE id = ANY(:user_ids) AND is_deleted = 'N'
            """
            user_result = db.execute(text(user_query), {"user_ids": result.user_ids}).fetchall()
            users = [
                {
                    "id": row.id,
                    "yonghu_ming": row.yonghu_ming,
                    "xing_ming": row.xingming,
                    "zhuangtai": row.zhuangtai
                }
                for row in user_result
            ]
        
        return JiaoseResponse(
            id=result.id,
            jiaose_ming=result.jiaose_ming,
            jiaose_bianma=result.jiaose_bianma,
            miaoshu=result.miaoshu,
            zhuangtai=result.zhuangtai,
            created_at=result.created_at,
            updated_at=result.updated_at,
            created_by=result.created_by,
            updated_by=result.updated_by,
            permissions=permissions,
            users=users
        )

    @staticmethod
    async def get_jiaose_by_bianma(db: Session, jiaose_bianma: str) -> Optional[dict]:
        """根据编码获取角色"""
        query = """
            SELECT * FROM jiaose 
            WHERE jiaose_bianma = :jiaose_bianma AND is_deleted = 'N'
        """
        result = db.execute(text(query), {"jiaose_bianma": jiaose_bianma}).fetchone()
        return result

    @staticmethod
    async def create_jiaose(
        db: Session,
        jiaose_data: JiaoseCreate,
        created_by: str
    ) -> JiaoseResponse:
        """创建角色"""
        jiaose_id = str(uuid.uuid4())
        now = datetime.now()
        
        query = """
            INSERT INTO jiaose (
                id, jiaose_ming, jiaose_bianma, miaoshu, zhuangtai,
                created_by, created_at, updated_at, is_deleted
            ) VALUES (
                :id, :jiaose_ming, :jiaose_bianma, :miaoshu, :zhuangtai,
                :created_by, :created_at, :updated_at, 'N'
            )
        """
        
        db.execute(text(query), {
            "id": jiaose_id,
            "jiaose_ming": jiaose_data.jiaose_ming,
            "jiaose_bianma": jiaose_data.jiaose_bianma,
            "miaoshu": jiaose_data.miaoshu,
            "zhuangtai": jiaose_data.zhuangtai,
            "created_by": created_by,
            "created_at": now,
            "updated_at": now
        })
        
        db.commit()
        
        # 返回创建的角色
        return await JiaoseService.get_jiaose_by_id(db, jiaose_id)

    @staticmethod
    async def update_jiaose(
        db: Session,
        jiaose_id: str,
        jiaose_data: JiaoseUpdate,
        updated_by: str
    ) -> JiaoseResponse:
        """更新角色"""
        update_fields = []
        params = {"jiaose_id": jiaose_id, "updated_by": updated_by, "updated_at": datetime.now()}
        
        if jiaose_data.jiaose_ming is not None:
            update_fields.append("jiaose_ming = :jiaose_ming")
            params["jiaose_ming"] = jiaose_data.jiaose_ming
        
        if jiaose_data.jiaose_bianma is not None:
            update_fields.append("jiaose_bianma = :jiaose_bianma")
            params["jiaose_bianma"] = jiaose_data.jiaose_bianma
        
        if jiaose_data.miaoshu is not None:
            update_fields.append("miaoshu = :miaoshu")
            params["miaoshu"] = jiaose_data.miaoshu
        
        if jiaose_data.zhuangtai is not None:
            update_fields.append("zhuangtai = :zhuangtai")
            params["zhuangtai"] = jiaose_data.zhuangtai
        
        if update_fields:
            update_fields.append("updated_by = :updated_by")
            update_fields.append("updated_at = :updated_at")
            
            query = f"""
                UPDATE jiaose 
                SET {', '.join(update_fields)}
                WHERE id = :jiaose_id AND is_deleted = 'N'
            """
            
            db.execute(text(query), params)
            db.commit()
        
        return await JiaoseService.get_jiaose_by_id(db, jiaose_id)

    @staticmethod
    async def delete_jiaose(db: Session, jiaose_id: str) -> None:
        """删除角色（软删除）"""
        query = """
            UPDATE jiaose
            SET is_deleted = 'Y', updated_at = :updated_at
            WHERE id = :jiaose_id AND is_deleted = 'N'
        """

        db.execute(text(query), {
            "jiaose_id": jiaose_id,
            "updated_at": datetime.now()
        })
        db.commit()

    @staticmethod
    async def get_jiaose_user_count(db: Session, jiaose_id: str) -> int:
        """获取角色关联的用户数量"""
        query = """
            SELECT COUNT(*)
            FROM yonghu_jiaose yj
            JOIN yonghu y ON yj.yonghu_id = y.id
            WHERE yj.jiaose_id = :jiaose_id
            AND yj.is_deleted = 'N'
            AND y.is_deleted = 'N'
        """

        result = db.execute(text(query), {"jiaose_id": jiaose_id}).scalar()
        return result or 0

    @staticmethod
    async def update_jiaose_status(
        db: Session,
        jiaose_id: str,
        zhuangtai: str,
        reason: Optional[str],
        updated_by: str
    ) -> JiaoseResponse:
        """更新角色状态"""
        query = """
            UPDATE jiaose
            SET zhuangtai = :zhuangtai, updated_by = :updated_by, updated_at = :updated_at
            WHERE id = :jiaose_id AND is_deleted = 'N'
        """

        db.execute(text(query), {
            "jiaose_id": jiaose_id,
            "zhuangtai": zhuangtai,
            "updated_by": updated_by,
            "updated_at": datetime.now()
        })

        db.commit()
        return await JiaoseService.get_jiaose_by_id(db, jiaose_id)

    @staticmethod
    async def get_jiaose_permissions(db: Session, jiaose_id: str) -> List[dict]:
        """获取角色的所有权限"""
        query = """
            SELECT q.id, q.quanxian_ming, q.quanxian_bianma, q.ziyuan_leixing, q.zhuangtai
            FROM quanxian q
            JOIN jiaose_quanxian jq ON q.id = jq.quanxian_id
            WHERE jq.jiaose_id = :jiaose_id
            AND jq.is_deleted = 'N'
            AND q.is_deleted = 'N'
            ORDER BY q.quanxian_bianma
        """

        result = db.execute(text(query), {"jiaose_id": jiaose_id}).fetchall()
        return [
            {
                "id": row.id,
                "quanxian_ming": row.quanxian_ming,
                "quanxian_bianma": row.quanxian_bianma,
                "ziyuan_leixing": row.ziyuan_leixing,
                "zhuangtai": row.zhuangtai
            }
            for row in result
        ]

    @staticmethod
    async def update_jiaose_permissions(
        db: Session,
        jiaose_id: str,
        permission_ids: List[str],
        updated_by: str
    ) -> None:
        """更新角色权限（批量分配/移除权限）"""
        # 删除现有权限关联
        delete_query = """
            UPDATE jiaose_quanxian
            SET is_deleted = 'Y', updated_at = :updated_at
            WHERE jiaose_id = :jiaose_id AND is_deleted = 'N'
        """

        db.execute(text(delete_query), {
            "jiaose_id": jiaose_id,
            "updated_at": datetime.now()
        })

        # 添加新的权限关联
        if permission_ids:
            insert_query = """
                INSERT INTO jiaose_quanxian (
                    id, jiaose_id, quanxian_id, created_by, created_at, updated_at, is_deleted
                ) VALUES (
                    :id, :jiaose_id, :quanxian_id, :created_by, :created_at, :updated_at, 'N'
                )
            """

            now = datetime.now()
            for permission_id in permission_ids:
                db.execute(text(insert_query), {
                    "id": str(uuid.uuid4()),
                    "jiaose_id": jiaose_id,
                    "quanxian_id": permission_id,
                    "created_by": updated_by,
                    "created_at": now,
                    "updated_at": now
                })

        db.commit()
