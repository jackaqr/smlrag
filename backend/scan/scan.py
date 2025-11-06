import os
from pathlib import Path
from .upload import upload_file
import asyncio
import time

# 使用 backend 目录下的 data 目录
input_folder = Path(__file__).parent.parent / 'data'

print(f"扫描目录配置: {input_folder}")

async def scan_folder():
    """扫描文件夹并上传所有文件"""
    print(f"开始扫描目录: {input_folder}")
    file_count = 0
    
    # 确保目录存在
    if not input_folder.exists():
        print(f"目录不存在，创建目录: {input_folder}")
        input_folder.mkdir(parents=True, exist_ok=True)
    
    for file in input_folder.glob('**/*'):
        if file.is_file() and not file.name.startswith('.'):
            print(f"正在上传文件: {file}")
            try:
                result = await upload_file(file)
                print(f"上传成功: {file.name} - {result}")
                file_count += 1
            except Exception as e:
                print(f"上传失败: {file.name} - {str(e)}")
    
    print(f"扫描完成，共处理 {file_count} 个文件")
    return file_count


async def watch_and_scan(interval=60):
    """持续监控并扫描目录"""
    while True:
        try:
            await scan_folder()
        except Exception as e:
            print(f"扫描出错: {str(e)}")
        
        print(f"等待 {interval} 秒后进行下次扫描...")
        await asyncio.sleep(interval)

