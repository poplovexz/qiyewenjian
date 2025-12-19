"""
文件上传API
"""
import os
import uuid
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models.yonghu_guanli import Yonghu

router = APIRouter()

# 上传目录配置
UPLOAD_DIR = "/var/www/uploads"
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/image", summary="上传图片")
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    上传图片文件
    
    支持的文件格式：JPG、PNG、GIF、WEBP
    文件大小限制：10MB
    
    返回：
    - url: 图片访问URL
    - filename: 原始文件名
    - size: 文件大小（字节）
    """
    # 检查文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="不支持的文件类型，请上传图片文件（JPG、PNG、GIF、WEBP）"
        )
    
    # 读取文件内容以检查大小
    contents = await file.read()
    file_size = len(contents)
    
    # 检查文件大小
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="文件大小不能超过10MB"
        )
    
    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # 按日期创建子目录
    date_dir = datetime.now().strftime("%Y%m%d")
    upload_path = os.path.join(UPLOAD_DIR, "images", date_dir)
    
    # 确保目录存在
    os.makedirs(upload_path, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_path, unique_filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # 生成访问URL
    file_url = f"/uploads/images/{date_dir}/{unique_filename}"
    
    return {
        "url": file_url,
        "filename": file.filename,
        "size": file_size,
        "content_type": file.content_type
    }

@router.post("/file", summary="上传文件")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    上传通用文件
    
    支持的文件格式：PDF、图片、文档等
    文件大小限制：10MB
    
    返回：
    - url: 文件访问URL
    - filename: 原始文件名
    - size: 文件大小（字节）
    """
    # 读取文件内容以检查大小
    contents = await file.read()
    file_size = len(contents)
    
    # 检查文件大小
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="文件大小不能超过10MB"
        )
    
    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # 按日期创建子目录
    date_dir = datetime.now().strftime("%Y%m%d")
    upload_path = os.path.join(UPLOAD_DIR, "files", date_dir)
    
    # 确保目录存在
    os.makedirs(upload_path, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_path, unique_filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # 生成访问URL
    file_url = f"/uploads/files/{date_dir}/{unique_filename}"
    
    return {
        "url": file_url,
        "filename": file.filename,
        "size": file_size,
        "content_type": file.content_type
    }
