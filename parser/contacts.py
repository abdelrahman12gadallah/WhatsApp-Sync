"""
مسؤول عن استخراج رقم التليفون الحقيقي لصاحب الشات.

⚠️ ملحوظة مهمة:
الـ selectors هنا (زي aria-label, data-testid) بتتغير من واتساب لواتساب مع
كل تحديث. لو الكود بقى مبيلاقيش العناصر، افتح Chrome Dev Tools على
WhatsApp Web وحدّث الـ selectors دي.
"""

import re
from playwright.sync_api import Page
from loguru import logger

from services.cache import get_cached_phone, set_cached_phone

PHONE_REGEX = re.compile(r"\+?\d[\d\s\-]{7,}\d")


def resolve_phone_for_current_chat(page: Page, chat_name: str) -> str | None:
    """
    لو الرقم متخزن قبل كده في الـ Cache يرجعه على طول.
    غير كده يفتح Contact Info ويدور على الرقم ويخزنه.
    """
    cached = get_cached_phone(chat_name)
    if cached:
        return cached

    try:
        # فتح الـ Header بتاع الشات عشان يطلع Contact Info
        page.click('header[data-testid="conversation-header"]', timeout=5000)

        # انتظار ظهور بانل معلومات جهة الاتصال
        page.wait_for_selector('div[data-testid="contact-info-drawer"]', timeout=5000)

        # الرقم غالبًا بيكون في نص فرعي تحت الاسم
        panel_text = page.inner_text('div[data-testid="contact-info-drawer"]')
        match = PHONE_REGEX.search(panel_text)
        phone = match.group().strip() if match else None

        # قفل البانل تاني
        page.keyboard.press("Escape")

        if phone:
            set_cached_phone(chat_name, phone)
            logger.info(f"📞 اترسم رقم {chat_name} -> {phone}")
        else:
            logger.warning(f"مقدرتش ألاقي رقم لـ {chat_name} (ممكن يكون Group أو الاسم مش متسجل كرقم)")

        return phone

    except Exception as e:
        logger.warning(f"فشل استخراج رقم {chat_name}: {e}")
        return None
