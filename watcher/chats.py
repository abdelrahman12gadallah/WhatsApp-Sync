"""
مسؤول عن التعامل مع قائمة الشاتات (Sidebar):
- قراءة أسماء كل الشاتات الظاهرة.
- فتح شات معين بالاسم عشان نقدر نمسحه.

⚠️ زي باقي الملفات، الـ selectors دي تقريبية وممكن تحتاج تحديث لو
واتساب غيّر الـ HTML بتاعه.
"""

from playwright.sync_api import Page
from loguru import logger


def get_chat_names(page: Page, limit: int | None = None) -> list[str]:
    """
    يرجع أسماء الشاتات الظاهرة حاليًا في الـ Sidebar، مع ترتيبها بحيث
    الشاتات اللي فيها رسائل غير مقروءة (Unread) تيجي الأول — عشان
    الرسائل الجديدة تتفحص بسرعة أكبر بدل ما ننتظر نلف على كل حاجة.
    """
    rows = page.query_selector_all('div[aria-label="Chat list"] div[role="row"][data-testid^="list-item-"]')

    unread_names = []
    read_names = []

    for row in rows:
        title_el = row.query_selector('span[title]')
        if not title_el:
            continue
        name = title_el.get_attribute("title")
        if not name:
            continue

        # اكتشاف Badge الرسائل الغير مقروءة عن طريق data-testid الثابت
        # (بدل الاعتماد على aria-label اللي بيتغير مع لغة واجهة واتساب)
        has_unread = row.query_selector('[data-testid="icon-unread-count"]') is not None

        if has_unread:
            unread_names.append(name)
        else:
            read_names.append(name)

    ordered = unread_names + read_names
    return ordered[:limit] if limit else ordered


def open_chat_by_name(page: Page, name: str) -> bool:
    """يفتح شات معين بالاسم. يرجع True لو نجح."""
    try:
        # ندور على أول عنصر في الـ Sidebar بنفس الاسم بالظبط وننقر عليه
        selector = f'div[aria-label="Chat list"] span[title="{name}"]'
        page.click(selector, timeout=5000)
        page.wait_for_timeout(400)  # نستنى لحد ما محتوى الشات يتحمل
        return True
    except Exception as e:
        logger.warning(f"مقدرتش أفتح شات '{name}': {e}")
        return False
