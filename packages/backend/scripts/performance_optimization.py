"""
系统性能优化脚本
"""
import asyncio
import time
from typing import List, Dict, Any
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import get_db, engine
from src.core.config import settings


class PerformanceOptimizer:
    """性能优化器"""

    def __init__(self):
        self.engine = engine
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def create_indexes(self):
        """创建性能优化索引"""
        indexes = [
            # 审核相关索引
            "CREATE INDEX IF NOT EXISTS idx_shenhe_liucheng_guanlian ON shenhe_liucheng(guanlian_id, shenhe_leixing)",
            "CREATE INDEX IF NOT EXISTS idx_shenhe_liucheng_zhuangtai ON shenhe_liucheng(shenhe_zhuangtai, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_shenhe_jilu_liucheng ON shenhe_jilu(liucheng_id, buzhou_bianhao)",
            "CREATE INDEX IF NOT EXISTS idx_shenhe_jilu_shenhe_ren ON shenhe_jilu(shenhe_ren_id, jilu_zhuangtai)",
            
            # 合同相关索引
            "CREATE INDEX IF NOT EXISTS idx_hetong_zhuangtai_time ON hetong(hetong_zhuangtai, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_hetong_baojia ON hetong(baojia_id)",
            "CREATE INDEX IF NOT EXISTS idx_hetong_qianshu_hetong ON hetong_qianshu(hetong_id, qianshu_zhuangtai)",
            "CREATE INDEX IF NOT EXISTS idx_hetong_qianshu_token ON hetong_qianshu(qianshu_token)",
            
            # 支付相关索引
            "CREATE INDEX IF NOT EXISTS idx_hetong_zhifu_hetong ON hetong_zhifu(hetong_id, zhifu_zhuangtai)",
            "CREATE INDEX IF NOT EXISTS idx_hetong_zhifu_time ON hetong_zhifu(zhifu_shijian, zhifu_zhuangtai)",
            "CREATE INDEX IF NOT EXISTS idx_yinhang_huikuan_zhifu ON yinhang_huikuan_danju(hetong_zhifu_id, shenhe_zhuangtai)",
            
            # 线索相关索引
            "CREATE INDEX IF NOT EXISTS idx_xiansuo_zhuangtai_time ON xiansuo(xiansuo_zhuangtai_id, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_xiansuo_baojia_xiansuo ON xiansuo_baojia(xiansuo_id, baojia_zhuangtai)",
            "CREATE INDEX IF NOT EXISTS idx_xiansuo_baojia_time ON xiansuo_baojia(created_at, is_expired)",
            
            # 用户相关索引
            "CREATE INDEX IF NOT EXISTS idx_yonghu_zhuangtai ON yonghu(yonghu_zhuangtai, is_deleted)",
            "CREATE INDEX IF NOT EXISTS idx_yonghu_jiaose ON yonghu_jiaose_guanxi(yonghu_id, jiaose_id)",
        ]

        db = self.SessionLocal()
        try:
            for index_sql in indexes:
                print(f"创建索引: {index_sql}")
                db.execute(text(index_sql))
            db.commit()
            print("✓ 所有索引创建完成")
        except Exception as e:
            print(f"✗ 创建索引失败: {e}")
            db.rollback()
        finally:
            db.close()

    def analyze_slow_queries(self) -> List[Dict[str, Any]]:
        """分析慢查询"""
        slow_queries = []
        
        # 启用慢查询日志分析
        analysis_queries = [
            """
            SELECT 
                table_name,
                index_name,
                cardinality,
                pages
            FROM information_schema.statistics 
            WHERE table_schema = DATABASE()
            ORDER BY cardinality DESC
            """,
            
            """
            SELECT 
                table_name,
                table_rows,
                data_length,
                index_length,
                (data_length + index_length) as total_size
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            ORDER BY total_size DESC
            """,
        ]

        db = self.SessionLocal()
        try:
            for query in analysis_queries:
                result = db.execute(text(query))
                rows = result.fetchall()
                slow_queries.append({
                    "query": query,
                    "results": [dict(row._mapping) for row in rows]
                })
        except Exception as e:
            print(f"分析查询失败: {e}")
        finally:
            db.close()

        return slow_queries

    def optimize_database_settings(self):
        """优化数据库设置"""
        optimization_queries = [
            # 优化InnoDB设置
            "SET GLOBAL innodb_buffer_pool_size = 1073741824",  # 1GB
            "SET GLOBAL innodb_log_file_size = 268435456",      # 256MB
            "SET GLOBAL innodb_flush_log_at_trx_commit = 2",
            "SET GLOBAL innodb_flush_method = 'O_DIRECT'",
            
            # 优化查询缓存
            "SET GLOBAL query_cache_size = 67108864",           # 64MB
            "SET GLOBAL query_cache_type = 1",
            
            # 优化连接设置
            "SET GLOBAL max_connections = 200",
            "SET GLOBAL wait_timeout = 28800",
        ]

        db = self.SessionLocal()
        try:
            for query in optimization_queries:
                try:
                    print(f"执行优化: {query}")
                    db.execute(text(query))
                except Exception as e:
                    print(f"优化失败 (可能需要管理员权限): {e}")
            db.commit()
            print("✓ 数据库优化完成")
        except Exception as e:
            print(f"✗ 数据库优化失败: {e}")
            db.rollback()
        finally:
            db.close()

    def cleanup_old_data(self, days: int = 90):
        """清理旧数据"""
        cleanup_queries = [
            # 清理过期的签署链接
            f"""
            UPDATE hetong_qianshu 
            SET is_deleted = 'Y' 
            WHERE qianshu_zhuangtai = 'guoqi' 
            AND youxiao_jieshu < DATE_SUB(NOW(), INTERVAL {days} DAY)
            """,
            
            # 清理已完成的审核流程（保留重要记录）
            f"""
            UPDATE shenhe_liucheng 
            SET is_deleted = 'Y' 
            WHERE shenhe_zhuangtai IN ('tongguo', 'jujue') 
            AND wancheng_shijian < DATE_SUB(NOW(), INTERVAL {days} DAY)
            """,
            
            # 清理过期的报价
            f"""
            UPDATE xiansuo_baojia 
            SET is_deleted = 'Y' 
            WHERE is_expired = 'Y' 
            AND created_at < DATE_SUB(NOW(), INTERVAL {days} DAY)
            """,
        ]

        db = self.SessionLocal()
        try:
            for query in cleanup_queries:
                print(f"执行清理: {query}")
                result = db.execute(text(query))
                print(f"影响行数: {result.rowcount}")
            db.commit()
            print("✓ 数据清理完成")
        except Exception as e:
            print(f"✗ 数据清理失败: {e}")
            db.rollback()
        finally:
            db.close()

    def generate_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        report = {
            "timestamp": time.time(),
            "database_size": {},
            "table_stats": [],
            "index_usage": [],
            "slow_queries": []
        }

        db = self.SessionLocal()
        try:
            # 获取数据库大小
            size_query = """
            SELECT 
                table_schema as 'database_name',
                SUM(data_length + index_length) / 1024 / 1024 as 'size_mb'
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            GROUP BY table_schema
            """
            result = db.execute(text(size_query))
            size_data = result.fetchone()
            if size_data:
                report["database_size"] = dict(size_data._mapping)

            # 获取表统计信息
            table_stats_query = """
            SELECT 
                table_name,
                table_rows,
                ROUND(data_length / 1024 / 1024, 2) as data_size_mb,
                ROUND(index_length / 1024 / 1024, 2) as index_size_mb
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            ORDER BY (data_length + index_length) DESC
            LIMIT 20
            """
            result = db.execute(text(table_stats_query))
            report["table_stats"] = [dict(row._mapping) for row in result.fetchall()]

            # 获取索引使用情况
            index_usage_query = """
            SELECT 
                table_name,
                index_name,
                cardinality,
                CASE 
                    WHEN cardinality = 0 THEN 'Unused'
                    WHEN cardinality < 100 THEN 'Low Usage'
                    ELSE 'Active'
                END as usage_status
            FROM information_schema.statistics 
            WHERE table_schema = DATABASE()
            AND index_name != 'PRIMARY'
            ORDER BY cardinality DESC
            """
            result = db.execute(text(index_usage_query))
            report["index_usage"] = [dict(row._mapping) for row in result.fetchall()]

        except Exception as e:
            print(f"生成性能报告失败: {e}")
        finally:
            db.close()

        return report

    def run_full_optimization(self):
        """运行完整优化"""
        print("开始系统性能优化...")
        
        print("\n1. 创建性能索引...")
        self.create_indexes()
        
        print("\n2. 分析慢查询...")
        slow_queries = self.analyze_slow_queries()
        for i, query_info in enumerate(slow_queries):
            print(f"查询 {i+1}: {len(query_info['results'])} 条结果")
        
        print("\n3. 优化数据库设置...")
        self.optimize_database_settings()
        
        print("\n4. 清理旧数据...")
        self.cleanup_old_data()
        
        print("\n5. 生成性能报告...")
        report = self.generate_performance_report()
        
        print("\n性能优化完成!")
        print(f"数据库大小: {report.get('database_size', {}).get('size_mb', 0):.2f} MB")
        print(f"表数量: {len(report.get('table_stats', []))}")
        print(f"索引数量: {len(report.get('index_usage', []))}")
        
        return report


async def main():
    """主函数"""
    optimizer = PerformanceOptimizer()
    report = optimizer.run_full_optimization()
    
    # 保存报告到文件
    import json
    with open("performance_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print("\n性能报告已保存到 performance_report.json")


if __name__ == "__main__":
    asyncio.run(main())
