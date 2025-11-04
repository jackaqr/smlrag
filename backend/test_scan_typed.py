"""
测试带类型检查的 scan 功能
"""
import asyncio
from pathlib import Path
from scan.scan import scan_folder, ScanResult, FileInfo

async def test_scan():
    """测试扫描功能"""
    print("=" * 50)
    print("测试带类型检查的扫描功能")
    print("=" * 50)
    print()
    
    # 创建测试文件
    data_dir = Path("backend/data")
    data_dir.mkdir(exist_ok=True)
    
    test_file = data_dir / "test_typed.txt"
    test_file.write_text("这是一个测试文件")
    print(f"✅ 创建测试文件: {test_file.name}")
    print()
    
    # 调用扫描函数
    result: ScanResult = await scan_folder()
    
    # 类型检查会确保 result 是 ScanResult 类型
    print(f"📊 扫描结果:")
    print(f"  - 文件总数: {result.total_files}")
    print(f"  - 总大小: {result.total_size} 字节")
    print(f"  - 扫描路径: {result.scan_path}")
    print()
    
    print("📄 文件列表:")
    for file_info in result.files:
        # 类型检查会确保 file_info 是 FileInfo 类型
        print(f"  - {file_info.name} ({file_info.size} 字节)")
    
    print()
    print("=" * 50)
    print("✅ 类型检查测试通过！")
    print("=" * 50)
    
    # 测试转换为字典
    print()
    print("📋 转换为字典:")
    print(result.model_dump())

if __name__ == "__main__":
    asyncio.run(test_scan())

