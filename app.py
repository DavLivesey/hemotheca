from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
from keyboards import main_keyboard
from handlers import *


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = """
👋 Добро пожаловать в бот для подбора компонентов крови!

Выберите компонент для переливания:
    """
    await update.message.reply_text(welcome_text, reply_markup=main_keyboard)



def main():
    """Основная функция запуска бота"""
    # Замените 'YOUR_BOT_TOKEN' на реальный токен вашего бота
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Text([
        "🟥 Эритроциты", "🟨 Тромбоциты", "🟪 Плазма", "❄️ Криопреципитат"
    ]), handle_component))
    application.add_handler(MessageHandler(filters.Text([
        "➕ Резус-положительный", "➖ Резус-отрицательный"
    ]), handle_rh_factor))
    application.add_handler(MessageHandler(filters.Text([
        "🅰️ Группа крови А","🅱️ Группа крови Б","🆎 Группа крови АБ", "🅾️ Группа крови О"
    ]), handle_blood_group))
    application.add_handler(MessageHandler(filters.ALL, handle_unknown))
    
    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()