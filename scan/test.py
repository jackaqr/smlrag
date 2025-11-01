import requests
import json

# Dify API 配置
url = 'http://localhost/v1/datasets'
params = {
    'page': 1,
    'limit': 20
}
headers = {
    'Authorization': 'Bearer dataset-KpjYVKzUbHHMZy7Xjr8NR9eb'
}                                                                           

# 发送请求
try:
    response = requests.get(url, params=params, headers=headers)
    
    # 打印状态码
    print(f"状态码: {response.status_code}")
    
    # 打印响应内容
    print(f"\n响应内容:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")
except json.JSONDecodeError:
    print(f"响应内容 (非JSON): {response.text}")
