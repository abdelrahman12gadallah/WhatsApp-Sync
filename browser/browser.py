"""
مسؤول عن:
- فتح WhatsApp Web بمتصفح له Session ثابتة (Persistent Context)
- أول مرة هتظهر QR تعمله Scan بموبايلك
- بعد كده هيدخل تلقائي من غير QR
"""

from playwright.sync_api import sync_playwright, BrowserContext, Page
from loguru import logger

from config import PROFILE_DIR, HEADLESS

WHATSAPP_URL = "https://web.whatsapp.com"


class WhatsAppBrowser:
    def __init__(self):
        self._playwright = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    def start(self) -> Page:
        """يفتح المتصفح ويرجع الـ Page بتاعة واتساب بعد ما يتأكد إن تسجيل الدخول تم."""
        self._playwright = sync_playwright().start()

        PROFILE_DIR.mkdir(parents=True, exist_ok=True)

        self.context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=HEADLESS,
            viewport={"width": 1400, "height": 900},
        )

        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        self.page.goto(WHATSAPP_URL)

        self._wait_for_login()
        return self.page

    def _wait_for_login(self):
        """
        بينتظر لحد ما تظهر قايمة الشاتات (يعني تسجيل الدخول تم، سواء بـ QR
        أول مرة أو تلقائي من الـ Session المحفوظة).
        """
        logger.info("جاري التأكد من تسجيل الدخول... لو ظهر QR اعمله Scan من موبايلك.")

        # الـ selector ده بيتغير من واتساب لواتساب، لو اتغير التصميم
        # هتحتاج تحدثه (افتح Dev Tools على WhatsApp Web وشوف الـ id الحالي)
        self.page.wait_for_selector('[aria-label="Chat list"]', timeout=120_000)
        logger.success("تم تسجيل الدخول بنجاح ✅")

    def stop(self):
        if self.context:
            self.context.close()
        if self._playwright:
            self._playwright.stop()
