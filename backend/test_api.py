import requests
import time
 
headers = {
    "Authorization": "Bearer QC-6d1572adcf49ed77911d01be083e7fd8-db064c3d3b4fce728350b6874ea9b880",
    "Content-Type": "application/json"
}
 
try:

    # 获取结果
    task_id = "1297042327210884494_437099"
    url = f"https://aiping.cn/api/v1/videos/{task_id}"
    response = requests.get(url, headers=headers)
    result = response.json()
    print("\n任务结果:")
    print(result)
except Exception as e:
    print(f"请求失败: {e}")
    print(f"响应内容: {response.text}")
