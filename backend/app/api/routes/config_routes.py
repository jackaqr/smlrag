"""
配置 API：读取/更新模型配置、界面设置（持久化到 SQLite）
"""
from fastapi import APIRouter

from ...config_store import (
    CONFIG_KEY_MODEL,
    CONFIG_KEY_UI,
    get,
    get_default_model_config,
    get_default_ui_config,
    set_many,
)
from ...schemas.config_schema import ConfigResponse, ConfigUpdateRequest

router = APIRouter(prefix="/api/config", tags=["Config"])


def _deep_merge(base: dict, override: dict) -> dict:
    """递归合并 override 到 base，override 优先。不修改 base。"""
    out = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


@router.get("", response_model=ConfigResponse)
async def get_config():
    """
    获取当前配置（模型配置 + 界面设置）。
    未保存过的项使用默认值。
    """
    default_model = get_default_model_config()
    default_ui = get_default_ui_config()
    stored_model = get(CONFIG_KEY_MODEL)
    stored_ui = get(CONFIG_KEY_UI)
    model = _deep_merge(default_model, stored_model) if stored_model else default_model
    ui = _deep_merge(default_ui, stored_ui) if stored_ui else default_ui
    return ConfigResponse(model=model, ui=ui)


@router.put("", response_model=ConfigResponse)
async def update_config(request: ConfigUpdateRequest):
    """
    更新配置（只更新传入的 model / ui，与现有配置合并后持久化）。
    """
    default_model = get_default_model_config()
    default_ui = get_default_ui_config()
    stored_model = get(CONFIG_KEY_MODEL) or {}
    stored_ui = get(CONFIG_KEY_UI) or {}
    updates: dict = {}
    if request.model is not None:
        merged = _deep_merge(_deep_merge(default_model, stored_model), request.model)
        # 对每个模态的 models 做整体替换，以便前端可以“删除”某个模型（发送不含该 key 的 models）
        for mod in ("text", "image", "video"):
            if (
                request.model.get(mod) is not None
                and isinstance(request.model[mod], dict)
                and "models" in request.model[mod]
            ):
                if merged.get(mod) is None:
                    merged[mod] = {}
                merged[mod]["models"] = request.model[mod]["models"]
        updates[CONFIG_KEY_MODEL] = merged
    if request.ui is not None:
        new_ui = _deep_merge(_deep_merge(default_ui, stored_ui), request.ui)
        updates[CONFIG_KEY_UI] = new_ui
    if updates:
        set_many(updates)
    # 返回最新完整配置
    return await get_config()
