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
# CONFIG
# =========================

TOKEN = os.getenv("TOKEN")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ADMIN_ID = 6081767884

WEBAPP_URL = "https://your-app.up.railway.app"

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    "gemini-flash-latest"
)

# =========================
# DATABASE
# =========================

conn = sqlite3.connect(
    "shop.db",
    check_same_thread=False
)

cursor = conn.cursor()

# ORDERS TABLE

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    username TEXT,
    product TEXT
)
""")

conn.commit()

# PRODUCTS TABLE

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
# CATALOG
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
# PRODUCTS
# =========================

face_products = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            "Relief Sun",
            callback_data="buy_sun"
        ),

        InlineKeyboardButton(
            "Round Lab Toner",
            callback_data="buy_toner"
        )
    ]
])

serum_products = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            "Axis-Y Serum",
            callback_data="buy_axis"
        ),

        InlineKeyboardButton(
            "Skin1004",
            callback_data="buy_skin"
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
# ADMIN PANEL
# =========================

async def admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:

        await update.message.reply_text(
            "У вас нет доступа ❌"
        )

        return

    cursor.execute(
        "SELECT * FROM orders"
    )

    orders = cursor.fetchall()

    if not orders:

        await update.message.reply_text(
            "Заказов пока нет 📭"
        )

        return

    text = "📦 Все заказы:\n\n"

    for order in orders:

        text += (
            f"📦 Order: {order[0]}\n"
            f"👤 <a href='tg://user?id={order[1]}'>"
            f"{order[2]}</a>\n"
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

    except:

        await update.message.reply_text(
            """
Использование:

/addproduct Название | Категория | Цена
"""
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

    products = cursor.fetchall()

    if not products:

        await update.message.reply_text(
            "Товаров нет 📭"
        )

        return

    text = "🛍 Товары:\n\n"

    for product in products:

        text += (
            f"ID: {product[0]}\n"
            f"📦 {product[1]}\n"
            f"📂 {product[2]}\n"
            f"💵 {product[3]}\n\n"
        )

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

    except:

        await update.message.reply_text(
            "Использование:\n/deleteproduct ID"
        )

# =========================
# TEXT MESSAGES
# =========================

async def messages(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text

    if text == "🛍 Каталог":

        await update.message.reply_text(
            "Выберите категорию 👇",
            reply_markup=catalog_keyboard
        )

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

    elif text == "🤖 AI Консультант":

        context.user_data["ai_mode"] = True

        await update.message.reply_text(
            "Напишите вопрос ✨"
        )

    elif text == "🧴 Подбор ухода":

        await update.message.reply_text(
            "Напишите ваш тип кожи ✨"
        )

    elif text == "📦 Мои заказы":

        user_id = str(
            update.effective_user.id
        )

        cursor.execute(
            "SELECT product FROM orders WHERE user_id=?",
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

    elif text == "💬 Поддержка":

        await update.message.reply_text(
            "Менеджер:\n@glowrush_support"
        )

    elif text == "📍 О нас":

        await update.message.reply_text(
            "GlowRush 🇰🇷\n\n"
            "Корейская косметика\n"
            "Доставка по Узбекистану 🚚"
        )

    elif text == "🌐 Instagram":

        await update.message.reply_text(
            "https://instagram.com/glowrush.uz"
        )

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

    elif context.user_data.get(
        "ai_mode"
    ):

        try:

            response = model.generate_content(
                f"""
                Ты консультант магазина
                корейской косметики.

                Отвечай кратко.

                Вопрос:
                {text}
                """
            )

            answer = response.text

            if len(answer) > 4000:
                answer = answer[:4000]

            await update.message.reply_text(
                answer
            )

        except Exception as e:

            await update.message.reply_text(
                f"Ошибка: {e}"
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

    if query.data == "face":

       await query.message.reply_text(
    "✨ Уход за лицом",
    reply_markup=face_products
)
        )

    elif query.data == "serum":

        await query.message.reply_text(
            "💧 Сыворотки",
            reply_markup=serum_products
        )

    elif query.data == "clean":

        await query.message.reply_text(
            "🫧 Cleansing Foam\n"
            "🫧 Cleansing Oil\n"
            "🫧 Cleansing Balm"
        )

    elif query.data == "buy_sun":

        product = (
            "Beauty of Joseon Relief Sun"
        )

        context.user_data[
            "order_product"
        ] = product

        await query.message.reply_text(
            f"""
🛍 Вы выбрали:
{product}

Введите:
• Имя
• Телефон
• Адрес доставки
"""
        )

    elif query.data == "buy_toner":

        product = "Round Lab Toner"

        context.user_data[
            "order_product"
        ] = product

        await query.message.reply_text(
            f"""
🛍 Вы выбрали:
{product}

Введите:
• Имя
• Телефон
• Адрес доставки
"""
        )

    elif query.data == "buy_axis":

        product = (
            "Axis-Y Dark Spot Serum"
        )

        context.user_data[
            "order_product"
        ] = product

        await query.message.reply_text(
            f"""
🛍 Вы выбрали:
{product}

Введите:
• Имя
• Телефон
• Адрес доставки
"""
        )

    elif query.data == "buy_skin":

        product = "Skin1004 Ampoule"

        context.user_data[
            "order_product"
        ] = product

        await query.message.reply_text(
            f"""
🛍 Вы выбрали:
{product}

Введите:
• Имя
• Телефон
• Адрес доставки
"""
        )

# =========================
# APP
# =========================

app = ApplicationBuilder().token(
    TOKEN
).build()

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    CommandHandler("admin", admin)
)

app.add_handler(
    CommandHandler("addproduct", addproduct)
)

app.add_handler(
    CommandHandler("products", products)
)

app.add_handler(
    CommandHandler("deleteproduct", deleteproduct)
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

print(
    "GlowRush AI business bot started 🚀"
)

app.run_polling(close_loop=False)
