"""
تشغيل المشروع:

    python main.py

أول مرة هيفتح متصفح وتعمل Scan لـ QR كود بموبايلك.
بعد كده هيفضل يراقب الشات المفتوح ويحفظ أي رسالة جديدة أول ما توصل.

⚠️ المرحلة دي بتراقب "الشات المفتوح حاليًا" بس (أبسط نقطة بداية).
لو عايز تراقب كل الشاتات في نفس الوقت، الخطوة الجاية إننا نضيف
Loop يتنقل بين الشاتات (هنعملها بعد ما نتأكد إن الأساس شغال tمام).
"""

import time
from loguru import logger

from config import FULL_CYCLE_INTERVAL_SECONDS, MAX_CHATS_PER_CYCLE, MAX_CONSECUTIVE_ERRORS
from logging_setup import configure_logging
from browser.browser import WhatsAppBrowser
from database.db import init_db, get_session
from watcher.messages import scan_current_chat
from watcher.chats import get_chat_names, open_chat_by_name
from dashboard.export import generate_dashboard


def run_full_cycle(page) -> bool:
    """يلف على كل الشاتات الظاهرة في الـ Sidebar ويفحص كل واحدة. يرجع True لو اتحفظت رسائل جديدة."""
    chat_names = get_chat_names(page, limit=MAX_CHATS_PER_CYCLE)

    if not chat_names:
        logger.warning("مفيش شاتات ظاهرة دلوقتي في الـ Sidebar.")
        return False

    logger.info(f"دورة جديدة على {len(chat_names)} شات...")

    any_new = False
    for name in chat_names:
        try:
            opened = open_chat_by_name(page, name)
            if not opened:
                continue
            if scan_current_chat(page, chat_name=name):
                any_new = True
        except Exception as e:
            # مشكلة في شات واحد منعملش توقف كل الدورة، نسجلها ونكمل اللي بعده
            logger.warning(f"اتخطينا شات '{name}' بسبب خطأ: {e}")
            continue

    return any_new


def main():
    configure_logging()
    init_db()
    logger.info("تم تجهيز قاعدة البيانات.")

    browser = WhatsAppBrowser()
    page = browser.start()

    logger.info(f"بدء المراقبة على كل الشاتات... (كل دورة {FULL_CYCLE_INTERVAL_SECONDS} ثانية)")

    consecutive_errors = 0
    try:
        while True:
            try:
                has_new_messages = run_full_cycle(page)
                consecutive_errors = 0  # نجحت الدورة، نصفر العداد

                if has_new_messages:
                    session = get_session()
                    try:
                        generate_dashboard(session)
                        logger.info("🔄 تم تحديث whatsapp_live.html")
                    except Exception as e:
                        logger.error(f"فشل تحديث الـ Dashboard: {e}")
                    finally:
                        session.close()

            except Exception as e:
                consecutive_errors += 1
                logger.error(f"خطأ غير متوقع في الدورة ({consecutive_errors}/{MAX_CONSECUTIVE_ERRORS}): {e}")

                if page.is_closed():
                    logger.warning("المتصفح اتقفل أو الاتصال اتقطع — جاري محاولة إعادة الفتح...")
                    try:
                        page = browser.start()
                        consecutive_errors = 0
                        logger.success("اتفتح المتصفح تاني بنجاح.")
                        continue
                    except Exception as reconnect_error:
                        logger.error(f"فشل إعادة فتح المتصفح: {reconnect_error}")

                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    logger.error(
                        "حصل عدد كبير من الأخطاء المتتالية — البرنامج هيوقف. "
                        "راجع logs/errors.log واعمل تشغيل تاني."
                    )
                    break

            time.sleep(FULL_CYCLE_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        logger.info("تم الإيقاف بواسطة المستخدم.")
    finally:
        browser.stop()


if __name__ == "__main__":
    main()
