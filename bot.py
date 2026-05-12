import os
import sqlite3
import google.generativeai as genai

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

# =========================
# CONFIG
# =========================

TOKEN = os.getenv("TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-flash-latest")

# =========================
# DATABASE
# =========================

conn = sqlite3.connect("shop.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    username TEXT,
    product TEXT
)
""")

conn.commit()

# =========================
# MAIN MENU
# =========================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["🛍 Каталог", "🤖 AI Консультант"],
        ["🧴 Подбор ухода", "📦 Мои заказы"],
        ["💬 Поддержка", "📍 О нас"],
        ["🌐 Instagram"]
    ],
    resize_keyboard=True
)

# =========================
# CATALOG
# =========================

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

# =========================
# PRODUCTS
# =========================

face_products = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            "Beauty of Joseon Relief Sun",
            callback_data="buy_sun"
        )
    ],
    [
        InlineKeyboardButton(
            "Round Lab Toner",
            callback_data="buy_toner"
        )
    ]
])

serum_products = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            "Axis-Y Dark Spot Serum",
            callback_data="buy_axis"
        )
    ],
    [
        InlineKeyboardButton(
            "Skin1004 Ampoule",
            callback_data="buy_skin"
        )
    ]
])

# =========================
# START
# =========================

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

# =========================
# TEXT MESSAGES
# =========================

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    # CATALOG

    if text == "🛍 Каталог":

        await update.message.reply_text(
            "Выберите категорию 👇",
            reply_markup=catalog_keyboard
        )

    # AI CONSULTANT

    elif text == "🤖 AI Консультант":

        await update.message.reply_text(
            "Напишите вопрос про уход за кожей ✨"
        )

        context.user_data["ai_mode"] = True

    # SKIN CARE

    elif text == "🧴 Подбор ухода":

        await update.message.reply_text(
            "Напишите тип кожи:\n\n"
            "• Сухая\n"
            "• Жирная\n"
            "• Комбинированная\n"
            "• Чувствительная"
        )

    # ORDERS

    elif text == "📦 Мои заказы":

        user_id = str(update.effective_user.id)

        cursor.execute(
            "SELECT product FROM orders WHERE user_id=?",
            (user_id,)
        )

        orders = cursor.fetchall()

        if not orders:

            await update.message.reply_text(
                "У вас пока нет заказов 📭"
            )

        else:

            text_orders = "📦 Ваши заказы:\n\n"

            for order in orders:
                text_orders += f"• {order[0]}\n"

            await update.message.reply_text(text_orders)

    # SUPPORT

    elif text == "💬 Поддержка":

        await update.message.reply_text(
            "Менеджер:\n@glowrush_support"
        )

    # ABOUT

    elif text == "📍 О нас":

        await update.message.reply_text(
            "GlowRush 🇰🇷\n\n"
            "Оригинальная корейская косметика\n"
            "Доставка по Узбекистану 🚚"
        )

    # INSTAGRAM

    elif text == "🌐 Instagram":

        await update.message.reply_text(
            "https://instagram.com/glowrush.uz"
        )

    # AI CHAT

    elif context.user_data.get("ai_mode"):

        try:

            response = model.generate_content(
                f"""
                Ты консультант магазина корейской косметики.
                Отвечай кратко и полезно.

                Вопрос:
                {text}
                """
            )

            answer = response.text

            if len(answer) > 4000:
                answer = answer[:4000]

            await update.message.reply_text(answer)

        except Exception as e:

            await update.message.reply_text(
                f"Ошибка AI: {e}"
            )

    else:

        await update.message.reply_text(
            "Выберите кнопку 👇"
        )

# =========================
# CALLBACKS
# =========================

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = str(query.from_user.id)

    username = str(query.from_user.username)

    # FACE

    if query.data == "face":

        await query.message.reply_text(
            "✨ Уход за лицом",
            reply_markup=face_products
        )

    # SERUM

    elif query.data == "serum":

        await query.message.reply_text(
            "💧 Сыворотки",
            reply_markup=serum_products
        )

    # CLEAN

    elif query.data == "clean":

        await query.message.reply_text(
            "🫧 Очищение\n\n"
            "• Cleansing Foam\n"
            "• Cleansing Oil\n"
            "• Cleansing Balm"
        )

    # BUY PRODUCTS

    elif query.data == "buy_sun":

        product = "Beauty of Joseon Relief Sun"

        cursor.execute(
            "INSERT INTO orders (user_id, username, product) VALUES (?, ?, ?)",
            (user_id, username, product)
        )

        conn.commit()

        await query.message.reply_text(
            f"✅ Заказ оформлен:\n{product}"
        )

    elif query.data == "buy_toner":

        product = "Round Lab Toner"

        cursor.execute(
            "INSERT INTO orders (user_id, username, product) VALUES (?, ?, ?)",
            (user_id, username, product)
        )

        conn.commit()

        await query.message.reply_text(
            f"✅ Заказ оформлен:\n{product}"
        )

    elif query.data == "buy_axis":

        product = "Axis-Y Dark Spot Serum"

        cursor.execute(
            "INSERT INTO orders (user_id, username, product) VALUES (?, ?, ?)",
            (user_id, username, product)
        )

        conn.commit()

        await query.message.reply_text(
            f"✅ Заказ оформлен:\n{product}"
        )

    elif query.data == "buy_skin":

        product = "Skin1004 Ampoule"

        cursor.execute(
            "INSERT INTO orders (user_id, username, product) VALUES (?, ?, ?)",
            (user_id, username, product)
        )

        conn.commit()

        await query.message.reply_text(
            f"✅ Заказ оформлен:\n{product}"
        )

# =========================
# APP
# =========================

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

print("GlowRush AI business bot started 🚀")

app.run_polling(close_loop=False)
