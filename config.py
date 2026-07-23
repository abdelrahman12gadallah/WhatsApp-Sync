"""
إعدادات عامة للمشروع.
"""

from pathlib import Path

BASE_DIR = Path(__file__).parent

# مكان بروفايل الكروم اللي هيحفظ الـ Session (عشان متعملش Scan للـ QR كل مرة)
PROFILE_DIR = BASE_DIR / "profile"

# قاعدة البيانات (SQLite للتجربة، وبعدين تقدر تبدله بـ PostgreSQL URL)
DATABASE_URL = f"sqlite:///{BASE_DIR / 'whatsapp.db'}"

# كل قد ايه (بالثانية) الـ Watcher يفحص الشات المفتوح على أي رسائل جديدة
POLL_INTERVAL_SECONDS = 2

# هل تفتح المتصفح Headless ولا لأ (لازم False أول مرة عشان تعمل Scan للـ QR)
HEADLESS = False

# أقصى عدد شاتات يتم فحصها في كل دورة (عشان الأداء، خليها معقولة الأول)
MAX_CHATS_PER_CYCLE = 15

# كل قد ايه (بالثانية) نعمل دورة كاملة على كل الشاتات
FULL_CYCLE_INTERVAL_SECONDS = 5

# مجلد حفظ الصور الملتقطة من الرسائل (منظم حسب النوع)
MEDIA_DIR = BASE_DIR / "media"

# مجلد ملفات الـ Logs (كل خدمة ليها ملف لوحدها)
LOGS_DIR = BASE_DIR / "logs"

# مسار ملف الـ Dashboard اللي بيتحدث تلقائيًا كل ما توصل رسالة جديدة
DASHBOARD_PATH = BASE_DIR / "whatsapp_live.html"

# بعد كام خطأ متتالي في الدورة الكاملة نوقف البرنامج بدل ما نكرر المحاولة للأبد
MAX_CONSECUTIVE_ERRORS = 5
