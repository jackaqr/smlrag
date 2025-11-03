import os
from pathlib import Path
import aiohttp

base_url = os.getenv('DIFY_BASE_URL')
api_key = os.getenv('DIFY_API_KEY')

async def upload_file(file_path: Path):
    """上传文件到 Dify API"""
    if not base_url or not api_key:
        raise ValueError("请设置环境变量 DIFY_BASE_URL 和 DIFY_API_KEY")
    
    url = f'{base_url}/datasets/upload'
    
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    # 使用 aiohttp 的 FormData 来上传文件
    data = aiohttp.FormData()
    data.add_field('file',
                   open(file_path, 'rb'),
                   filename=file_path.name,
                   content_type='application/octet-stream')
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"上传失败 (HTTP {response.status}): {error_text}")

