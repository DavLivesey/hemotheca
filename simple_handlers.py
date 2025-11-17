from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from keyboards import *
from elements import *


def get_rh_combinations_from_values(patient_values):
    #Возвращает все возможные комбинации резус-фактора 
    #для генотипа, заданного значениями
    rh_dict = {
        rh_D: [" D", "dd"], 
        rh_dd: ["dd"], 
        rh_D_unknown: ["dd"], 
        rh_D_weak: [" D", "dd"], 
        rh_D_partial: ["dd"],
        
        rh_C_unknown: ["CC"], 
        rh_CC: ["CC"], 
        rh_Cc: ["CC", "Cc", "cc"], 
        rh_cc: ["cc"],
        
        rh_E_unknown: ["ee"], 
        rh_EE: ["EE", "Ee"], 
        rh_Ee: ["EE", "Ee", "ee"], 
        rh_ee: ["ee"]
    }

    options_lists = []
    for val in patient_values:
        if val in rh_dict:
            options = rh_dict[val]
            if not isinstance(options, list):
                options = [options]
            options_lists.append(options)
    combinations = [""]
    for options in options_lists:
        new_combinations = []
        for combo in combinations:
            for option in options:
                new_combinations.append(combo + option)
        combinations = new_combinations
    return combinations

async def handle_regular_patient_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Обработчик для обычных пациентов (без ТКМ)
    context.chat_data['patient_type'] = 'regular'
    context.chat_data['status'] = update.message.text
    await update.message.reply_text("Выберите компонент крови:", reply_markup=components_keyboard)

async def handle_component(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Обработчик выбора компонента
    choice = update.message.text    
    if choice == back:
        await update.message.reply_text("Выберите компонент крови:", reply_markup=BMT_choice_keyboard)
    else:
        context.chat_data['component'] = choice
        await update.message.reply_text("Выберите группу крови пациента", reply_markup=blood_group_keyboard)

async def handle_blood_group(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.chat_data['blood_group']  = update.message.text
    component = context.chat_data['component']    
    if component == blood:
        await update.message.reply_text(
        f"Вы выбрали {context.chat_data['blood_group']}, теперь выберите резус-фактор пациента", 
        reply_markup=rh_keyboard_D, 
        parse_mode="Markdown"
    )
    else:
        result_text = f"✅ Подбор завершен!\n\n"\
              f"• Компонент: {component}\n\n"\
              "**Параметры пациента:**\n"\
              f"• Группа крови: {context.chat_data['blood_group'] }\n"\
              f"• {get_compatible_components(component, context.chat_data['blood_group'] , '')}"

        await update.message.reply_text(
            result_text, 
            reply_markup=BMT_choice_keyboard, 
            parse_mode="Markdown"
        )

async def handle_rh_factor_D(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data['rh_factor_D'] = update.message.text
    await update.message.reply_text(   
        "Выберите С-часть резус-фактора",      
        reply_markup=rh_keyboard_C,
        parse_mode="Markdown"
    )

async def handle_rh_factor_C(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data['rh_factor_C'] = update.message.text
    await update.message.reply_text(
        "Выберите E-часть резус-фактора",           
        reply_markup=rh_keyboard_E, 
        parse_mode="Markdown"
    )

async def handle_rh_factor_E(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Обработчик выбора резус-фактора
    rh_factor_E = update.message.text
    component = context.chat_data['component']
    blood_group = context.chat_data['blood_group']
    rh_factor_common = [context.chat_data['rh_factor_D'], context.chat_data['rh_factor_C'], rh_factor_E]
    
    # Формируем результат
    result_text = "✅ Подбор завершен!\n\n"\
        "**Параметры пациента:**\n"\
        f"• Группа крови: {blood_group}\n"\
        f"• Резус-фактор: {context.chat_data['rh_factor_D']}{context.chat_data['rh_factor_C']}{rh_factor_E}\n"\
        f"• {get_compatible_components(component, blood_group, rh_factor_common)}"
    
    await update.message.reply_text(
        result_text, 
        reply_markup=BMT_choice_keyboard,
        parse_mode='Markdown'
    )

def get_compatible_components(component: str, blood_group: str, rh_factor_common: str) -> str:
    #Функция для определения совместимых компонентов крови
    if component == granulocytes:
        if blood_group == blood_group_O:
            return "Совместимость: группа О"
        elif blood_group == blood_group_A:
            return "Совместимость: группы А, О"
        elif blood_group == blood_group_A2:
            return "Совместимость: группа О"
        elif blood_group == blood_group_B:
            return "Совместимость: группы B, О"
        elif blood_group == blood_group_AB:
            return "Совместимость: все группы ✅"
        elif blood_group == blood_group_A2B:
            return "Совместимость: группы О, B"
        elif blood_group == blood_group_unknown:
            return "Совместимость: группа О"
    if component == platelets:
        if blood_group == blood_group_O:
            return "Варианты тромбоцитов:\n\n"\
                    "• Тромбоциты в плазме донора \nиз единицы крови\n"\
                    "→ Совместимость: группа О\n"\
                    "• Тромбоциты в плазме донора (аферез)\n"\
                    "  → Совместимость: группы O, AB\n"\
                    "• Тромбоциты в добавочном растворе\n"\
                    "  → Совместимость: все группы ✅"
        elif blood_group == blood_group_A or blood_group == blood_group_A2:
            return "Варианты тромбоцитов:\n\n"\
                    "• Тромбоциты в плазме донора \nиз единицы крови\n"\
                    "→ Совместимость: группы A, О\n"\
                    "• Тромбоциты в плазме донора (аферез)\n"\
                    "  → Совместимость: группы A, AB\n"\
                    "• Тромбоциты в добавочном растворе\n"\
                    "  → Совместимость: все группы ✅"
        elif blood_group == blood_group_B:
            return "Варианты тромбоцитов:\n\n"\
                    "• Тромбоциты в плазме донора \nиз единицы крови\n"\
                    "→ Совместимость: группы B, О\n"\
                    "• Тромбоциты в плазме донора (аферез)\n"\
                    "  → Совместимость: группы B, AB\n"\
                    "• Тромбоциты в добавочном растворе\n"\
                    "  → Совместимость: все группы ✅"
        elif blood_group == blood_group_AB or blood_group == blood_group_A2B or blood_group == blood_group_unknown:
            return "Варианты тромбоцитов:\n\n"\
                    "• Тромбоциты в плазме донора \nиз единицы крови\n"\
                    "→ Совместимость: группы АB, О\n"\
                    "• Тромбоциты в плазме донора (аферез)\n"\
                    "  → Совместимость: группа AB\n"\
                    "• Тромбоциты в добавочном растворе\n"\
                    "  → Совместимость: все группы ✅"""
        else:
            return "Неизвестная комбинация компонентов"
    elif component == plasma:
        if blood_group == blood_group_O:
            return "Совместимость: все группы ✅"
        elif blood_group == blood_group_A or blood_group == blood_group_A2:
            return "Совместимость: группы А, AB"
        elif blood_group == blood_group_B:
            return "Совместимость: группы B, AB"
        elif blood_group == blood_group_AB or blood_group == blood_group_A2B:
            return "Совместимость: группа AB"
        elif blood_group == blood_group_unknown:
            return "Совместимость: группа AB"
    elif component == cryoprecipitate:        
        return """Варианты криопреципитата:                   
                      
→ Совместимость: все группы ✅"""        
    elif component == blood:        
        result = get_rh_combinations_from_values(rh_factor_common)
        message ="\n"
        for i, combo in enumerate(result, 1):
            message += f"{i}. {combo}\n"
        if blood_group == blood_group_O:
            return f"""Варианты эритроцитов:

→ Совместимость: группа О
→ Возможная резус-принадлежность донора: {message}"""
        elif blood_group == blood_group_A:
            return f"""Варианты эритроцитов:

→ Совместимость: группа А, О
→ Возможная резус-принадлежность донора: {message}"""
        elif blood_group == blood_group_A2:
            return f"""Варианты эритроцитов:

→ Совместимость: группа О
→ Возможная резус-принадлежность донора: {message}"""
        elif blood_group == blood_group_B:
            return f"""Варианты эритроцитов:

→ Совместимость: группа B, О
→ Возможная резус-принадлежность донора: {message}"""
        elif blood_group == blood_group_AB:
            return f"""Варианты эритроцитов:

→ Совместимость: все группы ✅
→ Возможная резус-принадлежность донора: {message}"""
        elif blood_group == blood_group_A2B:
            return f"""Варианты эритроцитов:

→ Совместимость: группа О, B
→ Возможная резус-принадлежность донора: {message}"""
        elif blood_group == blood_group_unknown:
            return f"""Варианты эритроцитов:

→ Совместимость: группа О
→ Возможная резус-принадлежность донора: {message}"""

async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик неизвестных сообщений"""
    await update.message.reply_text(
        "Пожалуйста, используйте кнопки для навигации 🩺",
        reply_markup=components_keyboard
    )