"""
合同生成服务
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException
from datetime import datetime, timedelta
import re

from models.hetong_guanli.hetong import Hetong
from models.hetong_guanli.hetong_moban import HetongMoban
from models.xiansuo_guanli.xiansuo_baojia import XiansuoBaojia
from models.xiansuo_guanli.xiansuo import Xiansuo
from models.kehu_guanli.kehu import Kehu
from schemas.hetong_guanli.hetong_schemas import HetongCreate, HetongResponse


class HetongGenerateService:
    """合同生成服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_quote(self, baojia_id: str) -> XiansuoBaojia:
        """
        验证报价是否存在且已接受
        
        Args:
            baojia_id: 报价ID
            
        Returns:
            XiansuoBaojia: 报价对象
            
        Raises:
            HTTPException: 报价不存在或状态不正确
        """
        baojia = self.db.query(XiansuoBaojia).filter(
            and_(
                XiansuoBaojia.id == baojia_id,
                XiansuoBaojia.is_deleted == "N"
            )
        ).first()
        
        if not baojia:
            raise HTTPException(status_code=404, detail="报价不存在")
        
        if baojia.baojia_zhuangtai != "accepted":
            raise HTTPException(status_code=400, detail="只能基于已接受的报价生成合同")
        
        # 检查报价是否过期
        if baojia.youxiao_qi and baojia.youxiao_qi < datetime.now():
            raise HTTPException(status_code=400, detail="报价已过期，无法生成合同")
        
        return baojia
    
    def get_template_by_type(self, contract_type: str) -> str:
        """
        根据合同类型获取默认模板ID
        
        Args:
            contract_type: 合同类型
            
        Returns:
            str: 模板ID
            
        Raises:
            HTTPException: 模板不存在
        """
        template = self.db.query(HetongMoban).filter(
            and_(
                HetongMoban.moban_leixing == contract_type,
                HetongMoban.moban_zhuangtai == "active",
                HetongMoban.is_deleted == "N"
            )
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail=f"未找到{contract_type}类型的合同模板")
        
        return template.id
    
    def create_contract(self, contract_data: Dict[str, Any], created_by: str) -> HetongResponse:
        """
        创建合同
        
        Args:
            contract_data: 合同数据
            created_by: 创建人ID
            
        Returns:
            HetongResponse: 创建的合同
        """
        # 生成合同编号
        hetong_bianhao = self._generate_hetong_bianhao()
        
        # 获取合同模板
        template = self.db.query(HetongMoban).filter(
            HetongMoban.id == contract_data["hetong_moban_id"]
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="合同模板不存在")
        
        # 获取客户信息
        kehu = self.db.query(Kehu).filter(
            Kehu.id == contract_data["kehu_id"]
        ).first()
        
        if not kehu:
            raise HTTPException(status_code=404, detail="客户不存在")
        
        # 生成合同内容
        hetong_neirong = self._generate_contract_content(
            template=template,
            customer=kehu,
            contract_data=contract_data
        )
        
        # 设置合同到期日期（默认1年）
        daoqi_riqi = datetime.now() + timedelta(days=365)
        
        # 创建合同对象
        hetong = Hetong(
            kehu_id=contract_data["kehu_id"],
            hetong_moban_id=contract_data["hetong_moban_id"],
            baojia_id=contract_data.get("baojia_id"),
            yifang_zhuti_id=contract_data.get("yifang_zhuti_id"),
            hetong_bianhao=hetong_bianhao,
            hetong_mingcheng=contract_data["hetong_mingcheng"],
            hetong_neirong=hetong_neirong,
            hetong_zhuangtai="draft",
            hetong_jine=contract_data["hetong_jine"],
            daoqi_riqi=daoqi_riqi,
            hetong_laiyuan="auto_from_quote",
            zidong_shengcheng="Y",
            created_by=created_by
        )
        
        self.db.add(hetong)
        self.db.commit()
        self.db.refresh(hetong)
        
        return HetongResponse.model_validate(hetong)
    
    def preview_contract(self, template_id: str, customer_id: str, variables: Dict[str, Any]) -> str:
        """
        预览合同内容
        
        Args:
            template_id: 模板ID
            customer_id: 客户ID
            variables: 模板变量
            
        Returns:
            str: 渲染后的合同内容
        """
        # 获取模板
        template = self.db.query(HetongMoban).filter(
            HetongMoban.id == template_id
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="合同模板不存在")
        
        # 获取客户信息
        customer = self.db.query(Kehu).filter(
            Kehu.id == customer_id
        ).first()
        
        if not customer:
            raise HTTPException(status_code=404, detail="客户不存在")
        
        # 渲染模板
        content = self._render_template(template.moban_neirong, customer, variables)
        
        return content
    
    def get_contracts_by_quote(self, baojia_id: str) -> List[HetongResponse]:
        """
        获取指定报价生成的合同列表
        
        Args:
            baojia_id: 报价ID
            
        Returns:
            List[HetongResponse]: 合同列表
        """
        contracts = self.db.query(Hetong).filter(
            and_(
                Hetong.baojia_id == baojia_id,
                Hetong.is_deleted == "N"
            )
        ).all()
        
        return [HetongResponse.model_validate(contract) for contract in contracts]
    
    def get_available_templates(self, contract_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取可用的合同模板列表
        
        Args:
            contract_type: 合同类型过滤
            
        Returns:
            List[Dict[str, Any]]: 模板列表
        """
        query = self.db.query(HetongMoban).filter(
            and_(
                HetongMoban.moban_zhuangtai == "active",
                HetongMoban.is_deleted == "N"
            )
        )
        
        if contract_type:
            query = query.filter(HetongMoban.moban_leixing == contract_type)
        
        templates = query.all()
        
        return [
            {
                "id": template.id,
                "moban_mingcheng": template.moban_mingcheng,
                "moban_leixing": template.moban_leixing,
                "moban_miaoshu": template.moban_miaoshu,
                "moban_banben": template.moban_banben
            }
            for template in templates
        ]
    
    def _generate_hetong_bianhao(self) -> str:
        """
        生成合同编号
        
        Returns:
            str: 合同编号
        """
        # 获取当前日期
        today = datetime.now()
        date_str = today.strftime("%Y%m%d")
        
        # 查询当天已有的合同数量
        count = self.db.query(Hetong).filter(
            Hetong.hetong_bianhao.like(f"HT{date_str}%")
        ).count()
        
        # 生成编号：HT + 日期 + 4位序号
        sequence = str(count + 1).zfill(4)
        return f"HT{date_str}{sequence}"
    
    def _generate_contract_content(
        self, 
        template: HetongMoban, 
        customer: Kehu, 
        contract_data: Dict[str, Any]
    ) -> str:
        """
        生成合同内容
        
        Args:
            template: 合同模板
            customer: 客户信息
            contract_data: 合同数据
            
        Returns:
            str: 生成的合同内容
        """
        # 准备模板变量
        variables = {
            "hetong_bianhao": contract_data.get("hetong_bianhao", ""),
            "hetong_mingcheng": contract_data.get("hetong_mingcheng", ""),
            "hetong_jine": contract_data.get("hetong_jine", 0),
            "kehu_mingcheng": customer.gongsi_mingcheng,
            "kehu_lianxiren": customer.lianxiren,
            "kehu_dianhua": customer.lianxi_dianhua,
            "kehu_dizhi": customer.gongsi_dizhi,
            "qianshu_riqi": datetime.now().strftime("%Y年%m月%d日"),
            "shengxiao_riqi": datetime.now().strftime("%Y年%m月%d日"),
            "daoqi_riqi": (datetime.now() + timedelta(days=365)).strftime("%Y年%m月%d日")
        }
        
        # 渲染模板
        return self._render_template(template.moban_neirong, customer, variables)
    
    def _render_template(self, template_content: str, customer: Kehu, variables: Dict[str, Any]) -> str:
        """
        渲染模板内容
        
        Args:
            template_content: 模板内容
            customer: 客户信息
            variables: 模板变量
            
        Returns:
            str: 渲染后的内容
        """
        content = template_content
        
        # 替换变量
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        
        # 处理客户相关变量
        customer_vars = {
            "kehu_mingcheng": customer.gongsi_mingcheng,
            "kehu_lianxiren": customer.lianxiren,
            "kehu_dianhua": customer.lianxi_dianhua,
            "kehu_youxiang": customer.lianxi_youxiang,
            "kehu_dizhi": customer.gongsi_dizhi,
            "kehu_tongyi_shehui_xinyong_daima": customer.tongyi_shehui_xinyong_daima
        }
        
        for key, value in customer_vars.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value or ""))
        
        return content
