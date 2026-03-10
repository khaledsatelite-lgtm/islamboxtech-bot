# 🤖 Islam Box Tech — إعداد البوت على Render.com (مجاناً)

## الملفات المطلوبة
- islambox_bot.py  ← الكود الرئيسي
- requirements.txt ← المكتبات

## requirements.txt (أنشئ هذا الملف)
```
python-telegram-bot==20.7
apscheduler==3.10.4
```

---

## خطوات الإعداد

### 1️⃣ عدّل الكود
افتح `islambox_bot.py` وعدّل هذين السطرين:
```python
BOT_TOKEN = "ضع_TOKEN_الجديد_هنا"
ADMIN_ID  = 123456789  # Chat ID الخاص بك
```
> لمعرفة Chat ID الخاص بك: شغّل البوت وارسل /start — سيظهر لك الـ ID

---

### 2️⃣ ارفعه على GitHub
1. سجّل في https://github.com
2. أنشئ repository جديد اسمه `islambox-bot`
3. ارفع الملفين: `islambox_bot.py` و `requirements.txt`

---

### 3️⃣ شغّله على Render.com (مجاناً)
1. سجّل في https://render.com
2. اضغط **New → Web Service**
3. اربطه بـ GitHub repository
4. اضبط الإعدادات:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python islambox_bot.py`
5. اضغط **Deploy** ✅

---

## أوامر البوت

| الأمر | الوظيفة |
|-------|---------|
| `/start` | بداية البوت + معرفة Chat ID |
| `/add الاسم \| الهاتف \| الباقة \| المدة \| السعر` | إضافة زبون |
| `/add ... \| السيرفر \| اليوزر \| الباسورد` | إضافة مع بيانات دخول |
| `/list` | قائمة الزبائن |
| `/check` | من ينتهي اشتراكه |
| `/remind` | إرسال تذكيرات واتساب |
| `/stats` | إحصائيات |

---

## مثال إضافة زبون

```
/add أحمد بن علي | 0550123456 | Gold IPTV | 3 | 800
```

مع بيانات دخول:
```
/add أحمد بن علي | 0550123456 | Gold | 3 | 800 | http://srv.com:8080 | user123 | pass456
```

---

## 🔔 التذكير التلقائي
البوت يرسل لك رسالة كل يوم الساعة 9 صباحاً إذا كان هناك زبون ينتهي اشتراكه خلال 3 أيام، مع زر مباشر لفتح واتساب وإرسال التذكير.
