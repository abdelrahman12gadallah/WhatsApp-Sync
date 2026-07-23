"""
التقاط صورة الرسالة نفسها (مش تنزيل عبر قائمة الكليك يمين).

الفكرة: نعمل Screenshot لعنصر الـ <img> اللي جوه صف الرسالة بالظبط،
ونحفظه كملف PNG. أبسط وأضمن بكتير من فتح قائمة "Download" لأنه:
- مش محتاج نعرف نص القائمة بأي لغة.
- مش بيعتمد على سلوك تنزيل المتصفح.
- بيشتغل حتى لو الصورة لسه Thumbnail (بناخد اللي ظاهر فعليًا).

⚠️ بيلتقط الصورة اللي ظاهرة في المحادثة بس (مش صور بروفايل حد).
"""

from pathlib import Path
import re

from playwright.sync_api import ElementHandle
from loguru import logger

from config import MEDIA_DIR

_INVALID_CHARS = re.compile(r'[\\/:*?"<>|]')


def _safe_name(name: str) -> str:
    return _INVALID_CHARS.sub("_", name).strip() or "unknown"


def capture_image(row: ElementHandle, msg_id: str, chat_name: str) -> str | None:
    """
    يلتقط صورة الرسالة (لو موجودة) ويحفظها في
    media/images/<chat>/<msg_id>.png
    يرجع المسار المحلي، أو None لو فشل (الرسالة لسه بتتسجل عادي بدون ملف).
    """
    try:
        img_el = row.query_selector("img")
        if not img_el:
            return None

        folder = MEDIA_DIR / "images" / _safe_name(chat_name)
        folder.mkdir(parents=True, exist_ok=True)

        file_path = folder / f"{_safe_name(msg_id)}.png"
        img_el.screenshot(path=str(file_path))

        logger.info(f"🖼️  اتلقطت صورة: {file_path.name}")
        return str(file_path)

    except Exception as e:
        logger.debug(f"فشل التقاط صورة الرسالة {msg_id}: {e}")
        return None
