from flask import Flask
from threading import Thread

import os
import sqlite3
import google.generativeai as genai

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo
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
# FLASK WEB SERVER
# =========================

app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "GlowRush Bot is running 🚀"

def run_web():
    app_web.run(
        host="0.0.0.0",
        port=8080
    )

# =========================
# CONFIG
# =========================

TOKEN = os.getenv("TOKEN")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ADMIN_ID = 6081767884

# USER ID ДЛЯ БЛОКИРОВКИ
BLOCKED_USER_ID = 1145800624

# MINI APP URL
WEBAPP_URL = "https://test222-production.up.railway.app"

# =========================
# GEMINI AI
# =========================

genai.configure(
    api_key=GEMINI_API_KEY
)

model = genai.GenerativeModel(
    "gemini-2.0-flash"
)

# =========================
# DATABASE
# =========================

conn = sqlite3.connect(
    "shop.db",
    check_same_thread=False,
    timeout=10
)

cursor = conn.cursor()

# =========================
# ORDERS TABLE
# =========================

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
# PRODUCTS TABLE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    price TEXT
)
""")

conn.commit()

# =========================
# DEFAULT PRODUCTS
# =========================

cursor.execute(
    "SELECT * FROM products"
)

existing_products = cursor.fetchall()

if not existing_products:

    products_data = [

        (
            "Beauty of Joseon Relief Sun",
            "face",
            "18$"
        ),

        (
            "Round Lab Toner",
            "face",
            "20$"
        ),

        (
            "Axis-Y Dark Spot Serum",
            "serum",
            "15$"
        ),

        (
            "Skin1004 Ampoule",
            "serum",
            "17$"
        )

    ]

    cursor.executemany(
        """
        INSERT INTO products
        (name, category, price)
        VALUES (?, ?, ?)
        """,
        products_data
    )

    conn.commit()

# =========================
# MAIN MENU
# =========================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["🛍 Каталог", "🤖 AI Консультант"],
        ["🧴 Подбор ухода", "📦 Мои заказы"],
        ["💬 Поддержка", "📍 О нас"],
        ["🌐 Instagram", "🛍 Mini App"]
    ],
    resize_keyboard=True
)

# =========================
# CATALOG MENU
# =========================

catalog_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            "✨ Уход за лицом",
            callback_data="face"
        ),

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
# START
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id == BLOCKED_USER_ID:

        await update.message.reply_text(
            "404 - Джалля именно сан ишлатомиса нахуй😂"
        )

        return

    await update.message.reply_text(
        (
            "✨ Добро пожаловать в GlowRush 🇰🇷\n\n"
            "Магазин корейской косметики\n"
            "Выберите раздел 👇"
        ),
        reply_markup=main_keyboard
    )

# =========================
# ADMIN PANEL
# =========================

async def admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:

        await update.message.reply_text(
            "Нет доступа ❌"
        )

        return

    cursor.execute(
        "SELECT * FROM orders"
    )

    orders = cursor.fetchall()

    if not orders:

        await update.message.reply_text(
            "Заказов нет 📭"
        )

        return

    text = "📦 Все заказы:\n\n"

    for order in orders:

        text += (
            f"📦 Order: {order[0]}\n"
            f"👤 "
            f"<a href='tg://user?id={order[1]}'>"
            f"{order[2]}"
            f"</a>\n"
            f"🛍 {order[3]}\n\n"
        )

    if len(text) > 4000:
        text = text[:4000]

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

# =========================
# ADD PRODUCT
# =========================

async def addproduct(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    try:

        data = " ".join(context.args)

        split_data = data.split("|")

        name = split_data[0].strip()
        category = split_data[1].strip()
        price = split_data[2].strip()

        cursor.execute(
            """
            INSERT INTO products
            (name, category, price)
            VALUES (?, ?, ?)
            """,
            (name, category, price)
        )

        conn.commit()

        await update.message.reply_text(
            "✅ Товар добавлен!"
        )

    except Exception as e:

        await update.message.reply_text(
            f"Ошибка: {e}"
        )

# =========================
# PRODUCTS ADMIN
# =========================

async def products(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute(
        "SELECT * FROM products"
    )

    products_data = cursor.fetchall()

    if not products_data:

        await update.message.reply_text(
            "Товаров нет 📭"
        )

        return

    text = "🛍 Товары:\n\n"

    for product in products_data:

        text += (
            f"ID: {product[0]}\n"
            f"📦 {product[1]}\n"
            f"📂 {product[2]}\n"
            f"💵 {product[3]}\n\n"
        )

    if len(text) > 4000:
        text = text[:4000]

    await update.message.reply_text(text)

# =========================
# DELETE PRODUCT
# =========================

async def deleteproduct(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    try:

        product_id = context.args[0]

        cursor.execute(
            "DELETE FROM products WHERE id=?",
            (product_id,)
        )

        conn.commit()

        await update.message.reply_text(
            "🗑 Товар удалён!"
        )

    except Exception as e:

        await update.message.reply_text(
            f"Ошибка: {e}"
        )

# =========================
# SHOW PRODUCTS
# =========================

async def show_products(
    query,
    category
):

    cursor.execute(
        """
        SELECT * FROM products
        WHERE category=?
        """,
        (category,)
    )

    products_data = cursor.fetchall()

    if not products_data:

        await query.message.reply_text(
            "Товаров нет 📭"
        )

        return

    keyboard = []

    row = []

    for product in products_data:

        button = InlineKeyboardButton(
            text=f"{product[1]} • {product[3]}",
            callback_data=f"buy_{product[0]}"
        )

        row.append(button)

        if len(row) == 2:

            keyboard.append(row)

            row = []

    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(
        keyboard
    )

    await query.message.reply_text(
        "🛍 Выберите товар",
        reply_markup=reply_markup
    )

# =========================
# TEXT MESSAGES
# =========================

async def messages(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id == BLOCKED_USER_ID:

        await update.message.reply_text(
            "🚧 Бот временно не работает"
        )

        return

    text = update.message.text

    # CATALOG

    if text == "🛍 Каталог":

        await update.message.reply_text(
            "Выберите категорию 👇",
            reply_markup=catalog_keyboard
        )

    # MINI APP

    elif text == "🛍 Mini App":

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text="🚀 Открыть магазин",
                    web_app=WebAppInfo(
                        url=WEBAPP_URL
                    )
                )
            ]
        ])

        await update.message.reply_text(
            "GlowRush Mini App 🇰🇷",
            reply_markup=keyboard
        )

    # AI

    elif text == "🤖 AI Консультант":

        context.user_data["ai_mode"] = True

        await update.message.reply_text(
            "Напишите вопрос ✨"
        )

    # SKINCARE

    elif text == "🧴 Подбор ухода":

        await update.message.reply_text(
            (
                "Напишите тип кожи:\n\n"
                "• Сухая\n"
                "• Жирная\n"
                "• Комбинированная\n"
                "• Чувствительная"
            )
        )

    # MY ORDERS

    elif text == "📦 Мои заказы":

        user_id = str(
            update.effective_user.id
        )

        cursor.execute(
            """
            SELECT product
            FROM orders
            WHERE user_id=?
            """,
            (user_id,)
        )

        orders = cursor.fetchall()

        if not orders:

            await update.message.reply_text(
                "У вас нет заказов 📭"
            )

        else:

            orders_text = (
                "📦 Ваши заказы:\n\n"
            )

            for order in orders:

                orders_text += (
                    f"• {order[0]}\n"
                )

            await update.message.reply_text(
                orders_text
            )

    # SUPPORT

    elif text == "💬 Поддержка":

        await update.message.reply_text(
            "Менеджер:\n@glowrush_support"
        )

    # ABOUT

    elif text == "📍 О нас":

        await update.message.reply_text(
            (
                "GlowRush 🇰🇷\n\n"
                "Оригинальная корейская косметика\n"
                "Доставка по Узбекистану 🚚"
            )
        )

    # INSTAGRAM

    elif text == "🌐 Instagram":

        await update.message.reply_text(
            "https://instagram.com/glowrush.uz"
        )

    # ORDER

    elif context.user_data.get(
        "order_product"
    ):

        product = context.user_data[
            "order_product"
        ]

        order_info = text

        if update.effective_user.username:

            username = (
                "@"
                + update.effective_user.username
            )

        else:

            username = (
                update.effective_user.first_name
            )

        cursor.execute(
            """
            INSERT INTO orders
            (user_id, username, product)
            VALUES (?, ?, ?)
            """,
            (
                str(update.effective_user.id),
                username,
                f"{product} | {order_info}"
            )
        )

        conn.commit()

        context.user_data[
            "order_product"
        ] = None

        await update.message.reply_text(
            "✅ Заказ отправлен!"
        )

    # AI CHAT

    elif context.user_data.get(
        "ai_mode"
    ):

        try:

            response = model.generate_content(
                f"""
                Ты консультант магазина
                корейской косметики.

                Отвечай кратко и полезно.

                Вопрос:
                {text}
                """
            )

            answer = response.text

            if len(answer) > 4000:
                answer = answer[:4000]

            context.user_data["ai_mode"] = False

            await update.message.reply_text(
                answer
            )

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

async def callbacks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if query.from_user.id == BLOCKED_USER_ID:

        await query.message.reply_text(
            "404 - Джалля именно сан ишлатомиса нахуй😂"
        )

        return

    # FACE

    if query.data == "face":

        await show_products(
            query,
            "face"
        )

    # SERUM

    elif query.data == "serum":

        await show_products(
            query,
            "serum"
        )

    # CLEAN

    elif query.data == "clean":

        await query.message.reply_text(
            (
                "🫧 Cleansing Foam\n"
                "🫧 Cleansing Oil\n"
                "🫧 Cleansing Balm"
            )
        )

    # BUY PRODUCT

    elif query.data.startswith("buy_"):

        product_id = (
            query.data.replace(
                "buy_",
                ""
            )
        )

        cursor.execute(
            """
            SELECT * FROM products
            WHERE id=?
            """,
            (product_id,)
        )

        product = cursor.fetchone()

        if not product:

            await query.message.reply_text(
                "Товар не найден ❌"
            )

            return

        product_name = product[1]

        context.user_data[
            "order_product"
        ] = product_name

        await query.message.reply_text(
            f"""
🛍 Вы выбрали:
{product_name}

Введите:
• Имя
• Телефон
• Адрес доставки
"""
        )

# =========================
# TELEGRAM BOT
# =========================

app = ApplicationBuilder().token(
    TOKEN
).build()

# COMMANDS

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    CommandHandler("admin", admin)
)

app.add_handler(
    CommandHandler(
        "addproduct",
        addproduct
    )
)

app.add_handler(
    CommandHandler(
        "products",
        products
    )
)

app.add_handler(
    CommandHandler(
        "deleteproduct",
        deleteproduct
    )
)

# TEXT

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        messages
    )
)

# CALLBACKS

app.add_handler(
    CallbackQueryHandler(callbacks)
)

print(
    "GlowRush AI business bot started 🚀"
)

# START WEB SERVER

Thread(target=run_web).start()

# START BOT

app.run_polling(
    close_loop=False
    )
