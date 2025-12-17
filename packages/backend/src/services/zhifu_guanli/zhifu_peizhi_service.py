"""
支付配置管理服务
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status
from datetime import datetime

from models.zhifu_guanli import ZhifuPeizhi
from schemas.zhifu_guanli.zhifu_peizhi_schemas import (
    ZhifuPeizhiCreate,
    ZhifuPeizhiUpdate,
    ZhifuPeizhiResponse,
    ZhifuPeizhiDetail,
    ZhifuPeizhiListResponse
)
from core.security.encryption import encryption


class ZhifuPeizhiService:
    """支付配置管理服务类"""
    
    # 需要加密的字段列表
    ENCRYPTED_FIELDS = [
        'weixin_appid',
        'weixin_shanghu_hao',
        'weixin_shanghu_siyao',
        'weixin_zhengshu_xuliehao',
        'weixin_api_v3_miyao',
        'zhifubao_appid',
        'zhifubao_shanghu_siyao',
        'zhifubao_zhifubao_gongyao'
    ]
    
    def __init__(self, db: Session):
        self.db = db
    
    def _encrypt_sensitive_fields(self, data: dict) -> dict:
        """加密敏感字段"""
        encrypted_data = data.copy()
        for field in self.ENCRYPTED_FIELDS:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = encryption.encrypt(str(encrypted_data[field]))
        return encrypted_data
    
    def _decrypt_sensitive_fields(self, data: dict) -> dict:
        """解密敏感字段"""
        decrypted_data = data.copy()
        for field in self.ENCRYPTED_FIELDS:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = encryption.decrypt(str(decrypted_data[field]))
                except Exception:
                    # 如果解密失败，保持原值（可能是未加密的数据）
                    pass
        return decrypted_data
    
    def _mask_sensitive_data(self, value: Optional[str]) -> Optional[str]:
        """脱敏显示敏感数据"""
        if not value:
            return None
        if len(value) <= 8:
            return "****"
        return f"{value[:4]}****{value[-4:]}"
    
    def create_zhifu_peizhi(self, peizhi_data: ZhifuPeizhiCreate, created_by: str) -> ZhifuPeizhiResponse:
        """创建支付配置"""
        # 检查配置名称是否已存在
        existing = self.db.query(ZhifuPeizhi).filter(
            ZhifuPeizhi.peizhi_mingcheng == peizhi_data.peizhi_mingcheng,
            ZhifuPeizhi.is_deleted == "N"
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="配置名称已存在"
            )
        
        # 加密敏感字段
        peizhi_dict = peizhi_data.model_dump()
        encrypted_data = self._encrypt_sensitive_fields(peizhi_dict)
        
        # 创建支付配置
        zhifu_peizhi = ZhifuPeizhi(
            **encrypted_data,
            created_by=created_by
        )
        
        self.db.add(zhifu_peizhi)
        self.db.commit()
        self.db.refresh(zhifu_peizhi)
        
        return self._to_response(zhifu_peizhi)
    
    def get_zhifu_peizhi_by_id(self, peizhi_id: str) -> ZhifuPeizhiResponse:
        """根据ID获取支付配置（脱敏）"""
        zhifu_peizhi = self.db.query(ZhifuPeizhi).filter(
            ZhifuPeizhi.id == peizhi_id,
            ZhifuPeizhi.is_deleted == "N"
        ).first()
        
        if not zhifu_peizhi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付配置不存在"
            )
        
        return self._to_response(zhifu_peizhi)
    
    def get_zhifu_peizhi_detail(self, peizhi_id: str) -> ZhifuPeizhiDetail:
        """根据ID获取支付配置详情（解密，仅内部使用）"""
        zhifu_peizhi = self.db.query(ZhifuPeizhi).filter(
            ZhifuPeizhi.id == peizhi_id,
            ZhifuPeizhi.is_deleted == "N"
        ).first()
        
        if not zhifu_peizhi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付配置不存在"
            )
        
        return self._to_detail(zhifu_peizhi)
    
    def get_zhifu_peizhi_list(
        self,
        page: int = 1,
        page_size: int = 10,
        peizhi_leixing: Optional[str] = None,
        zhuangtai: Optional[str] = None,
        search: Optional[str] = None
    ) -> ZhifuPeizhiListResponse:
        """获取支付配置列表"""
        query = self.db.query(ZhifuPeizhi).filter(ZhifuPeizhi.is_deleted == "N")
        
        # 筛选条件
        if peizhi_leixing:
            query = query.filter(ZhifuPeizhi.peizhi_leixing == peizhi_leixing)
        
        if zhuangtai:
            query = query.filter(ZhifuPeizhi.zhuangtai == zhuangtai)
        
        if search:
            query = query.filter(
                or_(
                    ZhifuPeizhi.peizhi_mingcheng.ilike(f"%{search}%"),
                    ZhifuPeizhi.beizhu.ilike(f"%{search}%")
                )
            )
        
        # 总数
        total = query.count()
        
        # 分页
        query = query.order_by(desc(ZhifuPeizhi.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        items = [self._to_response(item) for item in query.all()]
        
        return ZhifuPeizhiListResponse(total=total, items=items)
    
    def update_zhifu_peizhi(
        self,
        peizhi_id: str,
        peizhi_data: ZhifuPeizhiUpdate,
        updated_by: str
    ) -> ZhifuPeizhiResponse:
        """更新支付配置"""
        zhifu_peizhi = self.db.query(ZhifuPeizhi).filter(
            ZhifuPeizhi.id == peizhi_id,
            ZhifuPeizhi.is_deleted == "N"
        ).first()
        
        if not zhifu_peizhi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付配置不存在"
            )
        
        # 检查配置名称是否与其他配置重复
        if peizhi_data.peizhi_mingcheng:
            existing = self.db.query(ZhifuPeizhi).filter(
                ZhifuPeizhi.peizhi_mingcheng == peizhi_data.peizhi_mingcheng,
                ZhifuPeizhi.id != peizhi_id,
                ZhifuPeizhi.is_deleted == "N"
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="配置名称已存在"
                )
        
        # 加密敏感字段
        update_dict = peizhi_data.model_dump(exclude_unset=True)
        encrypted_data = self._encrypt_sensitive_fields(update_dict)
        
        # 更新字段
        for key, value in encrypted_data.items():
            if value is not None:
                setattr(zhifu_peizhi, key, value)
        
        zhifu_peizhi.updated_by = updated_by
        zhifu_peizhi.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(zhifu_peizhi)
        
        return self._to_response(zhifu_peizhi)
    
    def delete_zhifu_peizhi(self, peizhi_id: str, deleted_by: str) -> bool:
        """删除支付配置（软删除）"""
        zhifu_peizhi = self.db.query(ZhifuPeizhi).filter(
            ZhifuPeizhi.id == peizhi_id,
            ZhifuPeizhi.is_deleted == "N"
        ).first()
        
        if not zhifu_peizhi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付配置不存在"
            )
        
        zhifu_peizhi.is_deleted = "Y"
        zhifu_peizhi.updated_by = deleted_by
        zhifu_peizhi.updated_at = datetime.now()
        
        self.db.commit()
        
        return True
    
    def get_active_config_by_type(self, peizhi_leixing: str) -> Optional[ZhifuPeizhiDetail]:
        """获取指定类型的启用配置（解密）"""
        zhifu_peizhi = self.db.query(ZhifuPeizhi).filter(
            ZhifuPeizhi.peizhi_leixing == peizhi_leixing,
            ZhifuPeizhi.zhuangtai == 'qiyong',
            ZhifuPeizhi.is_deleted == "N"
        ).first()
        
        if not zhifu_peizhi:
            return None
        
        return self._to_detail(zhifu_peizhi)
    
    def _to_response(self, peizhi: ZhifuPeizhi) -> ZhifuPeizhiResponse:
        """转换为响应模型（脱敏）"""
        # 解密数据
        peizhi_dict = {
            'id': peizhi.id,
            'peizhi_mingcheng': peizhi.peizhi_mingcheng,
            'peizhi_leixing': peizhi.peizhi_leixing,
            'zhuangtai': peizhi.zhuangtai,
            'huanjing': peizhi.huanjing,
            'tongzhi_url': peizhi.tongzhi_url,
            'beizhu': peizhi.beizhu,
            'created_at': peizhi.created_at,
            'updated_at': peizhi.updated_at,
            'created_by': peizhi.created_by,
            'updated_by': peizhi.updated_by
        }
        
        # 解密并脱敏显示（增加异常处理，避免解密失败导致API崩溃）
        if peizhi.weixin_appid:
            try:
                decrypted = encryption.decrypt(peizhi.weixin_appid)
                peizhi_dict['weixin_appid'] = decrypted
            except Exception:
                # 解密失败，返回脱敏占位符
                peizhi_dict['weixin_appid'] = '****'

        if peizhi.weixin_shanghu_hao:
            try:
                decrypted = encryption.decrypt(peizhi.weixin_shanghu_hao)
                peizhi_dict['weixin_shanghu_hao'] = decrypted
            except Exception:
                peizhi_dict['weixin_shanghu_hao'] = '****'

        if peizhi.weixin_shanghu_siyao:
            peizhi_dict['weixin_shanghu_siyao_masked'] = self._mask_sensitive_data(peizhi.weixin_shanghu_siyao)

        if peizhi.weixin_zhengshu_xuliehao:
            try:
                decrypted = encryption.decrypt(peizhi.weixin_zhengshu_xuliehao)
                peizhi_dict['weixin_zhengshu_xuliehao'] = decrypted
            except Exception:
                peizhi_dict['weixin_zhengshu_xuliehao'] = '****'

        if peizhi.weixin_api_v3_miyao:
            peizhi_dict['weixin_api_v3_miyao_masked'] = self._mask_sensitive_data(peizhi.weixin_api_v3_miyao)

        if peizhi.zhifubao_appid:
            try:
                decrypted = encryption.decrypt(peizhi.zhifubao_appid)
                peizhi_dict['zhifubao_appid'] = decrypted
            except Exception:
                peizhi_dict['zhifubao_appid'] = '****'

        # 支付宝网关不需要加密，直接返回
        if peizhi.zhifubao_wangguan:
            peizhi_dict['zhifubao_wangguan'] = peizhi.zhifubao_wangguan

        if peizhi.zhifubao_shanghu_siyao:
            peizhi_dict['zhifubao_shanghu_siyao_masked'] = self._mask_sensitive_data(peizhi.zhifubao_shanghu_siyao)

        if peizhi.zhifubao_zhifubao_gongyao:
            peizhi_dict['zhifubao_zhifubao_gongyao_masked'] = self._mask_sensitive_data(peizhi.zhifubao_zhifubao_gongyao)

        # 银行汇款配置
        if peizhi.yinhang_mingcheng:
            peizhi_dict['yinhang_mingcheng'] = peizhi.yinhang_mingcheng
        if peizhi.yinhang_zhanghu_mingcheng:
            peizhi_dict['yinhang_zhanghu_mingcheng'] = peizhi.yinhang_zhanghu_mingcheng
        if peizhi.yinhang_zhanghu_haoma:
            peizhi_dict['yinhang_zhanghu_haoma'] = peizhi.yinhang_zhanghu_haoma
        if peizhi.kaihuhang_mingcheng:
            peizhi_dict['kaihuhang_mingcheng'] = peizhi.kaihuhang_mingcheng
        if peizhi.kaihuhang_lianhanghao:
            peizhi_dict['kaihuhang_lianhanghao'] = peizhi.kaihuhang_lianhanghao

        return ZhifuPeizhiResponse(**peizhi_dict)
    
    def _to_detail(self, peizhi: ZhifuPeizhi) -> ZhifuPeizhiDetail:
        """转换为详情模型（解密，不脱敏）"""
        print(f"🔍 _to_detail 开始处理配置: {peizhi.peizhi_mingcheng}, 类型: {peizhi.peizhi_leixing}")
        print(f"🔍 数据库中的支付宝字段:")
        print(f"  - zhifubao_appid: {peizhi.zhifubao_appid[:20] if peizhi.zhifubao_appid else None}...")
        print(f"  - zhifubao_shanghu_siyao: {peizhi.zhifubao_shanghu_siyao[:20] if peizhi.zhifubao_shanghu_siyao else None}...")
        print(f"  - zhifubao_wangguan: {peizhi.zhifubao_wangguan}")

        peizhi_dict = {
            'id': peizhi.id,
            'peizhi_mingcheng': peizhi.peizhi_mingcheng,
            'peizhi_leixing': peizhi.peizhi_leixing,
            'zhuangtai': peizhi.zhuangtai,
            'huanjing': peizhi.huanjing,
            'tongzhi_url': peizhi.tongzhi_url,
            'beizhu': peizhi.beizhu,
            'created_at': peizhi.created_at,
            'updated_at': peizhi.updated_at,
            'created_by': peizhi.created_by,
            'updated_by': peizhi.updated_by
        }
        
        # 解密所有敏感字段
        encrypted_fields_map = {
            'weixin_appid': peizhi.weixin_appid,
            'weixin_shanghu_hao': peizhi.weixin_shanghu_hao,
            'weixin_shanghu_siyao': peizhi.weixin_shanghu_siyao,
            'weixin_zhengshu_xuliehao': peizhi.weixin_zhengshu_xuliehao,
            'weixin_api_v3_miyao': peizhi.weixin_api_v3_miyao,
            'zhifubao_appid': peizhi.zhifubao_appid,
            'zhifubao_shanghu_siyao': peizhi.zhifubao_shanghu_siyao,
            'zhifubao_zhifubao_gongyao': peizhi.zhifubao_zhifubao_gongyao
        }

        for field_name, encrypted_value in encrypted_fields_map.items():
            if encrypted_value:
                try:
                    decrypted_value = encryption.decrypt(encrypted_value)
                    peizhi_dict[field_name] = decrypted_value
                    print(f"  ✅ {field_name} 解密成功: {decrypted_value[:20] if decrypted_value and len(decrypted_value) > 20 else decrypted_value}...")
                except Exception as e:
                    # 解密失败，可能是明文数据，直接返回原值
                    print(f"  ⚠️  {field_name} 解密失败（可能是明文数据）: {str(e)}")
                    print(f"  ℹ️  使用原值（明文）: {encrypted_value[:20] if len(encrypted_value) > 20 else encrypted_value}...")
                    peizhi_dict[field_name] = encrypted_value
            else:
                peizhi_dict[field_name] = None

        # 支付宝网关不需要加密，直接返回（确保字段存在，即使为空）
        peizhi_dict['zhifubao_wangguan'] = peizhi.zhifubao_wangguan or None

        # 银行汇款配置（确保字段存在，即使为空）
        peizhi_dict['yinhang_mingcheng'] = peizhi.yinhang_mingcheng or None
        peizhi_dict['yinhang_zhanghu_mingcheng'] = peizhi.yinhang_zhanghu_mingcheng or None
        peizhi_dict['yinhang_zhanghu_haoma'] = peizhi.yinhang_zhanghu_haoma or None
        peizhi_dict['kaihuhang_mingcheng'] = peizhi.kaihuhang_mingcheng or None
        peizhi_dict['kaihuhang_lianhanghao'] = peizhi.kaihuhang_lianhanghao or None

        print(f"🔍 解密后的字典内容:")
        print(f"  - zhifubao_appid: {peizhi_dict.get('zhifubao_appid', 'NOT_SET')}")
        print(f"  - zhifubao_shanghu_siyao: {peizhi_dict.get('zhifubao_shanghu_siyao', 'NOT_SET')[:20] if peizhi_dict.get('zhifubao_shanghu_siyao') else 'NOT_SET'}...")
        print(f"  - zhifubao_wangguan: {peizhi_dict.get('zhifubao_wangguan', 'NOT_SET')}")

        result = ZhifuPeizhiDetail(**peizhi_dict)
        print(f"🔍 返回的 ZhifuPeizhiDetail 对象:")
        print(f"  - zhifubao_appid: {result.zhifubao_appid}")
        print(f"  - zhifubao_shanghu_siyao: {result.zhifubao_shanghu_siyao[:20] if result.zhifubao_shanghu_siyao else None}...")
        print(f"  - zhifubao_wangguan: {result.zhifubao_wangguan}")

        return result

