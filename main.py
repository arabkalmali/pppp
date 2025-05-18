import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "1297860798:AAHtdbjequiGQM9nB1LSRoTFAU0brcgWBwY"

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
        return f"✅ sessionid: {sessionid}"
    else:
        return f"❌ فشل تسجيل الدخول:\n{response.json()}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if ":" not in text or text.count(":") < 2:
        await update.message.reply_text("يرجى إرسال البيانات بهذا الشكل:\nusername:password:mid")
        return

    username, password, mid = text.strip().split(":", 2)
    result = get_instagram_session(username, password, mid)
    await update.message.reply_text(result)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("البوت يعمل الآن...")
    app.run_polling()