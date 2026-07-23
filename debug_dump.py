"""
سكريبت تشخيصي فقط — مش جزء من التشغيل العادي.

بيفتح نفس الجلسة (اللي عملت فيها Scan قبل كده)، وبعد ما يتأكد إن الصفحة
اتحملت، بيحفظ الـ HTML بتاع منطقة قائمة الشاتات في ملف
`chat_list_debug.html`، وبيطبع كام عنصر لاقى بمحاولات مختلفة.

التشغيل:
    python debug_dump.py

بعد كده افتح chat_list_debug.html وابعتلي أول 100-150 سطر منه
(أو الجزء اللي فيه اسم شات أو اتنين)، عشان أظبط الـ selectors بالظبط
على الشكل الحالي عندك.
"""

from playwright.sync_api import sync_playwright
from config import PROFILE_DIR

WHATSAPP_URL = "https://web.whatsapp.com"


def main():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1400, "height": 900},
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(WHATSAPP_URL)

        print("جاري انتظار تحميل الصفحة (10 ثواني)...")
        page.wait_for_timeout(10_000)

        # نجرب نلاقي الحاوية اللي فيها قائمة الشاتات بأكتر من طريقة
        candidates = {
            'div[aria-label="Chat list"]': page.query_selector('div[aria-label="Chat list"]'),
            '[aria-label="Chat list"]': page.query_selector('[aria-label="Chat list"]'),
            '#pane-side': page.query_selector('#pane-side'),
            'div[role="grid"]': page.query_selector('div[role="grid"]'),
        }

        print("\n--- نتيجة البحث عن حاوية قائمة الشاتات ---")
        found_container = None
        for selector, el in candidates.items():
            exists = el is not None
            print(f"{selector}: {'✅ موجود' if exists else '❌ مش موجود'}")
            if exists and not found_container:
                found_container = el

        if found_container:
            html = found_container.inner_html()
            with open("chat_list_debug.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"\nتم حفظ HTML الحاوية ({len(html)} حرف) في chat_list_debug.html")

            # نجرب كذا selector شائع لصفوف الشاتات ونعد العناصر
            row_candidates = [
                'div[role="listitem"]',
                'div[role="row"]',
                '[data-testid="cell-frame-container"]',
                'span[title]',
            ]
            print("\n--- عدد العناصر لكل selector محتمل لصفوف الشاتات ---")
            for sel in row_candidates:
                count = len(found_container.query_selector_all(sel))
                print(f"{sel}: {count} عنصر")
        else:
            print("\n⚠️ مقدرتش ألاقي أي حاوية لقائمة الشاتات. هل الصفحة متسجل دخول فيها فعلاً؟")
            # نحفظ الـ body كله كحل أخير للمراجعة
            with open("full_page_debug.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("تم حفظ الصفحة كاملة في full_page_debug.html كبديل.")

        print("\nالمتصفح هيفضل مفتوح 30 ثانية كمان عشان تقدر تتأكد بنفسك من الـ Dev Tools لو حابب.")
        page.wait_for_timeout(30_000)
        context.close()


if __name__ == "__main__":
    main()
