"""
تجهيز الـ Logging بحيث كل "خدمة" في المشروع ليها ملف log منفصل، بدل ما
كل حاجة تتخبط في ملف واحد. بينادى مرة واحدة بس من main.py عند البداية.

النتيجة (جوه logs/):
    browser.log    -> كل حاجة خاصة بفتح المتصفح وتسجيل الدخول
    watcher.log    -> اكتشاف الشاتات والرسائل
    parser.log     -> تحليل المرسل/النوع/الوسائط
    database.log   -> الحفظ في قاعدة البيانات والـ Dashboard
    errors.log     -> أي WARNING أو ERROR من أي مكان (نظرة سريعة على المشاكل)
"""

import sys
from loguru import logger

from config import LOGS_DIR


def _module_matches(record, prefixes: tuple[str, ...]) -> bool:
    return record["name"].split(".")[0] in prefixes


def configure_logging():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # منشيل الإعداد الافتراضي (اللي بيطبع على الشاشة) ونضيف واحد بشكل أوضح
    logger.remove()
    logger.add(sys.stderr, level="INFO",
               format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | {message}")

    logger.add(LOGS_DIR / "browser.log", level="DEBUG", rotation="5 MB",
               filter=lambda r: _module_matches(r, ("browser",)))

    logger.add(LOGS_DIR / "watcher.log", level="DEBUG", rotation="5 MB",
               filter=lambda r: _module_matches(r, ("watcher",)))

    logger.add(LOGS_DIR / "parser.log", level="DEBUG", rotation="5 MB",
               filter=lambda r: _module_matches(r, ("parser",)))

    logger.add(LOGS_DIR / "database.log", level="DEBUG", rotation="5 MB",
               filter=lambda r: _module_matches(r, ("database", "services", "dashboard")))

    # ملف واحد بيجمع أي مشكلة (WARNING فأعلى) من أي مكان في المشروع،
    # عشان لو حصل عطل تقدر تشوفه بسرعة من غير ما تفتش في كل الملفات
    logger.add(LOGS_DIR / "errors.log", level="WARNING", rotation="5 MB")
