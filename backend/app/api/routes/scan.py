from fastapi import APIRouter, HTTPException

from scan.scan import scan_folder

router = APIRouter(prefix="/api", tags=["Scan"])


@router.post("/scan")
async def scan_files():
    """
    扫描 data 目录中的所有文件
    返回扫描结果的详细信息
    """
    try:
        result = await scan_folder()
        return {
            "status": "ok",
            "message": "扫描完成",
            **result.model_dump(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"扫描失败: {exc}") from exc

