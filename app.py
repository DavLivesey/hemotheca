from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
from keyboards import main_keyboard
from handlers import *
from elements import *


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Обработчик команды /start
    welcome_text = """
👋 Добро пожаловать в бот для подбора компонентов крови!

Выберите компонент для переливания:
    """
    await update.message.reply_text(welcome_text, reply_markup=main_keyboard)



def main():
    #Основная функция запуска бота
    application = Application.builder().token(BOT_TOKEN).build()
    
    #Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Text([
        blood, platelets, plasma, cryoprecipitate, granulocytes
    ]), handle_component))
    application.add_handler(MessageHandler(filters.Text([
        rh_D, rh_dd, rh_D_weak, rh_D_partial, rh_D_unknown
    ]), handle_rh_factor_D))
    application.add_handler(MessageHandler(filters.Text([
        rh_CC, rh_Cc, rh_cc, rh_C_unknown
    ]), handle_rh_factor_C))
    application.add_handler(MessageHandler(filters.Text([
        rh_EE, rh_Ee, rh_ee, rh_E_unknown
    ]), handle_rh_factor_E))
    application.add_handler(MessageHandler(filters.Text([
        blood_group_A, blood_group_A2, blood_group_B, blood_group_AB, 
        blood_group_A2B, blood_group_O, blood_group_unknown
    ]), handle_blood_group))
    application.add_handler(MessageHandler(filters.ALL, handle_unknown))
    
    #Запуск бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()