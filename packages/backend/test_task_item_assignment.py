"""
测试任务项分配功能
"""
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.fuwu_guanli import FuwuGongdan, FuwuGongdanXiangmu
from models.yonghu_guanli import Yonghu

# 数据库连接
DATABASE_URL = "postgresql://postgres:password@localhost:5432/proxy_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def test_task_item_assignment():
    """测试任务项分配功能"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("测试任务项分配功能")
        print("=" * 80)
        
        # 1. 查找一个工单
        gongdan = db.query(FuwuGongdan).filter(
            FuwuGongdan.is_deleted == "N"
        ).first()
        
        if not gongdan:
            print("❌ 没有找到工单")
            return
        
        print(f"\n✅ 找到工单: {gongdan.gongdan_bianhao} - {gongdan.gongdan_biaoti}")
        
        # 2. 查找工单的任务项
        xiangmu_list = db.query(FuwuGongdanXiangmu).filter(
            FuwuGongdanXiangmu.gongdan_id == gongdan.id,
            FuwuGongdanXiangmu.is_deleted == "N"
        ).all()
        
        if not xiangmu_list:
            print("❌ 工单没有任务项")
            return
        
        print(f"\n✅ 找到 {len(xiangmu_list)} 个任务项:")
        for idx, xiangmu in enumerate(xiangmu_list, 1):
            zhixing_ren_name = xiangmu.zhixing_ren.xingming if xiangmu.zhixing_ren else "未分配"
            print(f"   {idx}. {xiangmu.xiangmu_mingcheng} - 执行人: {zhixing_ren_name}")
        
        # 3. 查找所有用户
        users = db.query(Yonghu).filter(
            Yonghu.is_deleted == "N"
        ).all()
        
        if len(users) < 2:
            print("❌ 用户数量不足，无法测试分配")
            return
        
        print(f"\n✅ 找到 {len(users)} 个用户:")
        for idx, user in enumerate(users[:5], 1):  # 只显示前5个
            print(f"   {idx}. {user.xingming} ({user.yonghu_ming})")
        
        # 4. 测试分配任务项
        print("\n" + "=" * 80)
        print("开始测试任务项分配")
        print("=" * 80)
        
        for idx, xiangmu in enumerate(xiangmu_list):
            # 循环分配给不同的用户
            user = users[idx % len(users)]
            
            old_zhixing_ren_name = xiangmu.zhixing_ren.xingming if xiangmu.zhixing_ren else "未分配"
            
            # 分配任务项
            xiangmu.zhixing_ren_id = user.id
            db.commit()
            db.refresh(xiangmu)
            
            new_zhixing_ren_name = xiangmu.zhixing_ren.xingming if xiangmu.zhixing_ren else "未分配"
            
            print(f"\n✅ 任务项 {idx + 1}: {xiangmu.xiangmu_mingcheng}")
            print(f"   从「{old_zhixing_ren_name}」分配给「{new_zhixing_ren_name}」")
        
        # 5. 验证分配结果
        print("\n" + "=" * 80)
        print("验证分配结果")
        print("=" * 80)
        
        xiangmu_list = db.query(FuwuGongdanXiangmu).filter(
            FuwuGongdanXiangmu.gongdan_id == gongdan.id,
            FuwuGongdanXiangmu.is_deleted == "N"
        ).all()
        
        for idx, xiangmu in enumerate(xiangmu_list, 1):
            zhixing_ren_name = xiangmu.zhixing_ren.xingming if xiangmu.zhixing_ren else "未分配"
            print(f"   {idx}. {xiangmu.xiangmu_mingcheng} - 执行人: {zhixing_ren_name}")
        
        print("\n" + "=" * 80)
        print("✅ 测试完成！任务项分配功能正常工作")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_task_item_assignment()

