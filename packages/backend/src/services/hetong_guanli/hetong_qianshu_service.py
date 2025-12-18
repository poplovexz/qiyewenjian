"""
合同签署服务
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models.hetong_guanli import HetongQianshu, Hetong
from schemas.hetong_guanli import HetongQianshuCreate
from core.exceptions import BusinessException
import uuid


class HetongQianshuService:
    """合同签署服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_qianshu_lianjie(self, hetong_id: str, youxiao_tianshu: int = 7) -> Dict[str, Any]:
        """
        创建合同签署链接
        
        Args:
            hetong_id: 合同ID
            youxiao_tianshu: 有效天数，默认7天
            
        Returns:
            签署链接信息
        """
        # 检查合同是否存在
        hetong = self.db.query(Hetong).filter(
            and_(Hetong.id == hetong_id, Hetong.is_deleted == "N")
        ).first()
        
        if not hetong:
            raise BusinessException("合同不存在")
        
        # 检查合同状态是否允许签署
        if hetong.hetong_zhuangtai not in ["daizhifu", "daiqianshu"]:
            raise BusinessException("合同状态不允许签署")
        
        # 检查是否已有有效的签署链接
        existing_qianshu = self.db.query(HetongQianshu).filter(
            and_(
                HetongQianshu.hetong_id == hetong_id,
                HetongQianshu.qianshu_zhuangtai == "daiqianshu",
                HetongQianshu.youxiao_jieshu > datetime.utcnow(),
                HetongQianshu.is_deleted == "N"
            )
        ).first()
        
        if existing_qianshu:
            return {
                "qianshu_lianjie": existing_qianshu.qianshu_lianjie,
                "qianshu_token": existing_qianshu.qianshu_token,
                "youxiao_jieshu": existing_qianshu.youxiao_jieshu
            }
        
        # 生成签署令牌
        qianshu_token = str(uuid.uuid4()).replace('-', '')
        
        # 计算有效期
        youxiao_kaishi = datetime.utcnow()
        youxiao_jieshu = youxiao_kaishi + timedelta(days=youxiao_tianshu)
        
        # 生成签署链接
        qianshu_lianjie = f"/contract-sign/{qianshu_token}"
        
        # 创建签署记录
        qianshu_data = HetongQianshuCreate(
            hetong_id=hetong_id,
            qianshu_lianjie=qianshu_lianjie,
            qianshu_token=qianshu_token,
            youxiao_kaishi=youxiao_kaishi,
            youxiao_jieshu=youxiao_jieshu
        )
        
        qianshu = HetongQianshu(**qianshu_data.model_dump())
        self.db.add(qianshu)
        self.db.commit()
        self.db.refresh(qianshu)
        
        return {
            "qianshu_lianjie": qianshu_lianjie,
            "qianshu_token": qianshu_token,
            "youxiao_jieshu": youxiao_jieshu
        }

    def get_qianshu_by_token(self, qianshu_token: str) -> Optional[Dict[str, Any]]:
        """
        根据签署令牌获取签署信息
        
        Args:
            qianshu_token: 签署令牌
            
        Returns:
            签署信息
        """
        qianshu = self.db.query(HetongQianshu).filter(
            and_(
                HetongQianshu.qianshu_token == qianshu_token,
                HetongQianshu.is_deleted == "N"
            )
        ).first()
        
        if not qianshu:
            return None
        
        # 检查是否过期
        if qianshu.youxiao_jieshu < datetime.utcnow():
            # 更新状态为过期
            qianshu.qianshu_zhuangtai = "guoqi"
            self.db.commit()
            return None
        
        # 获取合同信息
        hetong = self.db.query(Hetong).filter(
            and_(Hetong.id == qianshu.hetong_id, Hetong.is_deleted == "N")
        ).first()
        
        if not hetong:
            return None
        
        return {
            "qianshu_id": qianshu.id,
            "hetong_id": qianshu.hetong_id,
            "hetong_bianhao": hetong.hetong_bianhao,
            "hetong_mingcheng": hetong.hetong_mingcheng,
            "hetong_neirong": hetong.hetong_neirong,
            "qianshu_zhuangtai": qianshu.qianshu_zhuangtai,
            "youxiao_jieshu": qianshu.youxiao_jieshu,
            "qianshu_ren_mingcheng": qianshu.qianshu_ren_mingcheng,
            "qianshu_shijian": qianshu.qianshu_shijian
        }

    def process_qianshu(self, qianshu_token: str, qianshu_data: Dict[str, Any]) -> bool:
        """
        处理合同签署
        
        Args:
            qianshu_token: 签署令牌
            qianshu_data: 签署数据
            
        Returns:
            是否成功
        """
        qianshu = self.db.query(HetongQianshu).filter(
            and_(
                HetongQianshu.qianshu_token == qianshu_token,
                HetongQianshu.qianshu_zhuangtai == "daiqianshu",
                HetongQianshu.is_deleted == "N"
            )
        ).first()
        
        if not qianshu:
            raise BusinessException("签署链接无效或已过期")
        
        # 检查是否过期
        if qianshu.youxiao_jieshu < datetime.utcnow():
            qianshu.qianshu_zhuangtai = "guoqi"
            self.db.commit()
            raise BusinessException("签署链接已过期")
        
        # 更新签署信息
        qianshu.qianshu_ren_mingcheng = qianshu_data.get("qianshu_ren_mingcheng")
        qianshu.qianshu_ren_dianhua = qianshu_data.get("qianshu_ren_dianhua")
        qianshu.qianshu_ren_youxiang = qianshu_data.get("qianshu_ren_youxiang")
        qianshu.qianshu_shijian = datetime.utcnow()
        qianshu.qianshu_ip = qianshu_data.get("qianshu_ip")
        qianshu.qianshu_shebei = qianshu_data.get("qianshu_shebei")
        qianshu.qianming_tupian = qianshu_data.get("qianming_tupian")
        qianshu.qianming_zuobiao = qianshu_data.get("qianming_zuobiao")
        qianshu.qianming_daxiao = qianshu_data.get("qianming_daxiao")
        qianshu.qianshu_zhuangtai = "yiqianshu"
        
        # 更新合同状态
        hetong = self.db.query(Hetong).filter(
            and_(Hetong.id == qianshu.hetong_id, Hetong.is_deleted == "N")
        ).first()
        
        if hetong:
            hetong.hetong_zhuangtai = "yiqianshu"
            hetong.qianshu_shijian = datetime.utcnow()
        
        self.db.commit()
        return True

    def get_qianshu_by_hetong(self, hetong_id: str) -> Optional[Dict[str, Any]]:
        """
        根据合同ID获取签署信息
        
        Args:
            hetong_id: 合同ID
            
        Returns:
            签署信息
        """
        qianshu = self.db.query(HetongQianshu).filter(
            and_(
                HetongQianshu.hetong_id == hetong_id,
                HetongQianshu.is_deleted == "N"
            )
        ).order_by(HetongQianshu.created_at.desc()).first()
        
        if not qianshu:
            return None
        
        return {
            "id": qianshu.id,
            "hetong_id": qianshu.hetong_id,
            "qianshu_lianjie": qianshu.qianshu_lianjie,
            "qianshu_token": qianshu.qianshu_token,
            "qianshu_zhuangtai": qianshu.qianshu_zhuangtai,
            "qianshu_ren_mingcheng": qianshu.qianshu_ren_mingcheng,
            "qianshu_ren_dianhua": qianshu.qianshu_ren_dianhua,
            "qianshu_ren_youxiang": qianshu.qianshu_ren_youxiang,
            "qianshu_shijian": qianshu.qianshu_shijian,
            "qianming_tupian": qianshu.qianming_tupian,
            "youxiao_kaishi": qianshu.youxiao_kaishi,
            "youxiao_jieshu": qianshu.youxiao_jieshu,
            "created_at": qianshu.created_at
        }

    def cancel_qianshu(self, hetong_id: str, reason: str) -> bool:
        """
        取消合同签署
        
        Args:
            hetong_id: 合同ID
            reason: 取消原因
            
        Returns:
            是否成功
        """
        qianshu = self.db.query(HetongQianshu).filter(
            and_(
                HetongQianshu.hetong_id == hetong_id,
                HetongQianshu.qianshu_zhuangtai == "daiqianshu",
                HetongQianshu.is_deleted == "N"
            )
        ).first()
        
        if qianshu:
            qianshu.qianshu_zhuangtai = "yiquxiao"
            qianshu.beizhu = f"取消原因：{reason}"
            self.db.commit()
            return True
        
        return False

    def get_contract_by_token(self, token: str) -> Dict[str, Any]:
        """
        根据签署令牌获取合同信息

        Args:
            token: 签署令牌

        Returns:
            Dict[str, Any]: 合同和签署信息
        """
        # 查找签署记录
        qianshu = self.db.query(HetongQianshu).filter(
            and_(
                HetongQianshu.qianshu_token == token,
                HetongQianshu.is_deleted == "N"
            )
        ).first()

        if not qianshu:
            raise BusinessException("签署链接无效")

        # 检查是否过期
        if qianshu.youxiao_jieshu < datetime.utcnow():
            qianshu.qianshu_zhuangtai = "guoqi"
            self.db.commit()
            raise BusinessException("签署链接已过期")

        # 获取合同信息
        hetong = self.db.query(Hetong).filter(
            Hetong.id == qianshu.hetong_id
        ).first()

        if not hetong:
            raise BusinessException("合同不存在")

        # 获取客户信息
        from models.kehu_guanli.kehu import Kehu
        kehu = self.db.query(Kehu).filter(
            Kehu.id == hetong.kehu_id
        ).first()

        return {
            "contract": {
                "id": hetong.id,
                "hetong_bianhao": hetong.hetong_bianhao,
                "hetong_mingcheng": hetong.hetong_mingcheng,
                "hetong_neirong": hetong.hetong_neirong,
                "hetong_jine": float(hetong.hetong_jine) if hetong.hetong_jine else 0,
                "hetong_zhuangtai": hetong.hetong_zhuangtai,
                "shengxiao_riqi": hetong.shengxiao_riqi.isoformat() if hetong.shengxiao_riqi else None,
                "daoqi_riqi": hetong.daoqi_riqi.isoformat() if hetong.daoqi_riqi else None,
                "kehu": {
                    "id": kehu.id if kehu else None,
                    "gongsi_mingcheng": kehu.gongsi_mingcheng if kehu else None
                }
            },
            "signing_info": {
                "id": qianshu.id,
                "qianshu_zhuangtai": qianshu.qianshu_zhuangtai,
                "qianshu_ren_mingcheng": qianshu.qianshu_ren_mingcheng,
                "qianshu_shijian": qianshu.qianshu_shijian.isoformat() if qianshu.qianshu_shijian else None,
                "youxiao_jieshu": qianshu.youxiao_jieshu.isoformat() if qianshu.youxiao_jieshu else None
            }
        }

    def sign_contract(
        self,
        token: str,
        signer_name: str,
        signer_phone: str,
        signer_email: str,
        signature_image: str,
        signature_type: str,
        client_ip: str,
        user_agent: str
    ) -> Dict[str, Any]:
        """
        签署合同

        Args:
            token: 签署令牌
            signer_name: 签署人姓名
            signer_phone: 签署人电话
            signer_email: 签署人邮箱
            signature_image: 签名图片
            signature_type: 签名类型
            client_ip: 客户端IP
            user_agent: 用户代理

        Returns:
            Dict[str, Any]: 签署结果
        """
        # 查找签署记录
        qianshu = self.db.query(HetongQianshu).filter(
            and_(
                HetongQianshu.qianshu_token == token,
                HetongQianshu.qianshu_zhuangtai == "daiqianshu",
                HetongQianshu.is_deleted == "N"
            )
        ).first()

        if not qianshu:
            raise BusinessException("签署链接无效或已过期")

        # 检查是否过期
        if qianshu.youxiao_jieshu < datetime.utcnow():
            qianshu.qianshu_zhuangtai = "guoqi"
            self.db.commit()
            raise BusinessException("签署链接已过期")

        # 获取合同
        hetong = self.db.query(Hetong).filter(
            Hetong.id == qianshu.hetong_id
        ).first()

        if not hetong:
            raise BusinessException("合同不存在")

        # 更新签署信息
        now = datetime.utcnow()
        qianshu.qianshu_zhuangtai = "yiqianshu"
        qianshu.qianshu_ren_mingcheng = signer_name
        qianshu.qianshu_ren_dianhua = signer_phone
        qianshu.qianshu_ren_youxiang = signer_email
        qianshu.qianshu_shijian = now
        qianshu.qianshu_ip = client_ip
        qianshu.qianshu_shebei = user_agent
        qianshu.qianming_tupian = signature_image

        # 更新合同状态
        hetong.hetong_zhuangtai = "signed"
        hetong.qianshu_riqi = now
        hetong.shengxiao_riqi = now

        self.db.commit()

        return {
            "success": True,
            "message": "合同签署成功",
            "contract_id": hetong.id,
            "signed_at": now.isoformat()
        }
