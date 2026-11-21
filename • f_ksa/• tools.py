import re

def fix_phone(phone):
    """تنظيف وتوحيد رقم الجوال السعودي إلى الصيغة الدولية (9665xxxxxxxx)"""
    digits = re.sub(r'\D', '', str(phone))
    if digits.startswith('9665') and len(digits) == 12:
        return digits
    elif digits.startswith('05') and len(digits) == 10:
        return '966' + digits[1:]
    elif digits.startswith('5') and len(digits) == 9:
        return '966' + digits
    else:
        return "❌ تنبيه: رقم الجوال غير صحيح، تأكد أن الرقم يبدأ بـ 05 ويتكون من 10 أرقام."

def clean_text(text):
    """تنظيف النص العربي من التشكيل والرموز وتوحيد الحروف بضغطة زر"""
    if not text or str(text).strip() == "":
        return "❌ تنبيه: النص المدخل فارغ."
    text = str(text)
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'[^\w\s\u0600-\u06FF]', '', text)
    return " ".join(text.split())

def check_iban(iban):
    """التحقق من صيغة الآيبان السعودي ومعرفة اسم البنك تلقائياً"""
    clean_iban = str(iban).replace(" ", "").upper()
    if not clean_iban.startswith("SA") or len(clean_iban) != 24:
        return "❌ آيبان غير صحيح: يجب أن يبدأ بـ SA ويتكون من 24 خانة."

    banks = {
        "80": "مصرف الراجحي",
        "10": "البنك الأهلي السعودي (SNB)",
        "20": "بنك الرياض",
        "45": "البنك السعودي البريطاني (ساب)",
        "55": "البنك السعودي الفرنسي",
        "60": "بنك الجزيرة",
        "05": "مصرف الإنماء",
        "15": "بنك البلاد",
        "30": "البنك العربي الوطني"
    }
    bank_code = clean_iban[4:6]
    bank_name = banks.get(bank_code, "بنك سعودي آخر")
    return f"✅ آيبان صحيح - تابع لـ: {bank_name}"

def check_saudi_id(id_number):
    """التحقق الرياضي الرسمي من صحة رقم الهوية الوطنية أو الإقامة"""
    id_str = str(id_number).strip()
    if not id_str.isdigit() or len(id_str) != 10 or id_str[0] not in ['1', '2']:
        return "❌ رقم غير صحيح: يجب أن يتكون من 10 أرقام ويبدأ بـ 1 (هوية) أو 2 (إقامة)."

    total = 0
    for i in range(10):
        digit = int(id_str[i])
        if i % 2 == 0:
            doubled = digit * 2
            total += doubled if doubled < 10 else (doubled // 10) + (doubled % 10)
        else:
            total += digit

    if total % 10 == 0:
        id_type = "هوية وطنية سعودية" if id_str[0] == '1' else "إقامة نظامية"
        return f"✅ رقم صحيح ({id_type})"
    else:
        return "❌ رقم غير صحيح (فشل في التحقق الرقمي)."

def calc_vat(amount, include_vat=False):
    """
    حساب ضريبة القيمة المضافة السعودية (15%)
    - إذا كان المبلغ بدون ضريبة: calc_vat(100)
    - إذا كان المبلغ شاملاً للضريبة وتريد استخراجها: calc_vat(115, include_vat=True)
    """
    try:
        amount = float(amount)
        if amount < 0:
            return "❌ تنبيه: المبلغ يجب أن يكون رقماً موجباً."
        if include_vat:
            base = round(amount / 1.15, 2)
            vat = round(amount - base, 2)
            return {"المبلغ_الأساسي": base, "الضريبة_15%": vat, "الإجمالي_شامل_الضريبة": amount}
        else:
            vat = round(amount * 0.15, 2)
            total = round(amount + vat, 2)
            return {"المبلغ_الأساسي": amount, "الضريبة_15%": vat, "الإجمالي_شامل_الضريبة": total}
    except ValueError:
        return "❌ تنبيه: الرجاء إدخال رقم صحيح للمبلغ."

def get_region(city):
    """معرفة المنطقة الإدارية في السعودية من اسم المدينة (حتى مع اختلاف الكتابة)"""
    clean_city = clean_text(city).replace("ال", "")
    regions = {
        "رياض": "منطقة الرياض", "خرج": "منطقة الرياض", "درعيه": "منطقة الرياض", "مجمعه": "منطقة الرياض",
        "مكه": "منطقة مكة المكرمة", "جده": "منطقة مكة المكرمة", "طائف": "منطقة مكة المكرمة", "رابع": "منطقة مكة المكرمة",
        "مدينه": "منطقة المدينة المنورة", "ينبع": "منطقة المدينة المنورة", "علا": "منطقة المدينة المنورة",
        "دمام": "المنطقة الشرقية", "خبر": "المنطقة الشرقية", "ظهران": "المنطقة الشرقية", "احساء": "المنطقة الشرقية", "جبيل": "المنطقة الشرقية", "قطيف": "المنطقة الشرقية",
        "بريده": "منطقة القصيم", "عنيزه": "منطقة القصيم", "رس": "منطقة القصيم",
        "ابها": "منطقة عسير", "خميس مشيط": "منطقة عسير", "بيشه": "منطقة عسير",
        "تبوك": "منطقة تبوك", "نيوم": "منطقة تبوك", "وجه": "منطقة تبوك",
        "حائل": "منطقة حائل",
        "عرعر": "منطقة الحدود الشمالية", "رفحاء": "منطقة الحدود الشمالية",
        "جازان": "منطقة جازان", "صبياء": "منطقة جازان",
        "نجران": "منطقة نجران",
        "باحه": "منطقة الباحة",
        "سكاكا": "منطقة الجوف", "دومه الجندل": "منطقة الجوف"
    }
    for key, region in regions.items():
        if key in clean_city:
            return f"📍 {region}"
    return "❓ المدينة غير مسجلة في القائمة السريعة، تأكد من كتابة اسم المدينة بشكل صحيح."
