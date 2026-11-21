import re
from datetime import datetime

def _msg(gender, female_text, male_text):
    """دالة داخلية لتخصيص الخطاب بين البنت والولد"""
    return female_text if str(gender).lower() in ['f', 'female', 'بنت', 'انثى'] else male_text

def normalize_numbers(text):
    """تحويل الأرقام العربية/الهندية (٠١٢٣) إلى إنجليزية (0123)"""
    arabic_nums = "٠١٢٣٤٥٦٧٨٩"
    english_nums = "0123456789"
    trans_table = str.maketrans(arabic_nums, english_nums)
    return str(text).translate(trans_table)

def fix_phone(phone, gender="f"):
    """تنظيف وتوحيد رقم الجوال السعودي إلى الصيغة الدولية"""
    phone = normalize_numbers(phone)
    digits = re.sub(r'\D', '', str(phone))
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
    """تنظيف النص العربي من التشكيل والرموز وتوحيد الحروف"""
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
    """التحقق من صيغة الآيبان السعودي ومعرفة اسم البنك تلقائياً"""
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
    """التحقق الرياضي الرسمي من صحة رقم الهوية الوطنية أو الإقامة"""
    id_str = normalize_numbers(id_number).strip()
    if not id_str.isdigit() or len(id_str) != 10 or id_str not in ['1', '2']:
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
    """حساب ضريبة القيمة المضافة السعودية (15%)"""
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
    """معرفة المنطقة الإدارية في السعودية من اسم المدينة"""
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
    """حساب زكاة المال الشرعية (ربع العشر 2.5%)"""
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
    """تحويل الأرقام إلى كتابة عربية رسمية للفواتير (تفقيط بالريال السعودي)"""
    try:
        num = int(float(normalize_numbers(number)))
        if num < 0 or num > 999999:
            return _msg(gender, "❌ الرقم لازم يكون بين 0 و 999,999 يا مزه!", "❌ الرقم لازم يكون بين 0 و 999,999 يا مزه!")
        if num == 0:
            return "فقط صفر ريال سعودي لا غير"
        ones = ["", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة", "عشرة",
                "أحد عشر", "اثنا عشر", "ثلاثة عشر", "أربعة عشر", "خمسة عشر", "ستة عشر", "سبعة عشر", "ثمانية عشر", "تسعة عشر"]
        tens = ["", "", "عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون", "ثمانون", "تسعون"]
        hundreds = ["", "مائة", "مائتان", "ثلاثمائة", "أربعمائة", "خمسمائة", "ستمائة", "سبعمائة", "ثمانمائة", "تسعمائة"]

        def _convert_under_1000(n):
            parts = []
            if n >= 100:
                parts.append(hundreds[n // 100])
                n %= 100
            if n > 0:
                if n < 20:
                    parts.append(ones[n])
                else:
                    u = n % 10
                    t = n // 10
                    if u > 0:
                        parts.append(f"{ones[u]} و{tens[t]}")
                    else:
                        parts.append(tens[t])
            return " و".join(parts)

        thousands = num // 1000
        rest = num % 1000
        result_parts = []
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
    """استخراج أرقام الجوال السعودية والآيبان من أي نص فوضوي تلقائياً"""
    clean = normalize_numbers(text)
    phones = re.findall(r'(?:\+?9665|05)\d{8}', clean)
    ibans = re.findall(r'SA\d{22}', clean.replace(" ", "").upper())
    return {"أرقام_الجوال": list(set(phones)), "أرقام_الآيبان": list(set(ibans))}

def arabic_date(date_str, gender="f"):
    """تحويل التاريخ (YYYY-MM-DD) إلى صيغة عربية كاملة مع اسم اليوم والشهر"""
    try:
        dt = datetime.strptime(normalize_numbers(date_str).strip(), "%Y-%m-%d")
        days = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
        months = ["", "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
        return f"📅 {days[dt.weekday()]}، {dt.day} {months[dt.month]} {dt.year}"
    except ValueError:
        return _msg(gender, "❌ صيغة التاريخ خطا يا مزه، اكتبيها كذا: 2026-11-21", "❌ صيغة التاريخ خطا يا مزه، اكتبها كذا: 2026-11-21")
