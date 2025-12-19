"""
轻量级事件总线系统
用于处理业务事件的发布和订阅
"""
import logging
from typing import Dict, List, Callable, Any
from datetime import datetime
import asyncio
import traceback

logger = logging.getLogger(__name__)

class EventBus:
    """轻量级事件总线"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: List[Dict[str, Any]] = []
        self._max_history = 1000  # 最多保留1000条事件历史
    
    def subscribe(self, event_name: str, handler: Callable) -> None:
        """订阅事件
        
        Args:
            event_name: 事件名称
            handler: 事件处理函数
        """
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        
        self._subscribers[event_name].append(handler)
        logger.info(f"事件订阅成功: {event_name} -> {handler.__name__}")
    
    def unsubscribe(self, event_name: str, handler: Callable) -> None:
        """取消订阅事件
        
        Args:
            event_name: 事件名称
            handler: 事件处理函数
        """
        if event_name in self._subscribers:
            try:
                self._subscribers[event_name].remove(handler)
                logger.info(f"取消事件订阅: {event_name} -> {handler.__name__}")
            except ValueError:
                logger.warning(f"尝试取消不存在的订阅: {event_name} -> {handler.__name__}")
    
    def publish(self, event_name: str, payload: Dict[str, Any] = None) -> None:
        """发布事件（同步）
        
        Args:
            event_name: 事件名称
            payload: 事件数据
        """
        if payload is None:
            payload = {}
        
        # 记录事件历史
        event_record = {
            "event_name": event_name,
            "payload": payload,
            "timestamp": datetime.now(),
            "success_count": 0,
            "error_count": 0,
            "errors": []
        }
        
        logger.info(f"发布事件: {event_name}, 数据: {payload}")
        
        # 执行所有订阅者
        if event_name in self._subscribers:
            for handler in self._subscribers[event_name]:
                try:
                    handler(payload)
                    event_record["success_count"] += 1
                    logger.debug(f"事件处理成功: {event_name} -> {handler.__name__}")
                except Exception as e:
                    event_record["error_count"] += 1
                    error_info = f"{handler.__name__}: {str(e)}"
                    event_record["errors"].append(error_info)
                    logger.error(f"事件处理失败: {event_name} -> {error_info}")
                    logger.error(traceback.format_exc())
        else:
            logger.warning(f"没有找到事件的订阅者: {event_name}")
        
        # 保存事件历史
        self._add_event_history(event_record)
    
    async def publish_async(self, event_name: str, payload: Dict[str, Any] = None) -> None:
        """发布事件（异步）
        
        Args:
            event_name: 事件名称
            payload: 事件数据
        """
        if payload is None:
            payload = {}
        
        # 记录事件历史
        event_record = {
            "event_name": event_name,
            "payload": payload,
            "timestamp": datetime.now(),
            "success_count": 0,
            "error_count": 0,
            "errors": []
        }
        
        logger.info(f"发布异步事件: {event_name}, 数据: {payload}")
        
        # 执行所有订阅者
        if event_name in self._subscribers:
            tasks = []
            for handler in self._subscribers[event_name]:
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(self._handle_async_event(handler, payload, event_record))
                else:
                    # 同步函数在线程池中执行
                    tasks.append(self._handle_sync_event_async(handler, payload, event_record))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        else:
            logger.warning(f"没有找到事件的订阅者: {event_name}")
        
        # 保存事件历史
        self._add_event_history(event_record)
    
    @staticmethod
    async def _handle_async_event(handler: Callable, payload: Dict[str, Any], event_record: Dict[str, Any]) -> None:
        """处理异步事件"""
        try:
            await handler(payload)
            event_record["success_count"] += 1
            logger.debug(f"异步事件处理成功: {handler.__name__}")
        except Exception as e:
            event_record["error_count"] += 1
            error_info = f"{handler.__name__}: {str(e)}"
            event_record["errors"].append(error_info)
            logger.error(f"异步事件处理失败: {error_info}")
            logger.error(traceback.format_exc())
    
    @staticmethod
    async def _handle_sync_event_async(handler: Callable, payload: Dict[str, Any], event_record: Dict[str, Any]) -> None:
        """在线程池中处理同步事件"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, handler, payload)
            event_record["success_count"] += 1
            logger.debug(f"同步事件处理成功: {handler.__name__}")
        except Exception as e:
            event_record["error_count"] += 1
            error_info = f"{handler.__name__}: {str(e)}"
            event_record["errors"].append(error_info)
            logger.error(f"同步事件处理失败: {error_info}")
            logger.error(traceback.format_exc())
    
    def _add_event_history(self, event_record: Dict[str, Any]) -> None:
        """添加事件历史记录"""
        self._event_history.append(event_record)
        
        # 保持历史记录数量在限制内
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
    
    def get_event_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取事件历史记录
        
        Args:
            limit: 返回记录数量限制
            
        Returns:
            事件历史记录列表
        """
        return self._event_history[-limit:]
    
    def get_subscribers(self, event_name: str = None) -> Dict[str, List[str]]:
        """获取订阅者信息
        
        Args:
            event_name: 事件名称，为None时返回所有事件的订阅者
            
        Returns:
            订阅者信息字典
        """
        if event_name:
            if event_name in self._subscribers:
                return {event_name: [handler.__name__ for handler in self._subscribers[event_name]]}
            else:
                return {event_name: []}
        else:
            return {
                event: [handler.__name__ for handler in handlers]
                for event, handlers in self._subscribers.items()
            }

# 全局事件总线实例
event_bus = EventBus()

# 便捷函数
def subscribe(event_name: str, handler: Callable) -> None:
    """订阅事件"""
    event_bus.subscribe(event_name, handler)

def unsubscribe(event_name: str, handler: Callable) -> None:
    """取消订阅事件"""
    event_bus.unsubscribe(event_name, handler)

def publish(event_name: str, payload: Dict[str, Any] = None) -> None:
    """发布事件（同步）"""
    event_bus.publish(event_name, payload)

async def publish_async(event_name: str, payload: Dict[str, Any] = None) -> None:
    """发布事件（异步）"""
    await event_bus.publish_async(event_name, payload)

def get_event_history(limit: int = 100) -> List[Dict[str, Any]]:
    """获取事件历史记录"""
    return event_bus.get_event_history(limit)

def get_subscribers(event_name: str = None) -> Dict[str, List[str]]:
    """获取订阅者信息"""
    return event_bus.get_subscribers(event_name)

# 预定义的事件名称常量
class EventNames:
    """事件名称常量"""
    
    # 报价相关事件
    BAOJIA_CONFIRMED = "baojia_confirmed"  # 报价确认
    BAOJIA_REJECTED = "baojia_rejected"    # 报价拒绝
    BAOJIA_CREATED = "baojia_created"      # 报价创建
    BAOJIA_UPDATED = "baojia_updated"      # 报价更新
    BAOJIA_EXPIRED = "baojia_expired"      # 报价过期
    
    # 线索相关事件
    XIANSUO_STATUS_CHANGED = "xiansuo_status_changed"  # 线索状态变更
    XIANSUO_ASSIGNED = "xiansuo_assigned"              # 线索分配
    
    # 合同相关事件
    HETONG_DRAFT_TRIGGERED = "hetong_draft_triggered"  # 合同草稿触发
    HETONG_GENERATED = "hetong_generated"              # 合同生成
    HETONG_SIGNED = "hetong_signed"                    # 合同签署
    
    # 支付相关事件
    PAYMENT_ORDER_CREATED = "payment_order_created"  # 支付订单创建
    PAYMENT_SUCCESS = "payment_success"              # 支付成功
    PAYMENT_FAILED = "payment_failed"                # 支付失败
    PAYMENT_REFUNDED = "payment_refunded"            # 支付退款

    # 通知相关事件
    NOTIFICATION_SENT = "notification_sent"          # 通知发送
    NOTIFICATION_READ = "notification_read"          # 通知已读

    # 财务相关事件
    INVOICE_GENERATED = "invoice_generated"          # 发票生成
    INVOICE_CANCELLED = "invoice_cancelled"          # 发票作废
    FINANCIAL_RECORD_CREATED = "financial_record_created"  # 财务记录创建
