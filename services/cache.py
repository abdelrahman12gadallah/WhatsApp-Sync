"""
Cache بسيط في الذاكرة: اسم الشخص -> رقم التليفون.
كده مش هنفتح Contact Info تاني لنفس الشخص كل رسالة.
"""

_contact_cache: dict[str, str] = {}


def get_cached_phone(name: str) -> str | None:
    return _contact_cache.get(name)


def set_cached_phone(name: str, phone: str):
    _contact_cache[name] = phone
