from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)          # الاسم زي ما ظاهر في واتساب
    phone = Column(String, nullable=True)           # ممكن يكون None لو لسه متعرفش عليه
    is_me = Column(Boolean, default=False)

    messages = relationship("Message", back_populates="sender")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    chat_name = Column(String, nullable=False, unique=True)
    chat_type = Column(String, default="private")   # private / group

    messages = relationship("Message", back_populates="chat")


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        UniqueConstraint("whatsapp_message_id", name="uq_whatsapp_message_id"),
    )

    id = Column(Integer, primary_key=True)
    whatsapp_message_id = Column(String, nullable=True)  # data-id من الـ DOM (لمنع التكرار)

    chat_id = Column(Integer, ForeignKey("chats.id"))
    sender_id = Column(Integer, ForeignKey("contacts.id"))

    text = Column(String, nullable=True)
    message_type = Column(String, default="text")   # text / image / audio / document
    is_from_me = Column(Boolean, default=False)

    timestamp = Column(DateTime, default=datetime.now)

    chat = relationship("Chat", back_populates="messages")
    sender = relationship("Contact", back_populates="messages")
    attachment = relationship("Attachment", back_populates="message", uselist=False)


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("messages.id"))

    media_type = Column(String, nullable=False)   # image / video / voice / audio / document / sticker
    file_path = Column(String, nullable=True)      # المسار المحلي بعد التنزيل (None لو التنزيل فشل)
    original_filename = Column(String, nullable=True)

    message = relationship("Message", back_populates="attachment")
