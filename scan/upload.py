import os
from pathlib import Path
import aiohttp

base_url = os.getenv('DIFY_API_URL')
api_key = os.getenv('DIFY_API_KEY')
headers = {
    'Authorization': f'Bearer {api_key}'
}

async def upload_file(file_path: Path):
    url = f'{base_url}/datasets'
    with open(file_path, 'rb') as f:
        files = {'file': f}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, files=files) as response:
            return await response.json()