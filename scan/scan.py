import os
from pathlib import Path
from upload import upload_file
import asyncio
import time

# 使用当前文件的上一级目录的data目录，用.parent
input_folder = Path(__file__).parent / 'data'


async def scan_folder():
    """扫描文件夹并上传所有文件"""
    print(f"开始扫描目录: {input_folder}")
    file_count = 0
    
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


if __name__ == "__main__":
    # 运行一次扫描
    # asyncio.run(scan_folder())
    
    # 持续监控模式（每60秒扫描一次）
    print("启动文件扫描服务...")
    asyncio.run(watch_and_scan(interval=60))