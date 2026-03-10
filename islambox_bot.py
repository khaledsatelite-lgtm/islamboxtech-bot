#!/usr/bin/env python3
# ============================================================
#   Islam Box Tech Zeboudja — بوت تيليغرام لإدارة الاشتراكات
# ============================================================
# تثبيت: pip install python-telegram-bot==20.7 apscheduler
# تشغيل: python islambox_bot.py

import json, os, logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ══════════════════════════════════════════════
#  ⚙️  الإعدادات — ضع Token البوت هنا
# ══════════════════════════════════════════════
BOT_TOKEN = " 8644244957:AAGoZiZbwJ7Ozqy2iXvlkDpKsD50XSMwQAI  "    
ADMIN_ID   =    1917928954                  # ← ضع Chat ID الخاص بك هنا (اكتب /start أولاً لمعرفته)
DATA_FILE  = "clients.json"
REMIND_DAYS = 3                      # عدد أيام التذكير قبل الانتهاء

# ══════════════════════════════════════════════
#  💾  تخزين البيانات
# ══════════════════════════════════════════════
def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def dump(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fmt_date(d):
    return datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y")

def days_left(end_date):
    delta = datetime.strptime(end_date, "%Y-%m-%d") - datetime.now()
    return delta.days

# ══════════════════════════════════════════════
#  📩  رسائل واتساب
# ══════════════════════════════════════════════
def wa_msg_reminder(c):
    sub = f" ({c['subName']})" if c.get('subName') else ""
    d = days_left(c['endDate'])
    return (
        f"السلام عليكم {c['name']} 👋\n\n"
        f"تنبيه هام ⚠️\n"
        f"اشتراكك{sub} سينتهي خلال {d} أيام فقط!\n"
        f"📅 تاريخ الانتهاء: {fmt_date(c['endDate'])}\n\n"
        f"جدد الآن ولا تنقطع عن المشاهدة 📺\n"
        f"تواصل معنا 💰\n\n"
        f"— Islam Box Tech Zeboudja"
    )

def wa_msg_credentials(c):
    sub = c.get('subName', 'IPTV')
    msg = (
        f"السلام عليكم {c['name']} 👋\n\n"
        f"✅ تم تفعيل اشتراكك في {sub}\n\n"
        f"🔐 بيانات الدخول:\n"
    )
    if c.get('server'):   msg += f"🌐 السيرفر: {c['server']}\n"
    if c.get('username'): msg += f"👤 اليوزر: {c['username']}\n"
    if c.get('password'): msg += f"🔑 الباسورد: {c['password']}\n"
    msg += (
        f"\n📅 الاشتراك ينتهي: {fmt_date(c['endDate'])}\n\n"
        f"أي مشكلة راسلنا 😊\n"
        f"— Islam Box Tech Zeboudja"
    )
    return msg

def wa_link(phone, msg):
    import urllib.parse
    p = "213" + phone.lstrip("0")
    return f"https://wa.me/{p}?text={urllib.parse.quote(msg)}"

# ══════════════════════════════════════════════
#  🤖  أوامر البوت
# ══════════════════════════════════════════════

# /start
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(
        f"👋 أهلاً بك في Islam Box Tech!\n"
        f"🆔 Chat ID الخاص بك: `{uid}`\n\n"
        f"📋 الأوامر المتاحة:\n"
        f"/add — إضافة زبون جديد\n"
        f"/list — قائمة الزبائن\n"
        f"/check — فحص الاشتراكات المنتهية\n"
        f"/remind — إرسال تذكيرات اليوم\n"
        f"/stats — إحصائيات\n"
        f"/help — المساعدة",
        parse_mode="Markdown"
    )

# /help
async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *طريقة الاستخدام:*\n\n"
        "*إضافة زبون:*\n"
        "`/add الاسم | الهاتف | اسم_الباقة | مدة_بالأشهر | السعر`\n"
        "مثال:\n"
        "`/add أحمد بن علي | 0550123456 | Gold IPTV | 3 | 800`\n\n"
        "*إضافة مع بيانات الدخول:*\n"
        "`/add الاسم | الهاتف | الباقة | المدة | السعر | السيرفر | اليوزر | الباسورد`\n\n"
        "*أوامر أخرى:*\n"
        "/list — عرض كل الزبائن\n"
        "/check — من ينتهي اشتراكه\n"
        "/remind — إرسال تذكيرات\n"
        "/stats — إحصائيات",
        parse_mode="Markdown"
    )

# /add
async def add_client(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/add", "").strip()
    if not text:
        await update.message.reply_text(
            "✏️ *طريقة الإضافة:*\n"
            "`/add الاسم | الهاتف | الباقة | المدة(أشهر) | السعر`\n\n"
            "مثال:\n"
            "`/add أحمد | 0550123456 | Gold | 3 | 800`\n\n"
            "مع بيانات الدخول:\n"
            "`/add أحمد | 0550123456 | Gold | 3 | 800 | http://srv.com | user | pass`",
            parse_mode="Markdown"
        )
        return

    parts = [p.strip() for p in text.split("|")]
    if len(parts) < 4:
        await update.message.reply_text("❌ صيغة خاطئة! استخدم: الاسم | الهاتف | الباقة | المدة")
        return

    name     = parts[0]
    phone    = parts[1]
    sub_name = parts[2] if len(parts) > 2 else ""
    duration = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 1
    price    = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
    server   = parts[5] if len(parts) > 5 else ""
    username = parts[6] if len(parts) > 6 else ""
    password = parts[7] if len(parts) > 7 else ""

    start_date = datetime.now()
    end_date   = start_date + timedelta(days=duration * 30)
    plan_label = f"{duration} شهر" if duration == 1 else (f"سنة" if duration == 12 else f"{duration} أشهر")

    client = {
        "id": int(datetime.now().timestamp() * 1000),
        "name": name, "phone": phone,
        "subName": sub_name, "plan": plan_label,
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "price": price,
        "server": server, "username": username, "password": password
    }

    clients = load()
    clients.insert(0, client)
    dump(clients)

    cred_info = ""
    if server or username:
        cred_info = f"\n🔐 بيانات الدخول محفوظة ✅"

    keyboard = []
    if phone:
        cred_msg = wa_msg_credentials(client)
        keyboard.append([InlineKeyboardButton(
            "📩 إرسال بيانات الدخول واتساب",
            url=wa_link(phone, cred_msg)
        )])

    await update.message.reply_text(
        f"✅ *تم إضافة الزبون بنجاح!*\n\n"
        f"👤 الاسم: {name}\n"
        f"📞 الهاتف: {phone}\n"
        f"🏷️ الباقة: {sub_name or plan_label}\n"
        f"📅 البداية: {fmt_date(client['startDate'])}\n"
        f"📅 النهاية: {fmt_date(client['endDate'])}\n"
        f"💰 السعر: {price} دج{cred_info}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
    )

# /list
async def list_clients(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    clients = load()
    if not clients:
        await update.message.reply_text("📭 لا يوجد زبائن بعد.\nاستخدم /add لإضافة زبون.")
        return

    msg = f"👥 *إجمالي الزبائن: {len(clients)}*\n\n"
    for c in clients[:20]:  # أول 20 فقط
        d = days_left(c['endDate'])
        if d < 0:    status = "❌ منتهي"
        elif d <= 3: status = f"🔴 {d} أيام"
        elif d <= 7: status = f"⚠️ {d} أيام"
        else:        status = f"✅ {d} يوم"
        msg += f"• *{c['name']}* — {c['phone']}\n  {status} | {c.get('subName') or c['plan']}\n\n"

    if len(clients) > 20:
        msg += f"_... و {len(clients)-20} زبون آخر_"

    await update.message.reply_text(msg, parse_mode="Markdown")

# /check
async def check_clients(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    clients = load()
    expiring = [c for c in clients if 0 <= days_left(c['endDate']) <= REMIND_DAYS]
    expired  = [c for c in clients if days_left(c['endDate']) < 0]

    if not expiring and not expired:
        await update.message.reply_text("✅ كل الاشتراكات نشطة! لا يوجد شيء ينتهي قريباً.")
        return

    buttons = []
    msg = ""

    if expiring:
        msg += f"⚠️ *تنتهي خلال {REMIND_DAYS} أيام ({len(expiring)} زبون):*\n\n"
        for c in expiring:
            d = days_left(c['endDate'])
            msg += f"• {c['name']} — {c['phone']} — {d} أيام\n"
            buttons.append([InlineKeyboardButton(
                f"📩 تذكير لـ {c['name']}",
                url=wa_link(c['phone'], wa_msg_reminder(c))
            )])

    if expired:
        msg += f"\n❌ *منتهية ({len(expired)} زبون):*\n\n"
        for c in expired:
            msg += f"• {c['name']} — {c['phone']}\n"

    await update.message.reply_text(
        msg, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
    )

# /remind — إرسال تذكيرات لكل من ينتهي اشتراكه
async def remind_all(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    clients = load()
    expiring = [c for c in clients if 0 <= days_left(c['endDate']) <= REMIND_DAYS]

    if not expiring:
        await update.message.reply_text("✅ لا أحد ينتهي اشتراكه خلال 3 أيام.")
        return

    buttons = [[InlineKeyboardButton(
        f"📩 {c['name']}",
        url=wa_link(c['phone'], wa_msg_reminder(c))
    )] for c in expiring]

    await update.message.reply_text(
        f"📩 *{len(expiring)} تذكير جاهز — اضغط لإرسال كل واحد:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# /stats
async def stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    clients = load()
    active   = sum(1 for c in clients if days_left(c['endDate']) > 7)
    warning  = sum(1 for c in clients if 0 <= days_left(c['endDate']) <= 7)
    expired  = sum(1 for c in clients if days_left(c['endDate']) < 0)
    revenue  = sum(c.get('price', 0) for c in clients)

    await update.message.reply_text(
        f"📊 *إحصائيات Islam Box Tech*\n\n"
        f"👥 إجمالي الزبائن: *{len(clients)}*\n"
        f"✅ اشتراكات نشطة: *{active}*\n"
        f"⚠️ تنتهي قريباً: *{warning}*\n"
        f"❌ منتهية: *{expired}*\n"
        f"💰 إجمالي الإيرادات: *{revenue:,} دج*",
        parse_mode="Markdown"
    )

# ══════════════════════════════════════════════
#  ⏰  التذكير التلقائي اليومي
# ══════════════════════════════════════════════
async def daily_reminder(app):
    clients = load()
    expiring = [c for c in clients if 0 <= days_left(c['endDate']) <= REMIND_DAYS]
    if not expiring or ADMIN_ID == 0:
        return

    buttons = [[InlineKeyboardButton(
        f"📩 {c['name']} ({days_left(c['endDate'])} أيام)",
        url=wa_link(c['phone'], wa_msg_reminder(c))
    )] for c in expiring]

    await app.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔔 *تذكير يومي — {len(expiring)} اشتراك ينتهي قريباً!*\n\nاضغط لإرسال رسالة واتساب لكل زبون:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ══════════════════════════════════════════════
#  🚀  تشغيل البوت
# ══════════════════════════════════════════════
def main():
    logging.basicConfig(level=logging.INFO)

    if BOT_TOKEN == "ضع_TOKEN_هنا":
        print("❌ خطأ: ضع Token البوت في المتغير BOT_TOKEN")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",  start))
    app.add_handler(CommandHandler("help",   help_cmd))
    app.add_handler(CommandHandler("add",    add_client))
    app.add_handler(CommandHandler("list",   list_clients))
    app.add_handler(CommandHandler("check",  check_clients))
    app.add_handler(CommandHandler("remind", remind_all))
    app.add_handler(CommandHandler("stats",  stats))

    # جدولة التذكير اليومي الساعة 9 صباحاً
    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_reminder, "cron", hour=9, minute=0, args=[app])
    scheduler.start()

    print("✅ البوت يعمل الآن!")
    print("افتح تيليغرام وابحث عن بوتك وارسل /start")
    app.run_polling()

if __name__ == "__main__":
    main()
