"""
مراقبة الشات المفتوح حاليًا وقراءة الرسائل الجديدة بس (مش كل التاريخ).

الفكرة:
- كل رسالة في الـ DOM ليها data-id فريد.
- بنحتفظ بمجموعة (set) للـ ids اللي شفناها قبل كده في الجلسة دي.
- أي عنصر جديد لسه مش في المجموعة => رسالة جديدة => نستخرجها ونحفظها.

⚠️ الـ selectors دي تقريبية وبتتغير مع تحديثات واتساب، هتحتاج تراجعها
بنفسك بفتح Dev Tools على WhatsApp Web الحالي عندك.
"""

from playwright.sync_api import Page
from loguru import logger

from parser.contacts import resolve_phone_for_current_chat
from parser.sender import resolve_sender_name
from services.repository import save_message, get_session
from services.media import capture_image

seen_message_ids: set[str] = set()


def get_open_chat_name(page: Page) -> str | None:
    try:
        header = page.query_selector('header[data-testid="conversation-header"] span[dir="auto"]')
        return header.inner_text() if header else None
    except Exception:
        return None


def scan_current_chat(page: Page, chat_name: str | None = None) -> bool:
    """
    يفحص الشات المفتوح دلوقتي ويحفظ أي رسالة جديدة.
    يرجع True لو اتحفظت رسالة واحدة على الأقل (مفيد عشان نعرف إمتى
    نحدث الـ Dashboard).

    لو مررت chat_name (لما بنلف على شاتات كتير) بيتم استخدامه مباشرة،
    غير كده بيحاول يقرأه من الـ Header.
    """
    chat_name = chat_name or get_open_chat_name(page)
    if not chat_name:
        return False  # مفيش شات مفتوح دلوقتي

    message_rows = page.query_selector_all('div[data-id]')  # كل صف رسالة
    if not message_rows:
        return False

    new_rows = []
    for row in message_rows:
        msg_id = row.get_attribute("data-id")
        if msg_id and msg_id not in seen_message_ids:
            seen_message_ids.add(msg_id)
            new_rows.append((msg_id, row))

    if not new_rows:
        return False

    phone = resolve_phone_for_current_chat(page, chat_name)
    session = get_session()

    saved_any = False
    try:
        for msg_id, row in new_rows:
            if _extract_and_save(page, session, row, msg_id, chat_name, phone):
                saved_any = True
    finally:
        session.close()

    return saved_any


def _extract_and_save(page, session, row, msg_id: str, chat_name: str, phone: str | None) -> bool:
    try:
        is_from_me = "message-out" in (row.get_attribute("class") or "")

        text_el = row.query_selector('span.selectable-text')
        text = text_el.inner_text() if text_el else None

        message_type = "text"
        if not text:
            if row.query_selector('video'):
                message_type = "video"
            elif row.query_selector('div[data-icon="audio-play"], div[data-icon="ptt-cancel"]'):
                message_type = "voice"
            elif row.query_selector('div[data-icon="media-play"]'):
                message_type = "audio"
            elif row.query_selector('img[src*="sticker"]'):
                message_type = "sticker"
            elif row.query_selector('img'):
                message_type = "image"
            elif row.query_selector('div[data-icon="document"]'):
                message_type = "document"

        sender_name = resolve_sender_name(row, chat_name, is_from_me)

        file_path = None
        if message_type == "image":
            file_path = capture_image(row, msg_id, chat_name)
        # ملحوظة: audio/video/document حاليًا بيتسجل نوعها بس من غير
        # ملف، زي الـ Architecture المتفق عليه. لو حبينا نلتقطها كمان
        # لاحقًا، دي النقطة اللي هنوسّعها فيها.

        result = save_message(
            session=session,
            chat_name=chat_name,
            sender_name=sender_name,
            phone=phone,
            text=text,
            message_type=message_type,
            is_from_me=is_from_me,
            whatsapp_message_id=msg_id,
            file_path=file_path,
            original_filename=None,
        )
        return result is not None
    except Exception as e:
        logger.warning(f"فشل استخراج رسالة {msg_id}: {e}")
        return False
