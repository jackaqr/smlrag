from fastapi import APIRouter

from .system import router as system_router
from .chat import router as chat_router
from .scan import router as scan_router
from .admin import router as admin_router

router = APIRouter()
router.include_router(system_router)
router.include_router(chat_router)
router.include_router(scan_router)
router.include_router(admin_router)

