from pathlib import Path
from pydantic import BaseModel
from typing import List

# 使用 backend 目录下的 data 目录
input_folder = Path(__file__).parent.parent / 'data'

class FileInfo(BaseModel):
    """单个文件信息"""
    name: str
    size: int

class ScanResult(BaseModel):
    """扫描结果"""
    total_files: int
    total_size: int
    files: List[FileInfo]
    scan_path: str

async def scan_folder() -> ScanResult:
    """扫描文件夹并返回文件列表"""
    # 确保目录存在
    if not input_folder.exists():
        input_folder.mkdir(parents=True, exist_ok=True)
    
    files: List[FileInfo] = []
    total_size = 0
    
    for file in input_folder.glob('**/*'):
        if file.is_file() and not file.name.startswith('.'):
            file_size = file.stat().st_size
            files.append(FileInfo(
                name=file.name,
                size=file_size
            ))
            total_size += file_size
    
    return ScanResult(
        total_files=len(files),
        total_size=total_size,
        files=files,
        scan_path=str(input_folder)
    )
