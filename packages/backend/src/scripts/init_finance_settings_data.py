"""
初始化财务设置数据
"""
import sys
import os
import uuid

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from core.config import settings

def init_zhichu_leibie_data():
    """初始化支出类别数据"""
    engine = create_engine(str(settings.DATABASE_URL))
    
    # 支出类别数据（根据用户提供的数据）
    zhichu_data = [
        # 日常行政经费
        {"fenlei": "日常行政经费", "mingcheng": "其他"},
        {"fenlei": "日常行政经费", "mingcheng": "转账手续费"},
        {"fenlei": "日常行政经费", "mingcheng": "维修费"},
        {"fenlei": "日常行政经费", "mingcheng": "快递费"},
        {"fenlei": "日常行政经费", "mingcheng": "招聘费"},
        {"fenlei": "日常行政经费", "mingcheng": "IT技术开发费"},
        {"fenlei": "日常行政经费", "mingcheng": "其他技术"},
        {"fenlei": "日常行政经费", "mingcheng": "财务软件服务费"},
        {"fenlei": "日常行政经费", "mingcheng": "程序开发费"},
        {"fenlei": "日常行政经费", "mingcheng": "域名与服务器"},
        {"fenlei": "日常行政经费", "mingcheng": "客户关系维护"},
        
        # 交通费
        {"fenlei": "交通费", "mingcheng": "车位费"},
        {"fenlei": "交通费", "mingcheng": "电动车购置"},
        {"fenlei": "交通费", "mingcheng": "出租车报销"},
        {"fenlei": "交通费", "mingcheng": "公交卡充值"},
        
        # 奖金
        {"fenlei": "奖金", "mingcheng": "建议采纳奖"},
        {"fenlei": "奖金", "mingcheng": "优秀员工奖"},
        
        # 广告费
        {"fenlei": "广告费", "mingcheng": "广告费"},
        
        # 房屋租金
        {"fenlei": "房屋租金", "mingcheng": "房屋租金"},
        
        # 电费及水费
        {"fenlei": "电费及水费", "mingcheng": "电费及水费"},
        
        # 福利费
        {"fenlei": "福利费", "mingcheng": "工服/文化衫"},
        {"fenlei": "福利费", "mingcheng": "商业保险"},
        {"fenlei": "福利费", "mingcheng": "员工拓展"},
        {"fenlei": "福利费", "mingcheng": "办公室零食"},
        {"fenlei": "福利费", "mingcheng": "高温补贴"},
        {"fenlei": "福利费", "mingcheng": "聚餐费"},
        {"fenlei": "福利费", "mingcheng": "生日礼金"},
        {"fenlei": "福利费", "mingcheng": "节日费"},
        
        # 办公费
        {"fenlei": "办公费", "mingcheng": "电脑购置"},
        {"fenlei": "办公费", "mingcheng": "饮用桶/瓶装水"},
        {"fenlei": "办公费", "mingcheng": "清洁用品及其他"},
        {"fenlei": "办公费", "mingcheng": "耗材（打印纸/封面）"},
        {"fenlei": "办公费", "mingcheng": "耗材（硒鼓）"},
        {"fenlei": "办公费", "mingcheng": "耗材（其他）"},
        {"fenlei": "办公费", "mingcheng": "办公室家具"},
        {"fenlei": "办公费", "mingcheng": "办公室装修"},
        
        # 通信费
        {"fenlei": "通信费", "mingcheng": "手机话费补贴"},
        {"fenlei": "通信费", "mingcheng": "上网费"},
        {"fenlei": "通信费", "mingcheng": "固定电话"},
        
        # 业务招待费
        {"fenlei": "业务招待费", "mingcheng": "业务招待费"},
        
        # 日常经营费用
        {"fenlei": "日常经营费用", "mingcheng": "日常经营费用"},
        
        # 税金
        {"fenlei": "税金", "mingcheng": "税金"},
        
        # 培训费
        {"fenlei": "培训费", "mingcheng": "培训费"},
        
        # 人员经费
        {"fenlei": "人员经费", "mingcheng": "劳动保险"},
        {"fenlei": "人员经费", "mingcheng": "住房公积金"},
        {"fenlei": "人员经费", "mingcheng": "工资"},
        
        # 客户相关支出
        {"fenlei": "客户相关支出", "mingcheng": "客户相关支出"},
        
        # 审计费
        {"fenlei": "审计费", "mingcheng": "审计费"},
        
        # 退款
        {"fenlei": "退款", "mingcheng": "退款"},
        
        # 其他
        {"fenlei": "其他", "mingcheng": "其它"},
        
        # 第三方地址费
        {"fenlei": "第三方地址费", "mingcheng": "第三方地址费"},
        
        # 垫付费用
        {"fenlei": "垫付费用", "mingcheng": "服务费"},
        {"fenlei": "垫付费用", "mingcheng": "其他垫付"},
        {"fenlei": "垫付费用", "mingcheng": "登报费"},
        {"fenlei": "垫付费用", "mingcheng": "刻章费"},
        {"fenlei": "垫付费用", "mingcheng": "代垫税金"},
        {"fenlei": "垫付费用", "mingcheng": "代垫税控"},
        
        # 合伙人分红
        {"fenlei": "合伙人分红", "mingcheng": "合伙人分红"},
        
        # 其他费用
        {"fenlei": "其他费用", "mingcheng": "其他费用"},
    ]
    
    with engine.connect() as conn:
        
        # 检查是否已有数据
        result = conn.execute(text("SELECT COUNT(*) as count FROM zhichu_leibie WHERE is_deleted = 'N'"))
        count = result.fetchone()[0]
        
        if count > 0:
            return
        
        # 插入数据
        paixu = 0
        for item in zhichu_data:
            item_id = str(uuid.uuid4())
            paixu += 1
            
            conn.execute(text("""
                INSERT INTO zhichu_leibie (
                    id, mingcheng, fenlei, paixu, zhuangtai, is_deleted, created_at
                ) VALUES (
                    :id, :mingcheng, :fenlei, :paixu, 'active', 'N', NOW()
                )
            """), {
                "id": item_id,
                "mingcheng": item["mingcheng"],
                "fenlei": item["fenlei"],
                "paixu": paixu
            })
        
        conn.commit()

def init_sample_data():
    """初始化示例数据"""
    engine = create_engine(str(settings.DATABASE_URL))
    
    with engine.connect() as conn:
        # 初始化收付款渠道示例数据
        qudao_data = [
            {
                "id": str(uuid.uuid4()),
                "mingcheng": "现金",
                "leixing": "shoufukuan",
                "paixu": 1
            },
            {
                "id": str(uuid.uuid4()),
                "mingcheng": "支付宝",
                "leixing": "shoukuan",
                "paixu": 2
            },
            {
                "id": str(uuid.uuid4()),
                "mingcheng": "微信",
                "leixing": "shoukuan",
                "paixu": 3
            },
            {
                "id": str(uuid.uuid4()),
                "mingcheng": "银行",
                "leixing": "shoufukuan",
                "paixu": 4
            }
        ]
        
        for qudao in qudao_data:
            conn.execute(text("""
                INSERT INTO shoufukuan_qudao (
                    id, mingcheng, leixing, paixu, zhuangtai, is_deleted, created_at
                ) VALUES (
                    :id, :mingcheng, :leixing, :paixu, 'active', 'N', NOW()
                )
            """), qudao)
        
        conn.commit()

if __name__ == "__main__":
    init_zhichu_leibie_data()
    init_sample_data()
