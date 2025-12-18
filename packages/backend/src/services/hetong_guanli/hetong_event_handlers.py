"""
合同管理事件处理器
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from core.database import get_db
from services.fuwu_guanli import FuwuGongdanService
from core.events import event_handler
import logging

logger = logging.getLogger(__name__)


@event_handler("hetong_signed")
async def handle_hetong_signed(payload: Dict[str, Any]):
    """
    处理合同签署事件，自动创建服务工单
    
    Args:
        payload: 事件载荷，包含：
            - hetong_id: 合同ID
            - signed_by: 签署人ID
            - signed_at: 签署时间
    """
    try:
        hetong_id = payload.get("hetong_id")
        signed_by = payload.get("signed_by", "system")
        
        if not hetong_id:
            logger.error("合同签署事件缺少必要参数：hetong_id")
            return
        
        # 获取数据库会话
        # PTC-W0063: 添加默认值防止 StopIteration
        db: Session = next(get_db(), None)
        if db is None:
            logger.error("无法获取数据库连接")
            return

        try:
            # 创建服务工单服务实例
            fuwu_gongdan_service = FuwuGongdanService(db)

            # 基于合同创建服务工单
            gongdan = fuwu_gongdan_service.create_gongdan_from_hetong(
                hetong_id=hetong_id,
                created_by=signed_by
            )
            
            logger.info(f"合同签署后自动创建服务工单成功", extra={
                "hetong_id": hetong_id,
                "gongdan_id": gongdan.id,
                "gongdan_bianhao": gongdan.gongdan_bianhao,
                "created_by": signed_by
            })
            
        except Exception as e:
            logger.error(f"基于合同创建服务工单失败", extra={
                "hetong_id": hetong_id,
                "error": str(e),
                "signed_by": signed_by
            })
            # 不抛出异常，避免影响合同签署流程
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"处理合同签署事件失败", extra={
            "payload": payload,
            "error": str(e)
        })


@event_handler("hetong_cancelled")
async def handle_hetong_cancelled(payload: Dict[str, Any]):
    """
    处理合同取消事件，取消相关的服务工单
    
    Args:
        payload: 事件载荷，包含：
            - hetong_id: 合同ID
            - cancelled_by: 取消人ID
            - cancel_reason: 取消原因
    """
    try:
        hetong_id = payload.get("hetong_id")
        cancelled_by = payload.get("cancelled_by", "system")
        cancel_reason = payload.get("cancel_reason", "合同已取消")
        
        if not hetong_id:
            logger.error("合同取消事件缺少必要参数：hetong_id")
            return
        
        # 获取数据库会话
        # PTC-W0063: 添加默认值防止 StopIteration
        db: Session = next(get_db(), None)
        if db is None:
            logger.error("无法获取数据库连接")
            return

        try:
            # 创建服务工单服务实例
            fuwu_gongdan_service = FuwuGongdanService(db)

            # 查找该合同相关的工单
            from models.fuwu_guanli import FuwuGongdan
            gongdan_list = db.query(FuwuGongdan).filter(
                FuwuGongdan.hetong_id == hetong_id,
                FuwuGongdan.is_deleted == "N",
                FuwuGongdan.gongdan_zhuangtai.notin_(["completed", "cancelled"])
            ).all()
            
            # 取消所有未完成的工单
            for gongdan in gongdan_list:
                fuwu_gongdan_service.cancel_gongdan(
                    gongdan_id=gongdan.id,
                    cancel_reason=f"关联合同已取消：{cancel_reason}",
                    cancelled_by=cancelled_by
                )
                
                logger.info(f"合同取消后自动取消服务工单", extra={
                    "hetong_id": hetong_id,
                    "gongdan_id": gongdan.id,
                    "gongdan_bianhao": gongdan.gongdan_bianhao,
                    "cancelled_by": cancelled_by
                })
            
        except Exception as e:
            logger.error(f"取消合同相关服务工单失败", extra={
                "hetong_id": hetong_id,
                "error": str(e),
                "cancelled_by": cancelled_by
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"处理合同取消事件失败", extra={
            "payload": payload,
            "error": str(e)
        })
