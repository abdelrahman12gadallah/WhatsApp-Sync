from loguru import logger

from database.db import get_session
from database.models import Contact, Chat, Message, Attachment


def get_or_create_chat(session, chat_name: str) -> Chat:
    chat = session.query(Chat).filter_by(chat_name=chat_name).first()
    if not chat:
        chat = Chat(chat_name=chat_name)
        session.add(chat)
        session.commit()
    return chat


def get_or_create_contact(session, name: str, phone: str | None, is_me: bool = False) -> Contact:
    contact = session.query(Contact).filter_by(name=name).first()
    if not contact:
        contact = Contact(name=name, phone=phone, is_me=is_me)
        session.add(contact)
        session.commit()
    elif phone and not contact.phone:
        # لو عرفنا الرقم دلوقتي وكان لسه مش معروف، حدّثه
        contact.phone = phone
        session.commit()
    return contact


def message_exists(session, whatsapp_message_id: str) -> bool:
    if not whatsapp_message_id:
        return False
    return (
        session.query(Message)
        .filter_by(whatsapp_message_id=whatsapp_message_id)
        .first()
        is not None
    )


def save_message(session, chat_name: str, sender_name: str, phone: str | None,
                  text: str, message_type: str, is_from_me: bool,
                  whatsapp_message_id: str | None,
                  file_path: str | None = None, original_filename: str | None = None):
    """يحفظ رسالة جديدة فقط لو مش موجودة قبل كده (تحقق بالـ whatsapp_message_id)."""
    if message_exists(session, whatsapp_message_id):
        return None

    chat = get_or_create_chat(session, chat_name)
    sender = get_or_create_contact(session, sender_name, phone, is_me=is_from_me)

    message = Message(
        whatsapp_message_id=whatsapp_message_id,
        chat_id=chat.id,
        sender_id=sender.id,
        text=text,
        message_type=message_type,
        is_from_me=is_from_me,
    )
    session.add(message)
    session.commit()

    if message_type != "text":
        attachment = Attachment(
            message_id=message.id,
            media_type=message_type,
            file_path=file_path,
            original_filename=original_filename,
        )
        session.add(attachment)
        session.commit()

    label = text if text else f"[{message_type}]" + (" ✅" if file_path else " (بدون ملف)")
    logger.info(f"💬 [{chat_name}] {sender_name}: {label}")
    return message
