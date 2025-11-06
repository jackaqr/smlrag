"""
测试文件扫描 API
"""
import requests
import os
from pathlib import Path

BASE_URL = "http://localhost:5301"

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    response = requests.get(f"{BASE_URL}/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_scan():
    """测试文件扫描"""
    print("📁 测试文件扫描...")
    
    # 确保 data 目录存在
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(exist_ok=True)
    
    # 创建测试文件
    test_file = data_dir / 'test_scan.txt'
    test_file.write_text('这是一个测试文件，用于验证文件扫描功能。')
    print(f"✅ 创建测试文件: {test_file}")
    
    # 调用扫描 API
    response = requests.post(f"{BASE_URL}/api/scan")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 扫描成功!")
        print(f"响应: {result}")
    else:
        print(f"❌ 扫描失败: {response.text}")
    print()

def test_all_endpoints():
    """测试所有端点"""
    print("=" * 50)
    print("开始测试 Smlrag 后端服务")
    print("=" * 50)
    print()
    
    try:
        test_health()
        
        # 注意: 扫描功能需要配置环境变量 DIFY_BASE_URL 和 DIFY_API_KEY
        if os.getenv('DIFY_BASE_URL') and os.getenv('DIFY_API_KEY'):
            test_scan()
        else:
            print("⚠️  跳过扫描测试: 未设置 DIFY_BASE_URL 和 DIFY_API_KEY 环境变量")
            print("   如需测试扫描功能，请设置这些环境变量")
            print()
        
        print("=" * 50)
        print("✅ 测试完成")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保后端服务正在运行")
        print(f"   服务地址: {BASE_URL}")
        print("   启动命令: python main.py")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    test_all_endpoints()

