"""
线索管理 API 端点
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.permissions import require_permission, has_permission
from core.security.jwt_handler import get_current_user
from models.yonghu_guanli import Yonghu
from services.xiansuo_guanli import XiansuoService
from schemas.xiansuo_guanli import (
    XiansuoCreate,
    XiansuoUpdate,
    XiansuoResponse,
    XiansuoListResponse,
    XiansuoDetailResponse,
    XiansuoStatusUpdate,
    XiansuoAssignUpdate,
    XiansuoStatistics
)

router = APIRouter()


@router.post("/", response_model=XiansuoResponse, summary="创建线索")
async def create_xiansuo(
    xiansuo_data: XiansuoCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:create"))
):
    """
    创建新线索
    
    - **gongsi_mingcheng**: 公司名称（必填）
    - **lianxi_ren**: 联系人（必填）
    - **lianxi_dianhua**: 联系电话
    - **laiyuan_id**: 线索来源ID（必填）
    - **zhiliang_pinggu**: 质量评估（high/medium/low）
    """
    service = XiansuoService(db)
    return service.create_xiansuo(xiansuo_data, current_user.id)


@router.get("/", response_model=XiansuoListResponse, summary="获取线索列表")
async def get_xiansuo_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（编码、公司名称、联系人等）"),
    xiansuo_zhuangtai: Optional[str] = Query(None, description="线索状态筛选"),
    laiyuan_id: Optional[str] = Query(None, description="来源ID筛选"),
    fenpei_ren_id: Optional[str] = Query(None, description="分配人ID筛选"),
    zhiliang_pinggu: Optional[str] = Query(None, description="质量评估筛选"),
    hangye_leixing: Optional[str] = Query(None, description="行业类型筛选"),
    start_date: Optional[datetime] = Query(None, description="开始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:read"))
):
    """
    获取线索列表

    支持分页、搜索和多维度筛选
    数据隔离：普通用户只能查看自己创建的线索，有read_all权限的用户可以查看所有线索
    """
    service = XiansuoService(db)

    # 检查是否有全局查看权限
    has_read_all = has_permission(db, current_user, "xiansuo:read_all")

    return service.get_xiansuo_list(
        page=page,
        size=size,
        search=search,
        xiansuo_zhuangtai=xiansuo_zhuangtai,
        laiyuan_id=laiyuan_id,
        fenpei_ren_id=fenpei_ren_id,
        zhiliang_pinggu=zhiliang_pinggu,
        hangye_leixing=hangye_leixing,
        start_date=start_date,
        end_date=end_date,
        current_user_id=current_user.id,
        has_read_all_permission=has_read_all
    )


@router.get("/statistics", response_model=XiansuoStatistics, summary="获取线索统计数据")
async def get_xiansuo_statistics(
    start_date: Optional[datetime] = Query(None, description="开始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    fenpei_ren_id: Optional[str] = Query(None, description="分配人ID筛选"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:read"))
):
    """
    获取线索统计数据
    
    包括各状态线索数量、转化率、平均转化周期等
    """
    service = XiansuoService(db)
    return service.get_xiansuo_statistics(
        start_date=start_date,
        end_date=end_date,
        fenpei_ren_id=fenpei_ren_id
    )


@router.get("/{xiansuo_id}", response_model=XiansuoDetailResponse, summary="获取线索详情")
async def get_xiansuo_detail(
    xiansuo_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:read"))
):
    """根据ID获取线索详情（包含关联数据）"""
    service = XiansuoService(db)
    xiansuo = service.get_xiansuo_detail(xiansuo_id)
    
    if not xiansuo:
        raise HTTPException(status_code=404, detail="线索不存在")
    
    return xiansuo


@router.put("/{xiansuo_id}", response_model=XiansuoResponse, summary="更新线索")
async def update_xiansuo(
    xiansuo_id: str,
    xiansuo_data: XiansuoUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:update"))
):
    """
    更新线索信息

    - 支持部分字段更新
    - 更新来源时会验证来源是否存在
    - 数据隔离：普通用户只能更新自己创建的线索，有update_all权限的用户可以更新所有线索
    """
    service = XiansuoService(db)

    # 检查是否有全局更新权限
    has_update_all = has_permission(db, current_user, "xiansuo:update_all")

    return service.update_xiansuo(xiansuo_id, xiansuo_data, current_user.id, has_update_all)


@router.patch("/{xiansuo_id}/status", response_model=XiansuoResponse, summary="更新线索状态")
async def update_xiansuo_status(
    xiansuo_id: str,
    status_data: XiansuoStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:update"))
):
    """
    更新线索状态
    
    - 状态变为成交时会自动设置转化信息
    - 会更新来源的转化统计数据
    """
    service = XiansuoService(db)
    return service.update_xiansuo_status(xiansuo_id, status_data, current_user.id)


@router.patch("/{xiansuo_id}/assign", response_model=XiansuoResponse, summary="分配线索")
async def assign_xiansuo(
    xiansuo_id: str,
    assign_data: XiansuoAssignUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:update"))
):
    """
    分配线索给销售人员
    
    - 会验证分配人是否存在
    - 新线索分配后自动变为跟进中状态
    """
    service = XiansuoService(db)
    return service.assign_xiansuo(xiansuo_id, assign_data, current_user.id)


@router.delete("/{xiansuo_id}", summary="删除线索")
async def delete_xiansuo(
    xiansuo_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:delete"))
):
    """
    删除线索（软删除）

    - 会同步更新来源的线索统计数据
    - 数据隔离：普通用户只能删除自己创建的线索，有delete_all权限的用户可以删除所有线索
    """
    service = XiansuoService(db)

    # 检查是否有全局删除权限
    has_delete_all = has_permission(db, current_user, "xiansuo:delete_all")

    success = service.delete_xiansuo(xiansuo_id, current_user.id, has_delete_all)

    if success:
        return {"message": "线索删除成功"}
    else:
        raise HTTPException(status_code=500, detail="删除失败")


@router.get("/{xiansuo_id}/contract-status", summary="获取线索的合同状态")
async def get_xiansuo_contract_status(
    xiansuo_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    获取线索的合同状态和审核信息

    返回:
    - contract_status: 合同状态 (null/pending/active/signed等)
    - contract_id: 合同ID
    - audit_status: 审核状态 (null/pending/approved/rejected)
    - audit_workflow_id: 审核流程ID
    - audit_details: 审核详情（包括审核步骤、审核人等）
    """
    from models.xiansuo_guanli.xiansuo_baojia import XiansuoBaojia
    from models.hetong_guanli.hetong import Hetong
    from models.shenhe_guanli.shenhe_liucheng import ShenheLiucheng
    from models.shenhe_guanli.shenhe_jilu import ShenheJilu
    from models.yonghu_guanli.yonghu import Yonghu as YonghuModel

    # 1. 查询已确认的报价
    baojia = db.query(XiansuoBaojia).filter(
        XiansuoBaojia.xiansuo_id == xiansuo_id,
        XiansuoBaojia.baojia_zhuangtai == 'accepted',
        XiansuoBaojia.is_deleted == 'N'
    ).order_by(XiansuoBaojia.created_at.desc()).first()

    if not baojia:
        return {
            "contract_status": None,
            "contract_id": None,
            "audit_status": None,
            "audit_workflow_id": None,
            "audit_details": None
        }

    # 2. 查询合同
    hetong = db.query(Hetong).filter(
        Hetong.baojia_id == baojia.id,
        Hetong.is_deleted == 'N'
    ).order_by(Hetong.created_at.desc()).first()

    if not hetong:
        return {
            "contract_status": None,
            "contract_id": None,
            "audit_status": None,
            "audit_workflow_id": None,
            "audit_details": None
        }

    # 3. 查询审核流程
    workflow = db.query(ShenheLiucheng).filter(
        ShenheLiucheng.guanlian_id == hetong.id,
        ShenheLiucheng.shenhe_leixing == 'hetong_jine_xiuzheng',
        ShenheLiucheng.is_deleted == 'N'
    ).order_by(ShenheLiucheng.created_at.desc()).first()

    audit_details = None
    audit_status = None

    if workflow:
        # 映射审核状态
        status_map = {
            'daishehe': 'pending',
            'shenhezhong': 'pending',
            'yitongguo': 'approved',
            'tongguo': 'approved',
            'jujue': 'rejected',
            'yibohui': 'rejected',
            'chexiao': 'cancelled'
        }
        audit_status = status_map.get(workflow.shenhe_zhuangtai, 'pending')

        # 4. 查询审核记录
        records = db.query(ShenheJilu).filter(
            ShenheJilu.liucheng_id == workflow.id,
            ShenheJilu.is_deleted == 'N'
        ).order_by(ShenheJilu.buzhou_bianhao).all()

        # 构建审核详情
        steps = []
        for record in records:
            # 查询审核人信息
            auditor = db.query(YonghuModel).filter(
                YonghuModel.id == record.shenhe_ren_id
            ).first()

            step_status = 'pending'
            if record.jilu_zhuangtai == 'yichuli':
                if record.shenhe_jieguo == 'tongguo':
                    step_status = 'approved'
                elif record.shenhe_jieguo in ('jujue', 'bohui'):
                    step_status = 'rejected'

            steps.append({
                'step_number': record.buzhou_bianhao,
                'step_name': record.buzhou_mingcheng or f'审核步骤{record.buzhou_bianhao}',
                'auditor_name': auditor.xingming if auditor else '未知',
                'auditor_id': record.shenhe_ren_id,
                'status': step_status,
                'comment': record.shenhe_yijian,
                'audit_time': record.shenhe_shijian.isoformat() if record.shenhe_shijian else None
            })

        audit_details = {
            'workflow_id': workflow.id,
            'workflow_number': workflow.liucheng_bianhao,
            'current_step': workflow.dangqian_buzhou,
            'total_steps': workflow.zonggong_buzhou,
            'steps': steps,
            'created_at': workflow.created_at.isoformat() if workflow.created_at else None,
            'completed_at': workflow.wancheng_shijian.isoformat() if workflow.wancheng_shijian else None
        }

    return {
        "contract_status": hetong.hetong_zhuangtai,
        "contract_id": hetong.id,
        "audit_status": audit_status,
        "audit_workflow_id": workflow.id if workflow else None,
        "audit_details": audit_details
    }
