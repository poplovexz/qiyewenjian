"""
退款管理服务类
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException
import uuid
import logging

from models.zhifu_guanli.zhifu_tuikuan import ZhifuTuikuan
from models.zhifu_guanli.zhifu_dingdan import ZhifuDingdan
from schemas.zhifu_guanli.zhifu_tuikuan_schemas import (
    ZhifuTuikuanCreate,
    ZhifuTuikuanResponse,
    ZhifuTuikuanListResponse
)
from services.zhifu_guanli.zhifu_peizhi_service import ZhifuPeizhiService
from utils.payment.weixin_pay import WeixinPayUtil
from utils.payment.alipay import AlipayUtil, ALIPAY_SDK_AVAILABLE
from core.events import publish, EventNames

logger = logging.getLogger(__name__)

class ZhifuTuikuanService:
    """退款管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.peizhi_service = ZhifuPeizhiService(db)
    
    def create_refund(
        self,
        tuikuan_data: ZhifuTuikuanCreate,
        created_by: str
    ) -> ZhifuTuikuanResponse:
        """
        创建退款申请
        
        Args:
            tuikuan_data: 退款数据
            created_by: 创建人
        
        Returns:
            退款记录响应
        """
        # 查找支付订单
        dingdan = self.db.query(ZhifuDingdan).filter(
            ZhifuDingdan.id == tuikuan_data.zhifu_dingdan_id,
            ZhifuDingdan.is_deleted == "N"
        ).first()
        
        if not dingdan:
            raise HTTPException(status_code=404, detail="支付订单不存在")
        
        # 验证订单状态
        if dingdan.zhifu_zhuangtai != 'paid':
            raise HTTPException(status_code=400, detail="订单未支付，无法退款")
        
        # 验证退款金额
        if tuikuan_data.tuikuan_jine <= 0:
            raise HTTPException(status_code=400, detail="退款金额必须大于0")
        
        if tuikuan_data.tuikuan_jine > dingdan.shifu_jine:
            raise HTTPException(status_code=400, detail="退款金额不能大于实付金额")
        
        # 检查已退款金额
        yituikuan_jine = Decimal(dingdan.tuikuan_jine or 0)
        if yituikuan_jine + tuikuan_data.tuikuan_jine > dingdan.shifu_jine:
            raise HTTPException(
                status_code=400,
                detail=f"退款金额超出可退款额度，已退款：{yituikuan_jine}，可退款：{dingdan.shifu_jine - yituikuan_jine}"
            )
        
        # 生成退款单号
        tuikuan_danhao = self._generate_tuikuan_danhao()
        
        # 创建退款记录
        tuikuan = ZhifuTuikuan(
            zhifu_dingdan_id=tuikuan_data.zhifu_dingdan_id,
            zhifu_peizhi_id=dingdan.zhifu_peizhi_id,
            tuikuan_danhao=tuikuan_danhao,
            yuanshi_dingdan_hao=dingdan.dingdan_bianhao,
            yuanshi_jine=dingdan.shifu_jine,
            tuikuan_jine=tuikuan_data.tuikuan_jine,
            tuikuan_yuanyin=tuikuan_data.tuikuan_yuanyin,
            tuikuan_zhuangtai='chuli_zhong',
            tuikuan_pingtai=dingdan.zhifu_pingtai,
            shenqing_shijian=datetime.now(),
            created_by=created_by
        )
        
        self.db.add(tuikuan)
        self.db.flush()
        
        # 调用第三方退款接口
        try:
            if dingdan.zhifu_pingtai == 'weixin':
                result = self._process_weixin_refund(dingdan, tuikuan)
            elif dingdan.zhifu_pingtai == 'zhifubao':
                result = self._process_alipay_refund(dingdan, tuikuan)
            else:
                raise ValueError(f"不支持的支付平台: {dingdan.zhifu_pingtai}")
            
            if result.get('success'):
                # 退款申请成功
                tuikuan.disanfang_tuikuan_hao = result.get('refund_id')
                tuikuan.chuli_jieguo = result.get('message')
                
                # 更新订单退款信息
                dingdan.tuikuan_jine = Decimal(dingdan.tuikuan_jine or 0) + tuikuan_data.tuikuan_jine
                dingdan.tuikuan_cishu = str(int(dingdan.tuikuan_cishu or 0) + 1)
                
                # 如果全额退款，更新订单状态
                if dingdan.tuikuan_jine >= dingdan.shifu_jine:
                    dingdan.zhifu_zhuangtai = 'refunded'
                    tuikuan.tuikuan_zhuangtai = 'chenggong'
                    tuikuan.chenggong_shijian = datetime.now()
            else:
                # 退款申请失败
                tuikuan.tuikuan_zhuangtai = 'shibai'
                tuikuan.cuowu_xinxi = result.get('message')
                tuikuan.cuowu_daima = result.get('error_code')
                
        except Exception as e:
            logger.error(f"退款申请异常: {str(e)}")
            tuikuan.tuikuan_zhuangtai = 'shibai'
            tuikuan.cuowu_xinxi = str(e)
        
        self.db.commit()
        self.db.refresh(tuikuan)
        
        # 发布退款事件
        publish(EventNames.REFUND_CREATED, {
            "tuikuan_id": tuikuan.id,
            "dingdan_id": dingdan.id,
            "tuikuan_jine": float(tuikuan_data.tuikuan_jine),
            "zhuangtai": tuikuan.tuikuan_zhuangtai,
            "created_by": created_by
        })
        
        return ZhifuTuikuanResponse.from_orm(tuikuan)
    
    def _process_weixin_refund(
        self,
        dingdan: ZhifuDingdan,
        tuikuan: ZhifuTuikuan
    ) -> Dict[str, Any]:
        """处理微信退款"""
        # 获取支付配置
        peizhi = self.peizhi_service.get_detail(dingdan.zhifu_peizhi_id)
        
        # 初始化微信支付工具
        weixin_util = WeixinPayUtil({
            'weixin_appid': peizhi.weixin_appid,
            'weixin_shanghu_hao': peizhi.weixin_shanghu_hao,
            'weixin_shanghu_siyao': peizhi.weixin_shanghu_siyao,
            'weixin_zhengshu_xuliehao': peizhi.weixin_zhengshu_xuliehao,
            'weixin_api_v3_miyao': peizhi.weixin_api_v3_miyao,
            'tongzhi_url': peizhi.tongzhi_url
        })
        
        # 调用退款接口
        result = weixin_util.refund(
            out_trade_no=dingdan.dingdan_bianhao,
            out_refund_no=tuikuan.tuikuan_danhao,
            refund_amount=int(tuikuan.tuikuan_jine * 100),  # 转换为分
            total_amount=int(dingdan.shifu_jine * 100),
            reason=tuikuan.tuikuan_yuanyin
        )
        
        if result.get('success'):
            refund_data = result.get('data', {})
            return {
                'success': True,
                'refund_id': refund_data.get('refund_id'),
                'message': '退款申请成功'
            }
        else:
            return {
                'success': False,
                'error_code': result.get('error_code'),
                'message': result.get('message', '退款申请失败')
            }
    
    def _process_alipay_refund(
        self,
        dingdan: ZhifuDingdan,
        tuikuan: ZhifuTuikuan
    ) -> Dict[str, Any]:
        """处理支付宝退款"""
        if not ALIPAY_SDK_AVAILABLE:
            return {
                'success': False,
                'message': '支付宝SDK不可用'
            }
        
        # 获取支付配置
        peizhi = self.peizhi_service.get_detail(dingdan.zhifu_peizhi_id)
        
        # 初始化支付宝工具
        alipay_util = AlipayUtil(
            appid=peizhi.zhifubao_appid,
            app_private_key=peizhi.zhifubao_shanghu_siyao,
            alipay_public_key=peizhi.zhifubao_zhifubao_gongyao,
            notify_url=peizhi.tongzhi_url,
            debug=peizhi.huanjing == 'shachang'
        )
        
        # 调用退款接口
        result = alipay_util.refund(
            out_trade_no=dingdan.dingdan_bianhao,
            refund_amount=float(tuikuan.tuikuan_jine),
            refund_reason=tuikuan.tuikuan_yuanyin
        )
        
        if result.get('success'):
            return {
                'success': True,
                'refund_id': result.get('trade_no'),
                'message': '退款申请成功'
            }
        else:
            return {
                'success': False,
                'error_code': result.get('error_code'),
                'message': result.get('message', '退款申请失败')
            }
    
    def get_refund_list(
        self,
        page: int = 1,
        page_size: int = 20,
        tuikuan_zhuangtai: Optional[str] = None,
        tuikuan_pingtai: Optional[str] = None,
        search: Optional[str] = None
    ) -> ZhifuTuikuanListResponse:
        """
        获取退款列表
        
        Args:
            page: 页码
            page_size: 每页数量
            tuikuan_zhuangtai: 退款状态筛选
            tuikuan_pingtai: 退款平台筛选
            search: 搜索关键词
        
        Returns:
            退款列表响应
        """
        query = self.db.query(ZhifuTuikuan).filter(
            ZhifuTuikuan.is_deleted == "N"
        )
        
        # 筛选条件
        if tuikuan_zhuangtai:
            query = query.filter(ZhifuTuikuan.tuikuan_zhuangtai == tuikuan_zhuangtai)
        if tuikuan_pingtai:
            query = query.filter(ZhifuTuikuan.tuikuan_pingtai == tuikuan_pingtai)
        if search:
            query = query.filter(
                (ZhifuTuikuan.tuikuan_danhao.like(f"%{search}%")) |
                (ZhifuTuikuan.yuanshi_dingdan_hao.like(f"%{search}%"))
            )
        
        # 总数
        total = query.count()
        
        # 分页
        tuikuan_list = query.order_by(desc(ZhifuTuikuan.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return ZhifuTuikuanListResponse(
            total=total,
            items=[ZhifuTuikuanResponse.from_orm(t) for t in tuikuan_list],
            page=page,
            page_size=page_size
        )
    
    def get_refund_by_id(self, tuikuan_id: str) -> ZhifuTuikuanResponse:
        """
        根据ID获取退款详情
        
        Args:
            tuikuan_id: 退款ID
        
        Returns:
            退款记录响应
        """
        tuikuan = self.db.query(ZhifuTuikuan).filter(
            ZhifuTuikuan.id == tuikuan_id,
            ZhifuTuikuan.is_deleted == "N"
        ).first()
        
        if not tuikuan:
            raise HTTPException(status_code=404, detail="退款记录不存在")
        
        return ZhifuTuikuanResponse.from_orm(tuikuan)
    
    @staticmethod
    def _generate_tuikuan_danhao() -> str:
        """生成退款单号"""
        # 格式：TK + YYYYMMDD + 6位随机数
        today = datetime.now().strftime("%Y%m%d")
        random_suffix = str(uuid.uuid4().int)[:6]
        return f"TK{today}{random_suffix}"
