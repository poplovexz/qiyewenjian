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
                HetongMoban.hetong_leixing == contract_type,
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
        import logging
        logger = logging.getLogger(__name__)

        try:
            # 获取模板
            logger.info(f"查询模板: {template_id}")
            template = self.db.query(HetongMoban).filter(
                HetongMoban.id == template_id
            ).first()

            if not template:
                logger.error(f"合同模板不存在: {template_id}")
                raise HTTPException(status_code=404, detail="合同模板不存在")

            logger.info(f"找到模板: {template.moban_mingcheng}")

            # 获取客户信息
            logger.info(f"查询客户: {customer_id}")
            customer = self.db.query(Kehu).filter(
                Kehu.id == customer_id
            ).first()

            if not customer:
                logger.error(f"客户不存在: {customer_id}")
                raise HTTPException(status_code=404, detail="客户不存在")

            logger.info(f"找到客户: {customer.gongsi_mingcheng}")

            # 渲染模板
            logger.info(f"开始渲染模板，变量: {variables}")
            content = self._render_template(template.moban_neirong, customer, variables)
            logger.info("模板渲染成功")

            return content

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"预览合同时发生错误: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"预览合同失败: {str(e)}")
    
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
            query = query.filter(HetongMoban.hetong_leixing == contract_type)
        
        templates = query.all()
        
        return [
            {
                "id": template.id,
                "moban_mingcheng": template.moban_mingcheng,
                "hetong_leixing": template.hetong_leixing,
                "moban_bianma": template.moban_bianma,
                "banben_hao": template.banben_hao
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
            "kehu_lianxiren": customer.faren_xingming,  # 使用法人姓名作为联系人
            "kehu_dianhua": customer.lianxi_dianhua,
            "kehu_dizhi": customer.lianxi_dizhi,  # 使用联系地址
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
        import logging
        logger = logging.getLogger(__name__)

        try:
            if not template_content:
                raise ValueError("模板内容为空")

            content = template_content

            # 替换变量
            logger.info(f"替换用户提供的变量: {list(variables.keys())}")
            for key, value in variables.items():
                placeholder = f"{{{{{key}}}}}"
                # 安全地转换值为字符串
                str_value = str(value) if value is not None else ""
                content = content.replace(placeholder, str_value)
                logger.debug(f"替换变量 {key}: {placeholder} -> {str_value}")

            # 处理客户相关变量
            logger.info(f"处理客户变量，客户: {customer.gongsi_mingcheng}")
            customer_vars = {
                "kehu_mingcheng": customer.gongsi_mingcheng or "",
                "kehu_lianxiren": customer.faren_xingming or "",  # 使用法人姓名作为联系人
                "kehu_dianhua": customer.lianxi_dianhua or "",
                "kehu_youxiang": customer.lianxi_youxiang or "",
                "kehu_dizhi": customer.lianxi_dizhi or "",  # 使用联系地址
                "kehu_tongyi_shehui_xinyong_daima": customer.tongyi_shehui_xinyong_daima or "",
                # 添加模板中使用的其他变量
                "faren_daibiao": customer.faren_xingming or "",  # 法定代表人
                "lianxi_dizhi": customer.lianxi_dizhi or "",  # 联系地址
                "lianxi_dianhua": customer.lianxi_dianhua or "",  # 联系电话
                "gongsi_mingcheng": customer.gongsi_mingcheng or "",  # 公司名称
                "zhuce_dizhi": customer.zhuce_dizhi or "",  # 注册地址
                "faren_xingming": customer.faren_xingming or "",  # 法人姓名
                "faren_shenfenzheng": customer.faren_shenfenzheng or "",  # 法人身份证
                "faren_lianxi": customer.faren_lianxi or "",  # 法人联系方式
                "chengli_riqi": customer.chengli_riqi.strftime("%Y年%m月%d日") if customer.chengli_riqi else "",  # 成立日期
            }

            for key, value in customer_vars.items():
                placeholder = f"{{{{{key}}}}}"
                str_value = str(value) if value is not None else ""
                content = content.replace(placeholder, str_value)
                logger.debug(f"替换客户变量 {key}: {placeholder} -> {str_value}")

            logger.info("模板变量替换完成")
            return content

        except Exception as e:
            logger.error(f"渲染模板时发生错误: {str(e)}", exc_info=True)
            raise
