"""
工具函数模块
"""
import time
import json
from base64 import urlsafe_b64encode
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4


def _make_jwt_token(user_id: str, expires_in: int = 3600, extra_claims: Dict = None) -> str:
    """生成简单的JWT格式token（仅用于测试）"""
    # JWT Header
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    
    # JWT Payload
    now = int(time.time())
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + expires_in,
        "user_id": user_id,
        "iss": "proxy-accounting-system",
        "aud": "proxy-accounting-frontend"
    }
    
    # 添加额外的claims
    if extra_claims:
        payload.update(extra_claims)
    
    # 编码header和payload
    header_encoded = urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_encoded = urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    
    # 简单的签名（仅用于测试）
    signature = urlsafe_b64encode(f"test-signature-{user_id}-{now}".encode()).decode().rstrip('=')
    
    return f"{header_encoded}.{payload_encoded}.{signature}"


def _now_iso() -> str:
    """返回当前时间的ISO格式字符串"""
    return datetime.now().isoformat() + "Z"


def _paginate(items: List[Dict], page: int, size: int) -> Dict:
    """分页工具函数"""
    total = len(items)
    start = (page - 1) * size
    end = start + size
    pages = (total + size - 1) // size if total > 0 else 0
    
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }
