"""
审批权责矩阵服务
用于管理角色权限映射和审批人自动分配
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.yonghu_guanli import Yonghu, Jiaose, YonghuJiaose


class ApprovalMatrixService:
    """审批权责矩阵服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_approval_matrix(self) -> Dict[str, Any]:
        """获取审批权责矩阵"""
        try:
            # 获取所有角色和用户信息
            roles = self.db.query(Jiaose).filter(Jiaose.is_deleted == "N").all()
            
            matrix = {
                "roles": [],
                "approval_levels": self._get_approval_levels(),
                "role_mappings": {}
            }
            
            for role in roles:
                # 获取角色下的用户
                users = self.db.query(Yonghu).join(YonghuJiaose).filter(
                    YonghuJiaose.jiaose_id == role.id,
                    Yonghu.is_deleted == "N",
                    Yonghu.zhuangtai == "active"
                ).all()
                
                role_info = {
                    "id": role.id,
                    "name": role.jiaose_ming,
                    "code": role.jiaose_bianma,
                    "description": role.miaoshu,
                    "users": [
                        {
                            "id": user.id,
                            "name": user.yonghu_ming,
                            "email": user.youxiang,
                            "department": getattr(user, 'bumen', ''),
                            "position": getattr(user, 'zhiwei', '')
                        }
                        for user in users
                    ],
                    "approval_authority": self._get_role_approval_authority(role.jiaose_bianma)
                }
                
                matrix["roles"].append(role_info)
                matrix["role_mappings"][role.jiaose_bianma] = role.id
            
            return matrix
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取审批矩阵失败: {str(e)}")
    
    def assign_approver(self, role_code: str, amount: float = 0, department: str = None) -> Optional[str]:
        """
        根据角色代码和条件自动分配审批人
        
        Args:
            role_code: 角色代码
            amount: 金额（用于金额阈值判断）
            department: 部门（用于部门匹配）
            
        Returns:
            审批人用户ID
        """
        try:
            # 获取角色
            role = self.db.query(Jiaose).filter(
                Jiaose.jiaose_bianma == role_code,
                Jiaose.is_deleted == "N"
            ).first()
            
            if not role:
                return None
            
            # 获取角色下的活跃用户
            users_query = self.db.query(Yonghu).join(YonghuJiaose).filter(
                YonghuJiaose.jiaose_id == role.id,
                Yonghu.is_deleted == "N",
                Yonghu.zhuangtai == "active"
            )
            
            # 如果指定了部门，优先匹配同部门的审批人
            if department:
                dept_users = users_query.filter(Yonghu.bumen == department).all()
                if dept_users:
                    return self._select_best_approver(dept_users, amount)
            
            # 如果没有同部门的，或者没有指定部门，选择所有符合条件的用户
            all_users = users_query.all()
            if all_users:
                return self._select_best_approver(all_users, amount)
            
            return None
        except Exception as e:
            return None
    
    def get_approval_chain(self, rule_type: str, amount: float = 0) -> List[Dict[str, Any]]:
        """
        获取审批链
        
        Args:
            rule_type: 规则类型
            amount: 金额
            
        Returns:
            审批链列表
        """
        approval_levels = self._get_approval_levels()
        rule_config = approval_levels.get(rule_type, {})
        
        chain = []
        for level in rule_config.get("levels", []):
            min_amount = level.get("min_amount", 0)
            max_amount = level.get("max_amount", float('inf'))
            
            if min_amount <= amount < max_amount:
                approver_id = self.assign_approver(level["role_code"], amount)
                chain.append({
                    "level": level["level"],
                    "role_code": level["role_code"],
                    "role_name": level["role_name"],
                    "approver_id": approver_id,
                    "min_amount": min_amount,
                    "max_amount": max_amount if max_amount != float('inf') else None,
                    "required": level.get("required", True)
                })
        
        return chain
    
    def validate_approver_authority(self, user_id: str, role_code: str, amount: float = 0) -> bool:
        """
        验证审批人权限
        
        Args:
            user_id: 用户ID
            role_code: 角色代码
            amount: 金额
            
        Returns:
            是否有权限
        """
        try:
            # 检查用户是否有指定角色
            user_role = self.db.query(YonghuJiaose).join(Jiaose).filter(
                YonghuJiaose.yonghu_id == user_id,
                Jiaose.jiaose_bianma == role_code,
                Jiaose.is_deleted == "N"
            ).first()
            
            if not user_role:
                return False
            
            # 检查金额权限
            authority = self._get_role_approval_authority(role_code)
            max_amount = authority.get("max_amount", 0)
            
            if amount > max_amount and max_amount > 0:
                return False
            
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def get_approval_levels() -> Dict[str, Any]:
        """获取审批级别配置"""
        return {
            "hetong_jine_xiuzheng": {
                "name": "合同金额修正审批",
                "levels": [
                    {
                        "level": 1,
                        "role_code": "supervisor",
                        "role_name": "主管",
                        "min_amount": 0,
                        "max_amount": 50000,
                        "required": True
                    },
                    {
                        "level": 2,
                        "role_code": "manager",
                        "role_name": "经理",
                        "min_amount": 50000,
                        "max_amount": 200000,
                        "required": True
                    },
                    {
                        "level": 3,
                        "role_code": "director",
                        "role_name": "总监",
                        "min_amount": 200000,
                        "max_amount": float('inf'),
                        "required": True
                    }
                ]
            },
            "baojia_shenhe": {
                "name": "报价审核",
                "levels": [
                    {
                        "level": 1,
                        "role_code": "sales_manager",
                        "role_name": "销售经理",
                        "min_amount": 0,
                        "max_amount": 100000,
                        "required": True
                    },
                    {
                        "level": 2,
                        "role_code": "director",
                        "role_name": "总监",
                        "min_amount": 100000,
                        "max_amount": float('inf'),
                        "required": True
                    }
                ]
            },
            "zhifu_shenhe": {
                "name": "支付审核",
                "levels": [
                    {
                        "level": 1,
                        "role_code": "finance_manager",
                        "role_name": "财务经理",
                        "min_amount": 0,
                        "max_amount": 100000,
                        "required": True
                    },
                    {
                        "level": 2,
                        "role_code": "cfo",
                        "role_name": "财务总监",
                        "min_amount": 100000,
                        "max_amount": float('inf'),
                        "required": True
                    }
                ]
            }
        }
    
    @staticmethod
    def get_role_approval_authority(role_code: str) -> Dict[str, Any]:
        """获取角色审批权限"""
        authorities = {
            "supervisor": {"max_amount": 50000, "description": "主管级别审批权限"},
            "manager": {"max_amount": 200000, "description": "经理级别审批权限"},
            "director": {"max_amount": 1000000, "description": "总监级别审批权限"},
            "sales_manager": {"max_amount": 100000, "description": "销售经理审批权限"},
            "finance_manager": {"max_amount": 100000, "description": "财务经理审批权限"},
            "cfo": {"max_amount": 5000000, "description": "财务总监审批权限"},
            "ceo": {"max_amount": float('inf'), "description": "CEO无限制审批权限"}
        }
        return authorities.get(role_code, {"max_amount": 0, "description": "无审批权限"})
    
    @staticmethod
    def _select_best_approver(users: List[Yonghu], amount: float) -> Optional[str]:
        """
        从用户列表中选择最佳审批人
        
        Args:
            users: 用户列表
            amount: 金额
            
        Returns:
            最佳审批人ID
        """
        if not users:
            return None
        
        # 简单策略：选择第一个用户
        # 实际项目中可以根据工作负载、在线状态等因素选择
        return users[0].id
