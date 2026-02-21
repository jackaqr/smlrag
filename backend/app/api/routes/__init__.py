from fastapi import APIRouter

from .system import router as system_router
from .chat import chats_router, completions_router
from .scan import router as scan_router
from .admin import router as admin_router
from .video import router as video_router
from .images import router as images_router
from .config_routes import router as config_router

router = APIRouter()
router.include_router(system_router)
router.include_router(chats_router)
router.include_router(completions_router)
router.include_router(scan_router)
router.include_router(admin_router)
router.include_router(video_router)
router.include_router(images_router)
router.include_router(config_router)

