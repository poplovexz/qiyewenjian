"""
财务设置服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from fastapi import HTTPException, status
from datetime import datetime

from models.caiwu_guanli import (
    ShoufukuanQudao,
    ShouruLeibie,
    BaoxiaoLeibie,
    ZhichuLeibie
)
from schemas.caiwu_guanli.caiwu_shezhi_schemas import (
    ShoufukuanQudaoCreate,
    ShoufukuanQudaoUpdate,
    ShoufukuanQudaoResponse,
    ShoufukuanQudaoListResponse,
    ShouruLeibieCreate,
    ShouruLeibieUpdate,
    ShouruLeibieResponse,
    ShouruLeibieListResponse,
    BaoxiaoLeibieCreate,
    BaoxiaoLeibieUpdate,
    BaoxiaoLeibieResponse,
    BaoxiaoLeibieListResponse,
    ZhichuLeibieCreate,
    ZhichuLeibieUpdate,
    ZhichuLeibieResponse,
    ZhichuLeibieListResponse
)


class CaiwuShezhiService:
    """财务设置服务类"""

    def __init__(self, db: Session):
        self.db = db

    def _generate_bianma(self, model_class, prefix: str) -> str:
        """
        生成唯一编码
        格式: 前缀 + 时间戳(YYYYMMDD) + 序号(3位)
        例如: SR20251112001, BX20251112001, ZC20251112001
        """
        today = datetime.now().strftime("%Y%m%d")
        base_code = f"{prefix}{today}"

        # 查询今天已有的最大序号
        result = self.db.query(func.max(model_class.bianma)).filter(
            model_class.bianma.like(f"{base_code}%"),
            model_class.is_deleted == "N"
        ).scalar()

        if result:
            # 提取序号部分并加1
            try:
                last_seq = int(result[-3:])
                new_seq = last_seq + 1
            except (ValueError, IndexError):
                new_seq = 1
        else:
            new_seq = 1

        # 生成新编码，序号补齐3位
        return f"{base_code}{new_seq:03d}"

    # ==================== 收付款渠道 ====================
    def create_qudao(self, qudao_data: ShoufukuanQudaoCreate, created_by: str) -> ShoufukuanQudaoResponse:
        """创建收付款渠道"""
        qudao = ShoufukuanQudao(
            **qudao_data.model_dump(),
            created_by=created_by
        )
        self.db.add(qudao)
        self.db.commit()
        self.db.refresh(qudao)
        return ShoufukuanQudaoResponse.model_validate(qudao)
    
    def get_qudao_list(self, page: int = 1, size: int = 20, leixing: Optional[str] = None) -> ShoufukuanQudaoListResponse:
        """获取收付款渠道列表"""
        query = self.db.query(ShoufukuanQudao).filter(ShoufukuanQudao.is_deleted == "N")
        
        if leixing:
            query = query.filter(ShoufukuanQudao.leixing == leixing)
        
        total = query.count()
        offset = (page - 1) * size
        items = query.order_by(ShoufukuanQudao.paixu, desc(ShoufukuanQudao.created_at)).offset(offset).limit(size).all()
        pages = (total + size - 1) // size
        
        return ShoufukuanQudaoListResponse(
            items=[ShoufukuanQudaoResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    def get_qudao_by_id(self, qudao_id: str) -> ShoufukuanQudaoResponse:
        """根据ID获取收付款渠道"""
        qudao = self.db.query(ShoufukuanQudao).filter(
            ShoufukuanQudao.id == qudao_id,
            ShoufukuanQudao.is_deleted == "N"
        ).first()
        
        if not qudao:
            raise HTTPException(status_code=404, detail="收付款渠道不存在")
        
        return ShoufukuanQudaoResponse.model_validate(qudao)
    
    def update_qudao(self, qudao_id: str, qudao_data: ShoufukuanQudaoUpdate, updated_by: str) -> ShoufukuanQudaoResponse:
        """更新收付款渠道"""
        qudao = self.db.query(ShoufukuanQudao).filter(
            ShoufukuanQudao.id == qudao_id,
            ShoufukuanQudao.is_deleted == "N"
        ).first()
        
        if not qudao:
            raise HTTPException(status_code=404, detail="收付款渠道不存在")
        
        for key, value in qudao_data.model_dump(exclude_unset=True).items():
            setattr(qudao, key, value)
        
        qudao.updated_by = updated_by
        self.db.commit()
        self.db.refresh(qudao)
        return ShoufukuanQudaoResponse.model_validate(qudao)
    
    def delete_qudao(self, qudao_id: str):
        """删除收付款渠道"""
        qudao = self.db.query(ShoufukuanQudao).filter(
            ShoufukuanQudao.id == qudao_id,
            ShoufukuanQudao.is_deleted == "N"
        ).first()
        
        if not qudao:
            raise HTTPException(status_code=404, detail="收付款渠道不存在")
        
        qudao.is_deleted = "Y"
        self.db.commit()
    
    # ==================== 收入类别 ====================
    def create_shouru_leibie(self, leibie_data: ShouruLeibieCreate, created_by: str) -> ShouruLeibieResponse:
        """创建收入类别"""
        data_dict = leibie_data.model_dump()

        # 如果编码为空或None，自动生成
        if not data_dict.get('bianma'):
            data_dict['bianma'] = self._generate_bianma(ShouruLeibie, 'SR')

        leibie = ShouruLeibie(
            **data_dict,
            created_by=created_by
        )
        self.db.add(leibie)
        self.db.commit()
        self.db.refresh(leibie)
        return ShouruLeibieResponse.model_validate(leibie)
    
    def get_shouru_leibie_list(self, page: int = 1, size: int = 100) -> ShouruLeibieListResponse:
        """获取收入类别列表"""
        query = self.db.query(ShouruLeibie).filter(ShouruLeibie.is_deleted == "N")
        
        total = query.count()
        offset = (page - 1) * size
        items = query.order_by(ShouruLeibie.paixu, desc(ShouruLeibie.created_at)).offset(offset).limit(size).all()
        pages = (total + size - 1) // size
        
        return ShouruLeibieListResponse(
            items=[ShouruLeibieResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    def update_shouru_leibie(self, leibie_id: str, leibie_data: ShouruLeibieUpdate, updated_by: str) -> ShouruLeibieResponse:
        """更新收入类别"""
        leibie = self.db.query(ShouruLeibie).filter(
            ShouruLeibie.id == leibie_id,
            ShouruLeibie.is_deleted == "N"
        ).first()
        
        if not leibie:
            raise HTTPException(status_code=404, detail="收入类别不存在")
        
        for key, value in leibie_data.model_dump(exclude_unset=True).items():
            setattr(leibie, key, value)
        
        leibie.updated_by = updated_by
        self.db.commit()
        self.db.refresh(leibie)
        return ShouruLeibieResponse.model_validate(leibie)
    
    def delete_shouru_leibie(self, leibie_id: str):
        """删除收入类别"""
        leibie = self.db.query(ShouruLeibie).filter(
            ShouruLeibie.id == leibie_id,
            ShouruLeibie.is_deleted == "N"
        ).first()
        
        if not leibie:
            raise HTTPException(status_code=404, detail="收入类别不存在")
        
        leibie.is_deleted = "Y"
        self.db.commit()
    
    # ==================== 报销类别 ====================
    def create_baoxiao_leibie(self, leibie_data: BaoxiaoLeibieCreate, created_by: str) -> BaoxiaoLeibieResponse:
        """创建报销类别"""
        data_dict = leibie_data.model_dump()

        # 如果编码为空或None，自动生成
        if not data_dict.get('bianma'):
            data_dict['bianma'] = self._generate_bianma(BaoxiaoLeibie, 'BX')

        leibie = BaoxiaoLeibie(
            **data_dict,
            created_by=created_by
        )
        self.db.add(leibie)
        self.db.commit()
        self.db.refresh(leibie)
        return BaoxiaoLeibieResponse.model_validate(leibie)
    
    def get_baoxiao_leibie_list(self, page: int = 1, size: int = 100) -> BaoxiaoLeibieListResponse:
        """获取报销类别列表"""
        query = self.db.query(BaoxiaoLeibie).filter(BaoxiaoLeibie.is_deleted == "N")
        
        total = query.count()
        offset = (page - 1) * size
        items = query.order_by(BaoxiaoLeibie.paixu, desc(BaoxiaoLeibie.created_at)).offset(offset).limit(size).all()
        pages = (total + size - 1) // size
        
        return BaoxiaoLeibieListResponse(
            items=[BaoxiaoLeibieResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    def update_baoxiao_leibie(self, leibie_id: str, leibie_data: BaoxiaoLeibieUpdate, updated_by: str) -> BaoxiaoLeibieResponse:
        """更新报销类别"""
        leibie = self.db.query(BaoxiaoLeibie).filter(
            BaoxiaoLeibie.id == leibie_id,
            BaoxiaoLeibie.is_deleted == "N"
        ).first()
        
        if not leibie:
            raise HTTPException(status_code=404, detail="报销类别不存在")
        
        for key, value in leibie_data.model_dump(exclude_unset=True).items():
            setattr(leibie, key, value)
        
        leibie.updated_by = updated_by
        self.db.commit()
        self.db.refresh(leibie)
        return BaoxiaoLeibieResponse.model_validate(leibie)
    
    def delete_baoxiao_leibie(self, leibie_id: str):
        """删除报销类别"""
        leibie = self.db.query(BaoxiaoLeibie).filter(
            BaoxiaoLeibie.id == leibie_id,
            BaoxiaoLeibie.is_deleted == "N"
        ).first()
        
        if not leibie:
            raise HTTPException(status_code=404, detail="报销类别不存在")
        
        leibie.is_deleted = "Y"
        self.db.commit()
    
    # ==================== 支出类别 ====================
    def create_zhichu_leibie(self, leibie_data: ZhichuLeibieCreate, created_by: str) -> ZhichuLeibieResponse:
        """创建支出类别"""
        data_dict = leibie_data.model_dump()

        # 如果编码为空或None，自动生成
        if not data_dict.get('bianma'):
            data_dict['bianma'] = self._generate_bianma(ZhichuLeibie, 'ZC')

        leibie = ZhichuLeibie(
            **data_dict,
            created_by=created_by
        )
        self.db.add(leibie)
        self.db.commit()
        self.db.refresh(leibie)
        return ZhichuLeibieResponse.model_validate(leibie)
    
    def get_zhichu_leibie_list(self, page: int = 1, size: int = 200, fenlei: Optional[str] = None) -> ZhichuLeibieListResponse:
        """获取支出类别列表"""
        query = self.db.query(ZhichuLeibie).filter(ZhichuLeibie.is_deleted == "N")
        
        if fenlei:
            query = query.filter(ZhichuLeibie.fenlei == fenlei)
        
        total = query.count()
        offset = (page - 1) * size
        items = query.order_by(ZhichuLeibie.paixu, desc(ZhichuLeibie.created_at)).offset(offset).limit(size).all()
        pages = (total + size - 1) // size
        
        return ZhichuLeibieListResponse(
            items=[ZhichuLeibieResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    def update_zhichu_leibie(self, leibie_id: str, leibie_data: ZhichuLeibieUpdate, updated_by: str) -> ZhichuLeibieResponse:
        """更新支出类别"""
        leibie = self.db.query(ZhichuLeibie).filter(
            ZhichuLeibie.id == leibie_id,
            ZhichuLeibie.is_deleted == "N"
        ).first()
        
        if not leibie:
            raise HTTPException(status_code=404, detail="支出类别不存在")
        
        for key, value in leibie_data.model_dump(exclude_unset=True).items():
            setattr(leibie, key, value)
        
        leibie.updated_by = updated_by
        self.db.commit()
        self.db.refresh(leibie)
        return ZhichuLeibieResponse.model_validate(leibie)
    
    def delete_zhichu_leibie(self, leibie_id: str):
        """删除支出类别"""
        leibie = self.db.query(ZhichuLeibie).filter(
            ZhichuLeibie.id == leibie_id,
            ZhichuLeibie.is_deleted == "N"
        ).first()
        
        if not leibie:
            raise HTTPException(status_code=404, detail="支出类别不存在")
        
        leibie.is_deleted = "Y"
        self.db.commit()

