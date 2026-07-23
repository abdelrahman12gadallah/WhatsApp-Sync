"""
Realtime Exporter: بياخد كل البيانات من قاعدة البيانات ويبني صفحة
whatsapp_live.html — عرض بسيط RTL للشاتات والرسائل، بدون أي اتصال
بالإنترنت أو صور بروفايل، كل حاجة محلية (SQLite + ملفات media/).

بيتنادى بعد كل دورة فيها رسائل جديدة فعليًا (مش كل تيك عشان منضيعش وقت
في إعادة كتابة الملف من غير داعي).
"""

import html
from datetime import datetime

from sqlalchemy.orm import joinedload

from config import DASHBOARD_PATH, MEDIA_DIR, BASE_DIR
from database.models import Chat, Message


def _render_message(msg: Message) -> str:
    sender = html.escape(msg.sender.name if msg.sender else "Unknown")
    time_str = msg.timestamp.strftime("%Y-%m-%d %H:%M")
    bubble_class = "me" if msg.is_from_me else "other"

    if msg.message_type == "image" and msg.attachment and msg.attachment.file_path:
        rel_path = msg.attachment.file_path.replace(str(BASE_DIR) + "/", "").replace(str(BASE_DIR) + "\\", "")
        body = f'<img src="{html.escape(rel_path)}" class="msg-image" loading="lazy">'
        if msg.text:
            body += f'<div class="caption">{html.escape(msg.text)}</div>'
    elif msg.message_type != "text":
        body = f'<div class="media-placeholder">📎 {html.escape(msg.message_type)}</div>'
    else:
        body = html.escape(msg.text or "")

    return f'''
    <div class="bubble {bubble_class}">
        <div class="sender">{sender}</div>
        <div class="body">{body}</div>
        <div class="time">{time_str}</div>
    </div>'''


def generate_dashboard(session):
    chats = (
        session.query(Chat)
        .options(joinedload(Chat.messages).joinedload(Message.sender),
                  joinedload(Chat.messages).joinedload(Message.attachment))
        .all()
    )

    chats_html = []
    for chat in chats:
        messages = sorted(chat.messages, key=lambda m: m.timestamp)
        if not messages:
            continue
        messages_html = "".join(_render_message(m) for m in messages)
        chats_html.append(f'''
        <section class="chat-block">
            <h2>{html.escape(chat.chat_name)}</h2>
            <div class="messages">{messages_html}</div>
        </section>''')

    page = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>WhatsApp Live</title>
<style>
    body {{ font-family: "Segoe UI", Tahoma, sans-serif; background: #e5ddd5; margin: 0; padding: 20px; }}
    
    /* تنسيق الهيدر والزرار */
    .header-container {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
    h1 {{ color: #075e54; margin: 0; }}
    #sound-toggle {{ padding: 8px 16px; border: none; border-radius: 20px; cursor: pointer; font-weight: bold; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.15); transition: 0.3s; font-family: inherit; outline: none; }}
    #sound-toggle.active {{ background: #dcf8c6; color: #075e54; }}
    
    .chat-block {{ background: white; border-radius: 8px; margin-bottom: 24px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.15); }}
    .chat-block h2 {{ margin-top: 0; color: #075e54; border-bottom: 1px solid #eee; padding-bottom: 8px; }}
    .messages {{ display: flex; flex-direction: column; gap: 6px; max-height: 500px; overflow-y: auto; scroll-behavior: smooth; }}
    .bubble {{ max-width: 70%; padding: 8px 12px; border-radius: 8px; font-size: 14px; }}
    .bubble.me {{ background: #dcf8c6; align-self: flex-start; }}
    .bubble.other {{ background: #f1f0f0; align-self: flex-end; }}
    .sender {{ font-weight: bold; font-size: 12px; color: #075e54; margin-bottom: 2px; }}
    .time {{ font-size: 10px; color: #999; margin-top: 4px; text-align: left; }}
    .msg-image {{ max-width: 260px; border-radius: 6px; display: block; }}
    .caption {{ margin-top: 4px; }}
    .media-placeholder {{ color: #666; font-style: italic; }}
    .updated {{ color: #666; font-size: 12px; margin-bottom: 20px; }}
    
    .messages::-webkit-scrollbar {{ width: 6px; }}
    .messages::-webkit-scrollbar-thumb {{ background: #bbb; border-radius: 3px; }}
    .messages::-webkit-scrollbar-thumb:hover {{ background: #888; }}
</style>

<script>
    let isUserScrolling = false;
    let soundEnabled = false;
    let totalMessagesCount = 0;

    // توليد صوت تنبيه برمجياً
    function playNotificationSound(silent = false) {{
        if (!soundEnabled && !silent) return;
        try {{
            let ctx = new (window.AudioContext || window.webkitAudioContext)();
            let osc = ctx.createOscillator();
            let gainNode = ctx.createGain();
            
            osc.type = 'sine';
            osc.frequency.setValueAtTime(silent ? 0 : 750, ctx.currentTime); 
            
            gainNode.gain.setValueAtTime(silent ? 0 : 0.1, ctx.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.15);
            
            osc.connect(gainNode);
            gainNode.connect(ctx.destination);
            
            osc.start();
            osc.stop(ctx.currentTime + 0.15);
        }} catch(e) {{
            console.log("الصوت غير مدعوم");
        }}
    }}

    function toggleSound() {{
        soundEnabled = !soundEnabled;
        let btn = document.getElementById('sound-toggle');
        if (soundEnabled) {{
            btn.innerHTML = '🔔 الصوت مفعل';
            btn.classList.add('active');
            playNotificationSound(true); // فك حظر المتصفح
        }} else {{
            btn.innerHTML = '🔕 تفعيل الصوت';
            btn.classList.remove('active');
        }}
    }}

    function scrollToBottom() {{
        document.querySelectorAll('.messages').forEach(box => {{
            if (!isUserScrolling) {{
                box.scrollTop = box.scrollHeight;
            }}
        }});
    }}

    document.addEventListener('scroll', function(e) {{
        if(e.target.classList && e.target.classList.contains('messages')) {{
            let box = e.target;
            isUserScrolling = (box.scrollHeight - box.scrollTop - box.clientHeight) > 50;
        }}
    }}, true);

    setInterval(() => {{
        fetch(window.location.href, {{ cache: "no-store" }})
        .then(response => response.text())
        .then(html => {{
            let parser = new DOMParser();
            let doc = parser.parseFromString(html, "text/html");
            
            let newContainer = doc.getElementById('chat-container');
            let oldContainer = document.getElementById('chat-container');
            let newUpdated = doc.getElementById('update-time').innerHTML;
            let oldUpdated = document.getElementById('update-time').innerHTML;

            if (newContainer && oldContainer && newUpdated !== oldUpdated) {{
                let newMessagesCount = doc.querySelectorAll('.bubble').length;
                
                oldContainer.innerHTML = newContainer.innerHTML;
                document.getElementById('update-time').innerHTML = newUpdated;
                
                // لو فيه رسالة جديدة فعلية وصلت، شغل الصوت
                if (newMessagesCount > totalMessagesCount) {{
                    playNotificationSound();
                    totalMessagesCount = newMessagesCount;
                }}
                
                scrollToBottom();
            }}
        }})
        .catch(err => console.log('جاري انتظار التحديث...'));
    }}, 2000);

    window.onload = () => {{
        totalMessagesCount = document.querySelectorAll('.bubble').length;
        scrollToBottom();
    }};
</script>

</head>
<body>
<div class="header-container">
    <h1>💬 WhatsApp Live Dashboard</h1>
    <button id="sound-toggle" onclick="toggleSound()">🔕 تفعيل الصوت</button>
</div>
<div class="updated" id="update-time">آخر تحديث: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>

<div id="chat-container">
{"".join(chats_html) if chats_html else "<p style='text-align:center'>لسه مفيش رسائل متسجلة.</p>"}
</div>

</body>
</html>'''

    DASHBOARD_PATH.write_text(page, encoding="utf-8")