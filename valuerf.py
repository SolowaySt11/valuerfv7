from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
from datetime import datetime

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

# ---------- МЕТАЛЛЫ (ЦБ РФ, руб/грамм) ----------
def get_cbr_metal_price(metal_code):
    """metal_code: 'AU' (золото), 'AG' (серебро), 'PT' (платина), 'PD' (палладий)"""
    today = datetime.now().strftime("%d/%m/%Y")
    url = f"https://cbr.ru/scripts/RML_daily_met_reestr.asp?date={today}&Met={metal_code}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return float(response.text.strip())
        return None
    except:
        return None

# ---------- АКЦИИ (ejtrader, Investing.com) ----------
def get_stock_price(ticker):
    try:
        import ejtrader
        search = ejtrader.search_quotes(text=ticker, products=['stocks'], n_results=1)
        if search:
            recent = search.retrieve_recent_data()
            if recent is not None and not recent.empty:
                return round(recent['Close'].iloc[-1], 2)
        return None
    except Exception as e:
        print(f"Ошибка акций {ticker}: {e}")
        return None

# ---------- ГЛАВНОЕ МЕНЮ ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🪙 Драгоценные металлы (ЦБ)", callback_data="metals")],
        [InlineKeyboardButton("💵 Валюты", callback_data="currencies")],
        [InlineKeyboardButton("📈 Акции (ejtrader)", callback_data="stocks")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🏭 *Инвестиционный дашборд (Тест: ЦБ + акции)*\n\n"
        "Здравствуй! Выбери категорию.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ---------- МЕНЮ МЕТАЛЛОВ ----------
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

# ---------- МЕНЮ АКЦИЙ ----------
async def stocks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("🛢️ Газпром", callback_data="GAZP")],
        [InlineKeyboardButton("🏦 Сбербанк", callback_data="SBER")],
        [InlineKeyboardButton("⛽ Лукойл", callback_data="LKOH")],
        [InlineKeyboardButton("🌐 Яндекс", callback_data="YDEX")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("📈 Выбери акцию:", reply_markup=reply_markup)

# ---------- ОБРАБОТЧИК ----------
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
        await stocks_menu(update, context)
        return

    # Металлы (ЦБ)
    if data == "gold":
        price = get_cbr_metal_price("AU")
        text = f"🥇 Золото: {price} ₽/г" if price else "❌ Не удалось получить цену золота"
        await query.edit_message_text(text)
        return

    if data == "silver":
        price = get_cbr_metal_price("AG")
        text = f"🥈 Серебро: {price} ₽/г" if price else "❌ Не удалось получить цену серебра"
        await query.edit_message_text(text)
        return

    if data == "PLAT":
        price = get_cbr_metal_price("PT")
        text = f"💍 Платина: {price} ₽/г" if price else "❌ Не удалось получить цену платины"
        await query.edit_message_text(text)
        return

    if data == "PLD":
        price = get_cbr_metal_price("PD")
        text = f"🪨 Палладий: {price} ₽/г" if price else "❌ Не удалось получить цену палладия"
        await query.edit_message_text(text)
        return

    # Валюты
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

    # Акции
    if data in ["GAZP", "SBER", "LKOH", "YDEX"]:
        price = get_stock_price(data)
        if price:
            if data == "GAZP":
                name = "🛢️ Газпром"
            elif data == "SBER":
                name = "🏦 Сбербанк"
            elif data == "LKOH":
                name = "⛽ Лукойл"
            else:
                name = "🌐 Яндекс"
            text = f"{name}: {price} ₽"
        else:
            text = f"❌ Не удалось получить цену для {data}"
        await query.edit_message_text(text)
        return

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Используй /start для начала работы.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("Бот запущен (тест ЦБ + акции)...")
    app.run_polling()

if __name__ == "__main__":
    main()