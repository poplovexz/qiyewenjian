"""
支付回调日志服务类
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, Dict, Any
from datetime import datetime
import json

from models.zhifu_guanli.zhifu_huidiao_rizhi import ZhifuHuidiaoRizhi
from schemas.zhifu_guanli.zhifu_huidiao_schemas import (
    ZhifuHuidiaoRizhiResponse,
    ZhifuHuidiaoRizhiListResponse
)

class ZhifuHuidiaoService:
    """支付回调日志服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_log(
        self,
        huidiao_leixing: str,
        zhifu_pingtai: str,
        qingqiu_url: str,
        qingqiu_fangfa: str,
        qingqiu_tou: Dict[str, Any],
        qingqiu_shuju: Dict[str, Any],
        qianming: Optional[str] = None,
        zhifu_peizhi_id: Optional[str] = None
    ) -> ZhifuHuidiaoRizhi:
        """
        创建回调日志
        
        Args:
            huidiao_leixing: 回调类型（zhifu/tuikuan）
            zhifu_pingtai: 支付平台（weixin/zhifubao）
            qingqiu_url: 请求URL
            qingqiu_fangfa: 请求方法
            qingqiu_tou: 请求头字典
            qingqiu_shuju: 请求数据字典
            qianming: 签名
            zhifu_peizhi_id: 支付配置ID
        
        Returns:
            创建的回调日志对象
        """
        log = ZhifuHuidiaoRizhi(
            zhifu_peizhi_id=zhifu_peizhi_id,
            huidiao_leixing=huidiao_leixing,
            zhifu_pingtai=zhifu_pingtai,
            qingqiu_url=qingqiu_url,
            qingqiu_fangfa=qingqiu_fangfa,
            qingqiu_tou=json.dumps(qingqiu_tou, ensure_ascii=False),
            qingqiu_shuju=json.dumps(qingqiu_shuju, ensure_ascii=False),
            qianming=qianming,
            qianming_yanzheng='weiyanzhen',
            chuli_zhuangtai='chuli_zhong',
            jieshou_shijian=datetime.now()
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
    def update_log_verification(
        self,
        log_id: str,
        qianming_yanzheng: str,
        cuowu_xinxi: Optional[str] = None
    ) -> ZhifuHuidiaoRizhi:
        """
        更新签名验证结果
        
        Args:
            log_id: 日志ID
            qianming_yanzheng: 签名验证结果（chenggong/shibai）
            cuowu_xinxi: 错误信息
        
        Returns:
            更新后的日志对象
        """
        log = self.db.query(ZhifuHuidiaoRizhi).filter(
            ZhifuHuidiaoRizhi.id == log_id
        ).first()
        
        if not log:
            raise ValueError(f"回调日志不存在: {log_id}")
        
        log.qianming_yanzheng = qianming_yanzheng
        if cuowu_xinxi:
            log.cuowu_xinxi = cuowu_xinxi
        
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
    def update_log_result(
        self,
        log_id: str,
        chuli_zhuangtai: str,
        chuli_jieguo: Optional[str] = None,
        cuowu_xinxi: Optional[str] = None
    ) -> ZhifuHuidiaoRizhi:
        """
        更新处理结果
        
        Args:
            log_id: 日志ID
            chuli_zhuangtai: 处理状态（chenggong/shibai）
            chuli_jieguo: 处理结果
            cuowu_xinxi: 错误信息
        
        Returns:
            更新后的日志对象
        """
        log = self.db.query(ZhifuHuidiaoRizhi).filter(
            ZhifuHuidiaoRizhi.id == log_id
        ).first()
        
        if not log:
            raise ValueError(f"回调日志不存在: {log_id}")
        
        log.chuli_zhuangtai = chuli_zhuangtai
        log.chuli_shijian = datetime.now()
        
        if chuli_jieguo:
            log.chuli_jieguo = chuli_jieguo
        if cuowu_xinxi:
            log.cuowu_xinxi = cuowu_xinxi
        
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
    def get_logs(
        self,
        page: int = 1,
        page_size: int = 20,
        huidiao_leixing: Optional[str] = None,
        zhifu_pingtai: Optional[str] = None,
        qianming_yanzheng: Optional[str] = None,
        chuli_zhuangtai: Optional[str] = None
    ) -> ZhifuHuidiaoRizhiListResponse:
        """
        获取回调日志列表
        
        Args:
            page: 页码
            page_size: 每页数量
            huidiao_leixing: 回调类型筛选
            zhifu_pingtai: 支付平台筛选
            qianming_yanzheng: 签名验证筛选
            chuli_zhuangtai: 处理状态筛选
        
        Returns:
            回调日志列表响应
        """
        query = self.db.query(ZhifuHuidiaoRizhi)
        
        # 筛选条件
        if huidiao_leixing:
            query = query.filter(ZhifuHuidiaoRizhi.huidiao_leixing == huidiao_leixing)
        if zhifu_pingtai:
            query = query.filter(ZhifuHuidiaoRizhi.zhifu_pingtai == zhifu_pingtai)
        if qianming_yanzheng:
            query = query.filter(ZhifuHuidiaoRizhi.qianming_yanzheng == qianming_yanzheng)
        if chuli_zhuangtai:
            query = query.filter(ZhifuHuidiaoRizhi.chuli_zhuangtai == chuli_zhuangtai)
        
        # 总数
        total = query.count()
        
        # 分页
        logs = query.order_by(desc(ZhifuHuidiaoRizhi.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return ZhifuHuidiaoRizhiListResponse(
            total=total,
            items=[ZhifuHuidiaoRizhiResponse.from_orm(log) for log in logs],
            page=page,
            page_size=page_size
        )
    
    def get_log_by_id(self, log_id: str) -> Optional[ZhifuHuidiaoRizhi]:
        """
        根据ID获取回调日志
        
        Args:
            log_id: 日志ID
        
        Returns:
            回调日志对象或None
        """
        return self.db.query(ZhifuHuidiaoRizhi).filter(
            ZhifuHuidiaoRizhi.id == log_id
        ).first()
