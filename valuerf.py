from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests

TOKEN = "8847119724:AAGudqiuhIdAoehPBwTCnJKywUmeoKxb7_E"

# ---------- КУРСЫ ВАЛЮТ ----------
def get_currency_rate(currency_code):
    url = "https://api.exchangerate-api.com/v4/latest/RUB"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        rub_per_currency = 1 / data['rates'][currency_code]
        return round(rub_per_currency, 2)
    except:
        return None

# ---------- ЦЕНЫ МЕТАЛЛОВ (GoldAPI, унции) ----------
def get_metal_price(metal_name):
    """metal_name: 'XAU' (золото), 'XAG' (серебро), 'XPT' (платина), 'XPD' (палладий)"""
    url = f"https://api.gold-api.com/price/{metal_name}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            price_usd = data['price']
            usd_rate = get_currency_rate("USD")
            if usd_rate:
                return round(price_usd * usd_rate, 2)  # цена в рублях за унцию
        return None
    except:
        return None

# ---------- ГЛАВНОЕ МЕНЮ ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🪙 Драгоценные металлы", callback_data="metals")],
        [InlineKeyboardButton("💵 Валюты", callback_data="currencies")],
        [InlineKeyboardButton("📈 Акции", callback_data="stocks")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🏭 *Инвестиционный дашборд*\n\n"
        "Здравствуй! Выбери категорию:\n"
        "⚠️ *Примечание:* Акции временно недоступны. Ведутся технические работы.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ---------- МЕНЮ ДРАГМЕТАЛЛОВ ----------
async def metals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("🥇 Золото", callback_data="gold")],
        [InlineKeyboardButton("🥈 Серебро", callback_data="silver")],
        [InlineKeyboardButton("💍 Платина", callback_data="PLAT")],
        [InlineKeyboardButton("🪨 Палладий", callback_data="PLD")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🪙 Выбери драгоценный металл:", reply_markup=reply_markup)

# ---------- МЕНЮ ВАЛЮТ ----------
async def currencies_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("🇺🇸 Доллар", callback_data="USD")],
        [InlineKeyboardButton("🇪🇺 Евро", callback_data="EUR")],
        [InlineKeyboardButton("🇨🇳 Юань", callback_data="CNY")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("💵 Выбери валюту:", reply_markup=reply_markup)

# ---------- ОБРАБОТЧИК КНОПОК ----------
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main_menu":
        await start(update, context)
        return

    if data == "metals":
        await metals_menu(update, context)
        return

    if data == "currencies":
        await currencies_menu(update, context)
        return

    if data == "stocks":
        await query.edit_message_text("📈 Раздел с акциями временно недоступен. Ведутся технические работы.")
        return

    # ========== МЕТАЛЛЫ (GoldAPI, унции) ==========
    if data == "gold":
        price = get_metal_price("XAU")
        text = f"🥇 Золото: {price} ₽/унция" if price else "❌ Не удалось получить цену золота"
        await query.edit_message_text(text)
        return

    if data == "silver":
        price = get_metal_price("XAG")
        text = f"🥈 Серебро: {price} ₽/унция" if price else "❌ Не удалось получить цену серебра"
        await query.edit_message_text(text)
        return

    if data == "PLAT":
        price = get_metal_price("XPT")
        text = f"💍 Платина: {price} ₽/унция" if price else "❌ Не удалось получить цену платины"
        await query.edit_message_text(text)
        return

    if data == "PLD":
        price = get_metal_price("XPD")
        text = f"🪨 Палладий: {price} ₽/унция" if price else "❌ Не удалось получить цену палладия"
        await query.edit_message_text(text)
        return

    # ========== ВАЛЮТЫ ==========
    if data in ["USD", "EUR", "CNY"]:
        rate = get_currency_rate(data)
        if rate:
            if data == "USD":
                text = f"🇺🇸 Доллар США: {rate} ₽"
            elif data == "EUR":
                text = f"🇪🇺 Евро: {rate} ₽"
            else:
                text = f"🇨🇳 Китайский юань: {rate} ₽"
        else:
            text = "❌ Не удалось получить курс"
        await query.edit_message_text(text)
        return

# ---------- HELP ----------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Используй /start для начала работы.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("Бот SolowayValue запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()