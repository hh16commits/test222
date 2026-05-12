import os
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("TOKEN")

# ===== Главное меню =====

main_keyboard = ReplyKeyboardMarkup(
    [
        ["🛍 Каталог", "🧴 Подбор ухода"],
        ["📦 Мои заказы", "💬 Поддержка"],
        ["📍 О нас", "🌐 Instagram"]
    ],
    resize_keyboard=True
)

# ===== Каталог =====

catalog_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            "✨ Уход за лицом",
            callback_data="face"
        )
    ],
    [
        InlineKeyboardButton(
            "💧 Сыворотки",
            callback_data="serum"
        )
    ],
    [
        InlineKeyboardButton(
            "🫧 Очищение",
            callback_data="clean"
        )
    ]
])

# ===== START =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "✨ Добро пожаловать в GlowRush 🇰🇷\n\n"
        "Магазин корейской косметики\n"
        "Выберите раздел 👇"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_keyboard
    )

# ===== ОБРАБОТКА КНОПОК =====

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    # КАТАЛОГ

    if text == "🛍 Каталог":

        await update.message.reply_text(
            "Выберите категорию 👇",
            reply_markup=catalog_keyboard
        )

    # ПОДБОР УХОДА

    elif text == "🧴 Подбор ухода":

        await update.message.reply_text(
            "Напишите ваш тип кожи:\n\n"
            "• Сухая\n"
            "• Жирная\n"
            "• Комбинированная\n"
            "• Чувствительная"
        )

    # ЗАКАЗЫ

    elif text == "📦 Мои заказы":

        await update.message.reply_text(
            "У вас пока нет заказов 📭"
        )

    # ПОДДЕРЖКА

    elif text == "💬 Поддержка":

        await update.message.reply_text(
            "Связь с менеджером:\n"
            "@glowrush_support"
        )

    # О НАС

    elif text == "📍 О нас":

        await update.message.reply_text(
            "GlowRush ✨\n\n"
            "Корейская косметика напрямую 🇰🇷\n"
            "Оригинальная продукция\n"
            "Доставка по Узбекистану 🚚"
        )

    # INSTAGRAM

    elif text == "🌐 Instagram":

        await update.message.reply_text(
            "Instagram:\n"
            "https://instagram.com/glowrush.uz"
        )

    else:

        await update.message.reply_text(
            "Выберите кнопку из меню 👇"
        )

# ===== INLINE КНОПКИ =====

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    # УХОД

    if query.data == "face":

        await query.message.reply_text(
            "✨ Уход за лицом\n\n"
            "• Round Lab\n"
            "• Anua\n"
            "• Beauty of Joseon"
        )

    # СЫВОРОТКИ

    elif query.data == "serum":

        await query.message.reply_text(
            "💧 Сыворотки\n\n"
            "• Axis-Y\n"
            "• Skin1004\n"
            "• COSRX"
        )

    # ОЧИЩЕНИЕ

    elif query.data == "clean":

        await query.message.reply_text(
            "🫧 Очищение\n\n"
            "• Oil Cleanser\n"
            "• Foam Cleanser\n"
            "• Cleansing Balm"
        )

# ===== APP =====

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        messages
    )
)

app.add_handler(
    CallbackQueryHandler(callbacks)
)

print("GlowRush business bot started 🚀")

app.run_polling(close_loop=False)
