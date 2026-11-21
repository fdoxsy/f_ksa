 import re
from datetime import datetime, date

def _msg(gender, female_text, male_text):
    """دالة داخلية لتخصيص الخطاب بين البنت والولد"""
    return female_text if str(gender).lower() in list(('f', 'female', 'بنت', 'انثى')) else male_text

def normalize_numbers(text):
    """1. تحويل الأرقام العربية/الهندية (٠١٢٣) إلى إنجليزية (0123)"""
    arabic_nums = "٠١٢٣٤٥٦٧٨٩"
    english_nums = "0123456789"
    return str(text).translate(str.maketrans(arabic_nums, english_nums))

def fix_phone(phone, gender="f"):
    """2. تنظيف وتوحيد رقم الجوال السعودي إلى الصيغة الدولية (9665xxxxxxxx)"""
    digits = re.sub(r'\D', '', normalize_numbers(phone))
    if digits.startswith('9665') and len(digits) == 12:
        return digits
    elif digits.startswith('05') and len(digits) == 10:
        return '966' + digits[1:]
    elif digits.startswith('5') and len(digits) == 9:
        return '966' + digits
    else:
        return _msg(
            gender,
            "❌ الرقم خطا يا مزه، تاكدي انه يبدا بـ 05 ويتكون من 10 ارقام!",
            "❌ الرقم خطا يا مزه، تاكد انه يبدا بـ 05 ويتكون من 10 ارقام!"
        )

def clean_text(text, gender="f"):
    """3. تنظيف النص العربي من التشكيل والرموز وتوحيد الحروف"""
    if not text or str(text).strip() == "":
        return _msg(
            gender,
            "❌ النص فاضي يا مزه، اكتبي شي عشان انظفه لك!",
            "❌ النص فاضي يا مزه، اكتب شي عشان انظفه لك!"
        )
    text = str(text)
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'[^\w\s\u0600-\u06FF]', '', text)
    return " ".join(text.split())

def check_iban(iban, gender="f"):
    """4. التحقق من صيغة الآيبان السعودي ومعرفة اسم البنك تلقائياً"""
    clean_iban = normalize_numbers(iban).replace(" ", "").upper()
    if not clean_iban.startswith("SA") or len(clean_iban) != 24:
        return _msg(
            gender,
            "❌ الايبان خطا يا مزه، تاكدي انه يبدا بـ SA ويتكون من 24 خانه!",
            "❌ الايبان خطا يا مزه، تاكد انه يبدا بـ SA ويتكون من 24 خانه!"
        )
    banks = {
        "80": "مصرف الراجحي", "10": "البنك الأهلي السعودي (SNB)", "20": "بنك الرياض",
        "45": "البنك السعودي البريطاني (ساب)", "55": "البنك السعودي الفرنسي",
        "60": "بنك الجزيرة", "05": "مصرف الإنماء", "15": "بنك البلاد", "30": "البنك العربي الوطني"
    }
    bank_code = clean_iban[4:6]
    bank_name = banks.get(bank_code, "بنك سعودي آخر")
    return f"✅ ايبان صحيح يا مزه - تابع لـ: {bank_name}"

def check_saudi_id(id_number, gender="f"):
    """5. التحقق الرياضي الرسمي من صحة رقم الهوية الوطنية أو الإقامة"""
    id_str = normalize_numbers(id_number).strip()
    if not id_str.isdigit() or len(id_str) != 10 or id_str not in ('1', '2'):
        return _msg(
            gender,
            "❌ الرقم خطا يا مزه، تاكدي انه 10 ارقام ويبدا بـ 1 او 2!",
            "❌ الرقم خطا يا مزه، تاكد انه 10 ارقام ويبدا بـ 1 او 2!"
        )
    total = 0
    for i in range(10):
        digit = int(id_str[i])
        if i % 2 == 0:
            doubled = digit * 2
            total += doubled if doubled < 10 else (doubled // 10) + (doubled % 10)
        else:
            total += digit
    if total % 10 == 0:
        id_type = "هوية وطنية سعودية" if id_str == '1' else "إقامة نظامية"
        return f"✅ رقم صحيح يا مزه ({id_type})"
    else:
        return _msg(
            gender,
            "❌ الرقم خطا يا مزه، تاكدي من رقم الهوية او الاقامه!",
            "❌ الرقم خطا يا مزه، تاكد من رقم الهوية او الاقامه!"
        )

def calc_vat(amount, include_vat=False, gender="f"):
    """6. حساب ضريبة القيمة المضافة السعودية (15%)"""
    try:
        amount = float(normalize_numbers(amount))
        if amount < 0:
            return _msg(gender, "❌ المبلغ خطا يا مزه، تاكدي انه رقم موجب!", "❌ المبلغ خطا يا مزه، تاكد انه رقم موجب!")
        if include_vat:
            base = round(amount / 1.15, 2)
            vat = round(amount - base, 2)
            return {"المبلغ_الأساسي": base, "الضريبة_15%": vat, "الإجمالي_شامل_الضريبة": amount}
        else:
            vat = round(amount * 0.15, 2)
            total = round(amount + vat, 2)
            return {"المبلغ_الأساسي": amount, "الضريبة_15%": vat, "الإجمالي_شامل_الضريبة": total}
    except ValueError:
        return _msg(gender, "❌ المبلغ خطا يا مزه، تاكدي انك كتبتي رقم صحيح!", "❌ المبلغ خطا يا مزه، تاكد انك كتبت رقم صحيح!")

def get_region(city, gender="f"):
    """7. معرفة المنطقة الإدارية في السعودية من اسم المدينة"""
    clean_city = clean_text(city).replace("ال", "")
    regions = {
        "رياض": "منطقة الرياض", "خرج": "منطقة الرياض", "درعيه": "منطقة الرياض", "مجمعه": "منطقة الرياض",
        "مكه": "منطقة مكة المكرمة", "جده": "منطقة مكة المكرمة", "طائف": "منطقة مكة المكرمة", "رابع": "منطقة مكة المكرمة",
        "مدينه": "منطقة المدينة المنورة", "ينبع": "منطقة المدينة المنورة", "علا": "منطقة المدينة المنورة",
        "دمام": "المنطقة الشرقية", "خبر": "المنطقة الشرقية", "ظهران": "المنطقة الشرقية", "احساء": "المنطقة الشرقية", "جبيل": "المنطقة الشرقية", "قطيف": "المنطقة الشرقية",
        "بريده": "منطقة القصيم", "عنيزه": "منطقة القصيم", "رس": "منطقة القصيم",
        "ابها": "منطقة عسير", "خميس مشيط": "منطقة عسير", "بيشه": "منطقة عسير",
        "تبوك": "منطقة تبوك", "نيوم": "منطقة تبوك", "وجه": "منطقة تبوك",
        "حائل": "منطقة حائل", "عرعر": "منطقة الحدود الشمالية", "رفحاء": "منطقة الحدود الشمالية",
        "جازان": "منطقة جازان", "صبياء": "منطقة جازان", "نجران": "منطقة نجران",
        "باحه": "منطقة الباحة", "سكاكا": "منطقة الجوف", "دومه الجندل": "منطقة الجوف"
    }
    for key, region in regions.items():
        if key in clean_city:
            return f"📍 {region}"
    return _msg(gender, "❓ المدينه مو مسجله يا مزه، تاكدي من كتابة اسمها صح!", "❓ المدينه مو مسجله يا مزه، تاكد من كتابة اسمها صح!")

def calc_zakat(amount, gender="f"):
    """8. حساب زكاة المال الشرعية (ربع العشر 2.5%)"""
    try:
        amount = float(normalize_numbers(amount))
        if amount < 0:
            return _msg(gender, "❌ المبلغ خطا يا مزه، تاكدي انه رقم موجب!", "❌ المبلغ خطا يا مزه، تاكد انه رقم موجب!")
        zakat = round(amount * 0.025, 2)
        remaining = round(amount - zakat, 2)
        return {"إجمالي_المبلغ": amount, "مقدار_الزكاة_2.5%": zakat, "المتبقي_بعد_الزكاة": remaining}
    except ValueError:
        return _msg(gender, "❌ المبلغ خطا يا مزه، تاكدي انك كتبتي رقم صحيح!", "❌ المبلغ خطا يا مزه، تاكد انك كتبت رقم صحيح!")

def tafkeet(number, gender="f"):
    """9. تحويل الأرقام إلى كتابة عربية رسمية للفواتير (تفقيط بالريال السعودي)"""
    try:
        num = int(float(normalize_numbers(number)))
        if num < 0 or num > 999999:
            return _msg(gender, "❌ الرقم لازم يكون بين 0 و 999,999 يا مزه!", "❌ الرقم لازم يكون بين 0 و 999,999 يا مزه!")
        if num == 0:
            return "فقط صفر ريال سعودي لا غير"
        ones = ("", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة", "عشرة",
                "أحد عشر", "اثنا عشر", "ثلاثة عشر", "أربعة عشر", "خمسة عشر", "ستة عشر", "سبعة عشر", "ثمانية عشر", "تسعة عشر")
        tens = ("", "", "عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون", "ثمانون", "تسعون")
        hundreds = ("", "مائة", "مائتان", "ثلاثمائة", "أربعمائة", "خمسمائة", "ستمائة", "سبعمائة", "ثمانمائة", "تسعمائة")

        def _convert_under_1000(n):
            parts = list()
            if n >= 100:
                parts.append(hundreds[n // 100])
                n %= 100
            if n > 0:
                if n < 20:
                    parts.append(ones[n])
                else:
                    u = n % 10
                    t = n // 10
                    parts.append(f"{ones[u]} و{tens[t]}" if u > 0 else tens[t])
            return " و".join(parts)

        thousands = num // 1000
        rest = num % 1000
        result_parts = list()
        if thousands > 0:
            if thousands == 1: result_parts.append("ألف")
            elif thousands == 2: result_parts.append("ألفان")
            elif 3 <= thousands <= 10: result_parts.append(f"{ones[thousands]} آلاف")
            else: result_parts.append(f"{_convert_under_1000(thousands)} ألف")
        if rest > 0:
            result_parts.append(_convert_under_1000(rest))
        return f"فقط {' و'.join(result_parts)} ريال سعودي لا غير"
    except ValueError:
        return _msg(gender, "❌ الرقم خطا يا مزه، اكتبي رقم صحيح!", "❌ الرقم خطا يا مزه، اكتب رقم صحيح!")

def extract_data(text):
    """10. استخراج أرقام الجوال السعودية والآيبان من أي نص فوضوي تلقائياً"""
    clean = normalize_numbers(text)
    phones = re.findall(r'(?:\+?9665|05)\d{8}', clean)
    ibans = re.findall(r'SA\d{22}', clean.replace(" ", "").upper())
    return {"أرقام_الجوال": list(set(phones)), "أرقام_الآيبان": list(set(ibans))}

def arabic_date(date_str, gender="f"):
    """11. تحويل التاريخ (YYYY-MM-DD) إلى صيغة عربية كاملة مع اسم اليوم والشهر"""
    try:
        dt = datetime.strptime(normalize_numbers(date_str).strip(), "%Y-%m-%d")
        days = ("الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد")
        months = ("", "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر")
        return f"📅 {days[dt.weekday()]}، {dt.day} {months[dt.month]} {dt.year}"
    except ValueError:
        return _msg(gender, "❌ صيغة التاريخ خطا يا مزه، اكتبيها كذا: 2026-11-21", "❌ صيغة التاريخ خطا يا مزه، اكتبها كذا: 2026-11-21")

def convert_sar(amount, to_currency="USD", reverse=False, gender="f"):
    """12. تحويل العملات من الريال السعودي (SAR) إلى العملات الرئيسية (USD, EUR, AED, KWD, GBP) والعكس"""
    rates = {"USD": 3.75, "EUR": 4.08, "AED": 1.02, "KWD": 12.20, "GBP": 4.78}
    curr = str(to_currency).upper().strip()
    if curr not in rates:
        return _msg(gender, "❌ العمله مو مدعومه يا مزه، اختاري: USD, EUR, AED, KWD, GBP", "❌ العمله مو مدعومه يا مزه، اختر: USD, EUR, AED, KWD, GBP")
    try:
        val = float(normalize_numbers(amount))
        if reverse:
            res = round(val * rates[curr], 2)
            return f"💱 {val} {curr} = {res} ريال سعودي (SAR)"
        else:
            res = round(val / rates[curr], 2)
            return f"💱 {val} ريال سعودي (SAR) = {res} {curr}"
    except ValueError:
        return _msg(gender, "❌ المبلغ خطا يا مزه، اكتبي رقم صحيح!", "❌ المبلغ خطا يا مزه، اكتب رقم صحيح!")

def calc_age(birth_date, gender="f"):
    """13. حساب العمر الدقيق بالسنوات والأشهر والأيام من تاريخ الميلاد (YYYY-MM-DD)"""
    try:
        bdate = datetime.strptime(normalize_numbers(birth_date).strip(), "%Y-%m-%d").date()
        today = date.today()
        if bdate > today:
            return _msg(gender, "❌ تاريخ الميلاد بالمستقبل يا مزه، تاكدي من التاريخ!", "❌ تاريخ الميلاد بالمستقبل يا مزه، تاكد من التاريخ!")
        years = today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
        months = (today.month - bdate.month - (today.day < bdate.day)) % 12
        days = (today - bdate.replace(year=today.year if (today.month, today.day) >= (bdate.month, bdate.day) else today.year - 1)).days % 30
        return {"السنوات": years, "الأشهر": months, "الأيام": days, "الوصف": f"🎂 عمرك {years} سنة و {months} شهر و {days} يوم"}
    except ValueError:
        return _msg(gender, "❌ صيغة التاريخ خطا يا مزه، اكتبيها كذا: 2000-05-15", "❌ صيغة التاريخ خطا يا مزه، اكتبها كذا: 2000-05-15")

def check_password(password, gender="f"):
    """14. فحص قوة كلمة المرور وإعطاء نصائح لتقويتها"""
    pwd = str(password)
    tips = list()
    if len(pwd) < 8:
        tips.append("اجعليها 8 خانات على الأقل" if gender == "f" else "اجعلها 8 خانات على الأقل")
    if not re.search(r'[A-Z]', pwd):
        tips.append("أضيفي حرفاً كبيراً (A-Z)" if gender == "f" else "أضف حرفاً كبيراً (A-Z)")
    if not re.search(r'[0-9]', pwd):
        tips.append("أضيفي أرقاماً (0-9)" if gender == "f" else "أضف أرقاماً (0-9)")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd):
        tips.append("أضيفي رمزاً خاصاً مثل (@#$)" if gender == "f" else "أضف رمزاً خاصاً مثل (@#$)")
    
    if not tips:
        return "🛡️ كلمة مرور قوية وممتازة يا مزه!"
    return f"⚠️ كلمة المرور ضعيفة يا مزه، نصيحتي: {' + '.join(tips)}"

def saudi_holidays():
    """15. عرض المناسبات الوطنية الرسمية في المملكة العربية السعودية"""
    return {
        "يوم التأسيس السعودي": "22 فبراير من كل عام",
        "يوم العلم السعودي": "11 مارس من كل عام",
        "اليوم الوطني السعودي": "23 سبتمبر من كل عام"
    }
