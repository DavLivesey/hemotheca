from telegram import Update
from telegram.ext import ContextTypes
from keyboards import *
from elements import *

user_data = {}

async def handle_component(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора компонента"""
    choice = update.message.text
    
    if choice == platelets:
        context.chat_data['component'] = choice
        await update.message.reply_text("Выберите группу крови пациента", reply_markup=blood_group_keyboard)        
    elif choice == plasma:
        context.chat_data['component'] = choice
        await update.message.reply_text("Выберите группу крови пациента", reply_markup=blood_group_keyboard)  
    elif choice in [blood, cryoprecipitate]:
        context.chat_data['component'] = choice
        await update.message.reply_text("Выберите резус-фактор:", reply_markup=rh_keyboard)
    elif choice == "🔙 Назад":
        await update.message.reply_text("Выберите компонент крови:", reply_markup=main_keyboard)

async def handle_blood_group(update:Update, context:ContextTypes.DEFAULT_TYPE):
    blood_group = update.message.text
    component = context.chat_data['component']    
    result_text = f"""
        ✅ Подбор завершен!

        🧬 **Параметры пациента:**
        • Группа крови: {blood_group}
        • Компонент: {component}

        💡 **Рекомендуемые компоненты:**
        • {get_compatible_components(component, blood_group, "")}"""
    
    await update.message.reply_text(
        result_text, 
        reply_markup=main_keyboard,  # Возвращаем основную клавиатуру
        parse_mode='Markdown'
    )

async def handle_rh_factor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора резус-фактора"""
    user_id = update.message.from_user.id
    rh_factor = update.message.text
    
    # Получаем сохраненную группу крови
    blood_group = user_data.get(user_id, {}).get('blood_group', 'не указана')
    
    # Формируем результат
    result_text = f"""
        ✅ Подбор завершен!

        🧬 **Параметры пациента:**
        • Группа крови: {blood_group}
        • Резус-фактор: {rh_factor}

        💡 **Рекомендуемые компоненты:**
        • {get_compatible_components(blood_group, rh_factor)}
    """
    
    await update.message.reply_text(
        result_text, 
        reply_markup=main_keyboard,  # Возвращаем основную клавиатуру
        parse_mode='Markdown'
    )

def get_compatible_components(component: str, blood_group: str, rh_factor: str) -> str:
    """Функция для определения совместимых компонентов крови"""
    # Простая логика для примера
    if component == platelets:
        if blood_group == blood_group_O:
            return """📋 *Варианты тромбоцитов:*
                    
                    • Тромбоциты в плазме донора (из крови)
                      → Совместимость: группа О
                    
                    • Тромбоциты в плазме донора (аферез)  
                      → Совместимость: группы О, AB
                    
                    • Тромбоциты в добавочном растворе
                      → Совместимость: все группы ✅"""
        else:
            return "Неизвестная комбинация компонентов"

async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик неизвестных сообщений"""
    await update.message.reply_text(
        "Пожалуйста, используйте кнопки для навигации 🩺",
        reply_markup=main_keyboard
    )