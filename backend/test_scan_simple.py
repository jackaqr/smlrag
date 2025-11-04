"""
简单的 scan 功能测试（不需要 Dify API）
"""
import asyncio
from pathlib import Path

# 创建测试文件
data_dir = Path(__file__).parent / 'data'
data_dir.mkdir(exist_ok=True)

test_file = data_dir / 'test_scan.txt'
test_file.write_text('这是一个测试文件')

print("✅ 测试文件已创建")
print(f"📁 文件路径: {test_file}")
print(f"📄 文件内容: {test_file.read_text()}")

# 测试扫描逻辑（不上传）
async def test_scan():
    """测试扫描文件的基本逻辑"""
    file_count = 0
    
    for file in data_dir.glob('**/*'):
        if file.is_file() and not file.name.startswith('.'):
            print(f"✅ 发现文件: {file.name} (大小: {file.stat().st_size} 字节)")
            file_count += 1
    
    print(f"\n📊 扫描结果: 共找到 {file_count} 个文件")
    return file_count

# 运行测试
if __name__ == "__main__":
    print("=" * 50)
    print("测试 scan 基本功能")
    print("=" * 50)
    print()
    
    result = asyncio.run(test_scan())
    
    print()
    print("=" * 50)
    if result > 0:
        print("✅ 测试通过！")
    else:
        print("⚠️  未找到文件")
    print("=" * 50)

