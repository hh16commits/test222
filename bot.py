import os
from telegram import (
    Update,
    ReplyKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("TOKEN")


keyboard = [
    ["🛍 Каталог", "📦 Заказать"],
    ["💬 Поддержка", "📍 О нас"]
]

reply_markup = ReplyKeyboardMarkup(
    keyboard,
    resize_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "✨ Добро пожаловать в GlowRush!\n\n"
        "Корейская косметика 🇰🇷"
    )

    await update.message.reply_text(
        text,
        reply_markup=reply_markup
    )


async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🛍 Каталог":
        await update.message.reply_text(
            "Каталог скоро будет доступен 🔥"
        )

    elif text == "📦 Заказать":
        await update.message.reply_text(
            "Напишите название товара ✍️"
        )

    elif text == "💬 Поддержка":
        await update.message.reply_text(
            "Поддержка: @your_username"
        )

    elif text == "📍 О нас":
        await update.message.reply_text(
            "GlowRush — магазин корейской косметики 🇰🇷"
        )

    else:
        await update.message.reply_text(
            "Выберите кнопку 👇"
        )


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        messages
    )
)

print("Business bot started 🚀")

app.run_polling(close_loop=False)
