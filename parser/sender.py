"""
استخراج اسم المرسل الحقيقي للرسالة.

واتساب ويب بيحط attribute اسمه data-pre-plain-text على عنصر جوه كل
رسالة، شكله تقريبًا:

    [10:15 ص, 22/07/2026] Ahmed:

ده بيبان في الجروبات عشان تعرف مين بعت، وأحيانًا في الشاتات الفردية
كمان. لو لقيناه، نستخرج الاسم منه لأنه أدق من افتراض إن "كل رسالة واردة
= صاحب الشات" (غلط في الجروبات).
"""

import re
from playwright.sync_api import ElementHandle

# بيلتقط أي حاجة بعد "] " ولحد قبل ":" الأخيرة
_PRE_PLAIN_REGEX = re.compile(r"\]\s*(.+?):\s*$")


def resolve_sender_name(row: ElementHandle, chat_name: str, is_from_me: bool) -> str:
    if is_from_me:
        return "Me"

    try:
        el = row.query_selector("[data-pre-plain-text]")
        if el:
            raw = el.get_attribute("data-pre-plain-text")
            if raw:
                match = _PRE_PLAIN_REGEX.search(raw)
                if match:
                    name = match.group(1).strip()
                    if name:
                        return name
    except Exception:
        pass

    # مفيش data-pre-plain-text أو مقدرناش نستخرج منه اسم -> نرجع لاسم الشات
    # (صح في الشات الفردي، تقريبي في الجروب لو الـ selector اتغير)
    return chat_name
