"""
API 测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health_check():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_create_chat():
    """测试创建对话"""
    print("\n=== 测试创建对话 ===")
    response = requests.post(
        f"{BASE_URL}/api/chats",
        params={"chat_id": "test-chat-001"},
        json={"title": "测试对话"}
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_send_messages():
    """测试发送消息"""
    print("\n=== 测试发送消息 ===")
    messages = [
        "你好！",
        "今天天气怎么样？",
        "谢谢你的回复"
    ]
    
    for msg in messages:
        response = requests.post(
            f"{BASE_URL}/api/chats/test-chat-001/messages",
            json={"content": msg}
        )
        print(f"发送: {msg}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_get_messages():
    """测试获取消息历史"""
    print("\n=== 测试获取消息历史 ===")
    response = requests.get(f"{BASE_URL}/api/chats/test-chat-001/messages")
    print(f"状态码: {response.status_code}")
    messages = response.json()
    print(f"消息数量: {len(messages)}")
    for i, msg in enumerate(messages, 1):
        print(f"\n消息 {i}:")
        print(f"  角色: {msg['role']}")
        print(f"  内容: {msg['content']}")
        print(f"  时间: {msg['timestamp']}")


def test_get_all_chats():
    """测试获取所有对话"""
    print("\n=== 测试获取所有对话 ===")
    response = requests.get(f"{BASE_URL}/api/chats")
    print(f"状态码: {response.status_code}")
    chats = response.json()
    print(f"对话数量: {len(chats)}")
    for chat in chats:
        print(f"\n对话 ID: {chat['id']}")
        print(f"  标题: {chat['title']}")
        print(f"  消息数: {chat['message_count']}")


def test_update_title():
    """测试更新对话标题"""
    print("\n=== 测试更新对话标题 ===")
    response = requests.put(
        f"{BASE_URL}/api/chats/test-chat-001/title",
        json={"title": "更新后的标题"}
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_stats():
    """测试统计信息"""
    print("\n=== 测试统计信息 ===")
    response = requests.get(f"{BASE_URL}/api/stats")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_delete_chat():
    """测试删除对话"""
    print("\n=== 测试删除对话 ===")
    response = requests.delete(f"{BASE_URL}/api/chats/test-chat-001")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


if __name__ == "__main__":
    try:
        print("开始测试 API...")
        test_health_check()
        test_create_chat()
        test_send_messages()
        test_get_messages()
        test_get_all_chats()
        test_update_title()
        test_stats()
        # test_delete_chat()  # 取消注释以测试删除
        
        print("\n\n✅ 所有测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器，请确保后端服务已启动:")
        print("   运行: python main.py")
        print("   或: docker-compose up")
    except Exception as e:
        print(f"\n❌ 测试出错: {str(e)}")

