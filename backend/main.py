"""
应用入口：仅负责创建并启动 FastAPI 应用
"""
import logging
import sys

from app import create_app

# ANSI 颜色（与 uvicorn 一致：INFO 绿色）
_GREEN = "\033[32m"  # INFO
_RESET = "\033[0m"


class _ColoredFormatter(logging.Formatter):
    """在终端下把 INFO 打成绿色"""
    def format(self, record):
        if sys.stdout.isatty() and record.levelno == logging.INFO:
            record.levelname = f"{_GREEN}{record.levelname}{_RESET}"
        return super().format(record)


# 让应用内 logger 带请求时间，时间放在 INFO 后面
_FMT = _ColoredFormatter(
    "%(levelname)s %(asctime)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# 为应用包下的 logger 单独加一个带 level 的 handler，避免被 uvicorn 的格式盖掉
for _name in ("app", "app.factory", "app.services", "app.services.ai"):
    _log = logging.getLogger(_name)
    _log.setLevel(logging.INFO)
    if not any(getattr(h, "stream", None) == sys.stdout for h in _log.handlers):
        _h = logging.StreamHandler(sys.stdout)
        _h.setFormatter(_FMT)
        _log.addHandler(_h)
    _log.propagate = False  # 不传给 root，只用自己的 handler，保证带 INFO 的格式只打一次

app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5301)

