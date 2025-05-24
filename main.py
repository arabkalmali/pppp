import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

# مراحل المحادثة لجمع البيانات
USERNAME, PASSWORD, MID = range(3)

def get_instagram_session(username, password, mid):
    session = requests.Session()
    session.cookies.set("mid", mid)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "X-CSRFToken": "missing",
        "Referer": "https://www.instagram.com/accounts/login/",
    }

    pre_req = session.get("https://www.instagram.com/accounts/login/", headers=headers)
    csrf_token = session.cookies.get_dict().get('csrftoken')
    headers["X-CSRFToken"] = csrf_token

    payload = {
        "username": username,
        "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:&:{password}",
        "queryParams": {},
        "optIntoOneTap": "false"
    }

    login_url = "https://www.instagram.com/accounts/login/ajax/"
    response = session.post(login_url, data=payload, headers=headers)

    if response.status_code == 200 and response.json().get("authenticated"):
        sessionid = session.cookies.get_dict().get("sessionid")
        return True, sessionid
    else:
        return False, response.json()

# وظائف البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا! أدخل اسم المستخدم الخاص بحساب إنستغرام:")
    return USERNAME

async def username_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['username'] = update.message.text
    await update.message.reply_text("أدخل كلمة المرور:")
    return PASSWORD

async def password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['password'] = update.message.text
    await update.message.reply_text("أدخل قيمة MID (إذا لا تعرفها اكتب 'none'):")
    return MID

async def mid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mid = update.message.text
    if mid.lower() == 'none':
        mid = ''
    context.user_data['mid'] = mid

    username = context.user_data['username']
    password = context.user_data['password']

    success, result = get_instagram_session(username, password, mid)

    if success:
        await update.message.reply_text(f"تم تسجيل الدخول بنجاح.\nsessionid: {result}")
    else:
        await update.message.reply_text(f"فشل تسجيل الدخول:\n{result}")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم إلغاء العملية.")
    return ConversationHandler.END

if __name__ == "__main__":
    import asyncio
    TOKEN = "1297860798:AAHtdbjequiGQM9nB1LSRoTFAU0brcgWBwY"
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, username_handler)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, password_handler)],
            MID: [MessageHandler(filters.TEXT & ~filters.COMMAND, mid_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)
    print("البوت يعمل...")
    asyncio.run(app.run_polling())
