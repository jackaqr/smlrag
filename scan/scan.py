import os
from pathlib import Path
from upload import upload_file
import asyncio, uvicorn
# 使用当前文件的上一级目录的data目录，用.parent
input_folder = Path(__file__).parent / 'data'


async def scan_folder():
    for file in input_folder.glob('**/*'):
        if file.is_file():
            await upload_file(file)
            
asyncio.run(scan_folder())


if __name__ == "__main__":
    uvicorn.run("scan:scan_folder", host="0.0.0.0", port=8000, reload=True)