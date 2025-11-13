from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from keyboards import *
from elements import *


CHIMERA_STATES = range(10, 15)
(CHIMERA_CHOICE, CHIMERA_RECIPIENT_BLOOD_GROUP, CHIMERA_RECIPIENT_RH_FACTOR, CHIMERA_BLOOD_GROUP, CHIMERA_RH_FACTOR) = CHIMERA_STATES


def get_rh_combinations_from_values_chimera(patient_values, chimera_values):
    #Возвращает все возможные комбинации резус-фактора 
    #для генотипа, заданного значениями
    rh_dict = {
        "Ddd" : ["dd"],
        "ddD": ["dd"],
        "D weakD": ["dd"],
        "D weakdd": ["dd"],
        "DD weak": ["dd"],
        "ddD weak": ["dd"],
        "D partialD weak": ["dd"],
        "D partialD": ["dd"],
        "D partialdd": ["dd"],
        "DD partial": ["dd"],
        "ddD partial": ["dd"],
        "D weakD partial": ["dd"],

        "CCCc": ["CC"],
        "CCcc": ["CC"],
        "CcCC": ["CC"],
        "Cccc": ["Cc", "cc"],
        "ccCC": ["CC"],
        "ccCc": ["Cc", "cc"],

        "EEEe": ["Ee", "Ee"],
        "EEee": ["ee"],
        "EeEE": ["EE", "Ee"],
        "Eeee": ["ee"],
        "eeEE": ["ee"],
        "eeEe": ["ee"]

    }
    common_rh_factor = []
    for rh_factor in patient_values:
        common_rh_factor.append(rh_factor+chimera_values[patient_values.index(rh_factor)])

    options_lists = []
    for val in common_rh_factor:
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
    return set(combinations)

async def handle_chimera_choice_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Начало ConversationHandler для пациентов с химерой
    context.chat_data['patient_type'] = 'chimera'
    await update.message.reply_text(
        "Для пациента с химерой выберите компонент крови:", 
        reply_markup=components_keyboard
    )
    return CHIMERA_CHOICE

async def handle_component_chimera(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Обработчик выбора компонента для пациентов с химерой
    context.chat_data['component'] = update.message.text
    await update.message.reply_text(
        "Выберите группу крови реципиента (пациента):", 
        reply_markup=blood_group_keyboard
    )
    return CHIMERA_RECIPIENT_BLOOD_GROUP


async def handle_chimera_recipient_blood_group(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.chat_data['recipient_blood_group']  = update.message.text
    component = context.chat_data['component']   
    if component == blood:
        await update.message.reply_text(
        f"Вы выбрали {context.chat_data['recipient_blood_group']}, теперь выберите резус-фактор D реципиента (пациента) ", 
        reply_markup=rh_keyboard_D_chimera, 
        parse_mode="Markdown"
        )
        return CHIMERA_RECIPIENT_RH_FACTOR
    else:
        blood_group_keyboard_chimera = get_chimera_keyboard("group", context.chat_data['recipient_blood_group'])
        await update.message.reply_text(
        f"Вы выбрали {context.chat_data['recipient_blood_group']}, теперь выберите группу крови химеры", 
        reply_markup=blood_group_keyboard_chimera, 
        parse_mode="Markdown"
        )
        return CHIMERA_BLOOD_GROUP


async def handle_chimera_blood_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Обработчик группы крови химеры для пациентов с химерой
    context.chat_data['chimera_blood_group'] = update.message.text
    component = context.chat_data['component']
    if component == blood:
        rh_keyboard_chimera_D = get_chimera_keyboard("D", context.chat_data['recipient_rh_D'])
        # Для ЭСК запрашиваем резус-факторы химеры
        await update.message.reply_text("Выберите резус-фактор D химеры:",
                                        reply_markup=rh_keyboard_chimera_D,
                                        parse_mode="Markdown"
        )
        return CHIMERA_RH_FACTOR
    else:
        # Формируем результат
        result_text = f"✅ Подбор завершен!\n\n"\
              "**Параметры пациента:**\n"\
              f"• Группа крови: {context.chat_data['recipient_blood_group']}\n"\
              f"• Компонент: {component}\n\n"\
              "**Параметры химеры:**\n"\
              f"• Группа крови: {context.chat_data['chimera_blood_group']}\n\n"\
              f"• {get_compatible_components_chimera(component, context.chat_data['recipient_blood_group'], context.chat_data['chimera_blood_group'], '', '')}"

        await update.message.reply_text(
            result_text, 
            reply_markup=BMT_choice_keyboard,
            parse_mode="Markdown"
        )
        return ConversationHandler.END

async def handle_chimera_recipient_rh_factor_D(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient_rh_D = update.message.text
    context.chat_data['recipient_rh_D'] = recipient_rh_D
    await update.message.reply_text("Выберите резус-фактор C реципиента (пациента):",      
        reply_markup=rh_keyboard_C_chimera,
        parse_mode="Markdown"
    )
    return CHIMERA_RECIPIENT_RH_FACTOR

async def handle_chimera_recipient_rh_factor_C(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient_rh_C = update.message.text
    context.chat_data['recipient_rh_C'] = recipient_rh_C
    await update.message.reply_text("Выберите резус-фактор E реципиента (пациента):",      
        reply_markup=rh_keyboard_E_chimera,
        parse_mode="Markdown"
    )
    return CHIMERA_RECIPIENT_RH_FACTOR

async def handle_chimera_recipient_rh_factor_E(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient_rh_E = update.message.text
    context.chat_data['recipient_rh_E'] = recipient_rh_E
    blood_group_keyboard_chimera = get_chimera_keyboard("group", context.chat_data['recipient_blood_group'])
    await update.message.reply_text("Выберите группу крови химеры:",      
        reply_markup=blood_group_keyboard_chimera,
        parse_mode="Markdown"
    )
    return CHIMERA_BLOOD_GROUP

async def handle_chimera_rh_factor_d(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient_rh_D = update.message.text
    context.chat_data['chimera_rh_D'] = recipient_rh_D
    rh_keyboard_chimera_C = get_chimera_keyboard("C", context.chat_data['recipient_rh_C'])
    await update.message.reply_text("Выберите резус-фактор C химеры:",      
        reply_markup=rh_keyboard_chimera_C,
        parse_mode="Markdown"
    )
    return CHIMERA_RH_FACTOR

async def handle_chimera_rh_factor_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient_rh_C = update.message.text
    context.chat_data['chimera_rh_C'] = recipient_rh_C
    rh_keyboard_chimera_E = get_chimera_keyboard("E", context.chat_data['recipient_rh_E'])
    await update.message.reply_text("Выберите резус-фактор E химеры:",      
        reply_markup=rh_keyboard_chimera_E,
        parse_mode="Markdown"
    )
    return CHIMERA_RH_FACTOR

async def handle_chimera_rh_factor_e(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Обработчик выбора резус-фактора химеры
    chimera_rh_factor_E = update.message.text
    component = context.chat_data['component']
    chimera_blood_group = context.chat_data['chimera_blood_group']
    recipient_blood_group = context.chat_data['recipient_blood_group']
    rh_factor_common = [context.chat_data['recipient_rh_D'], context.chat_data['recipient_rh_C'], context.chat_data['recipient_rh_E']]
    chimera_rh_factor_common = [context.chat_data['chimera_rh_D'], context.chat_data['chimera_rh_C'], chimera_rh_factor_E]
    
    # Формируем результат
    result_text = "✅ Подбор завершен!\n\n"\
        f"• Группа крови реципиента (пациента): {recipient_blood_group}\n"\
        f"• Резус-фактор реципиента (пациента): {context.chat_data['recipient_rh_D']}{context.chat_data['recipient_rh_C']}{context.chat_data['recipient_rh_E']}\n\n"\
        f"• Группа крови химеры: {context.chat_data['chimera_blood_group']}\n"\
        f"• Резус-фактор химеры: {context.chat_data['chimera_rh_D']}{context.chat_data['chimera_rh_C']}{chimera_rh_factor_E}\n\n"\
        f"• {get_compatible_components_chimera(component, recipient_blood_group, chimera_blood_group, rh_factor_common, chimera_rh_factor_common)}"
    
    await update.message.reply_text(
        result_text, 
        reply_markup=BMT_choice_keyboard,
        parse_mode='Markdown'
    )
    return ConversationHandler.END

def get_compatible_components_chimera(component: str, blood_group: str, chimera_blood_group: str, rh_factor_common: str, chimera_rh_factor_common: str) -> str:
    #Функция для определения совместимых компонентов крови
    if component == granulocytes:
        if blood_group in (blood_group_AB, blood_group_A2B) and chimera_blood_group == blood_group_B\
            or blood_group in (blood_group_B, blood_group_A2B) and chimera_blood_group == blood_group_AB\
            or blood_group in (blood_group_B, blood_group_AB) and chimera_blood_group == blood_group_A2B:
            return "Гранулоциты:\n\n"\
                    "→ Совместимость: группы B, О"
        elif blood_group == blood_group_A and chimera_blood_group == blood_group_AB\
            or blood_group == blood_group_AB and chimera_blood_group == blood_group_A:
            return "Гранулоциты:\n\n"\
                    "→ Совместимость: группы А, О"
        else:
            return "Гранулоциты:\n\n"\
                    "→ Совместимость: группа О"
    elif component == platelets:
        if blood_group in (blood_group_A, blood_group_A2) and chimera_blood_group == blood_group_O\
            or blood_group in (blood_group_O, blood_group_A2) and chimera_blood_group == blood_group_A\
            or blood_group in (blood_group_O, blood_group_A) and chimera_blood_group == blood_group_A2:
            return "Варианты тромбоцитов:\n\n"\
                    "• Тромбоциты в плазме донора \nиз единицы крови\n"\
                    "  → Совместимость: группа A, О\n\n"\
                    "• Тромбоциты в плазме донора (аферез)\n"\
                    "  → Совместимость: группы A, AB\n\n"\
                    "• Тромбоциты в добавочном растворе\n"\
                    "  → Совместимость: группы О, А, В, АВ"
        elif blood_group in (blood_group_B, blood_group_A2B) and chimera_blood_group == blood_group_O\
            or blood_group in (blood_group_O, blood_group_A2) and chimera_blood_group == blood_group_B\
            or blood_group == blood_group_O and chimera_blood_group == blood_group_A2B:
            return "Варианты тромбоцитов:\n\n"\
                    "• Тромбоциты в плазме донора \nиз единицы крови\n"\
                    "  → Совместимость: группа B, О\n\n"\
                    "• Тромбоциты в плазме донора (аферез)\n"\
                    "  → Совместимость: группы B, AB\n\n"\
                    "• Тромбоциты в добавочном растворе\n"\
                    "  → Совместимость: группы О, А, В, АВ"
        else:
            return "Варианты тромбоцитов:\n\n"\
                    "• Тромбоциты в плазме донора \nиз единицы крови\n"\
                    "  → Совместимость: группа О\n\n"\
                    "• Тромбоциты в плазме донора (аферез)\n"\
                    "  → Совместимость: группы AB\n\n"\
                    "• Тромбоциты в добавочном растворе\n"\
                    "  → Совместимость: группы О, А, В, АВ"
        
    elif component == plasma:
        if blood_group in (blood_group_A, blood_group_A2) and chimera_blood_group == blood_group_O\
            or blood_group in (blood_group_O, blood_group_A2) and chimera_blood_group == blood_group_A\
            or blood_group in (blood_group_O, blood_group_A) and chimera_blood_group == blood_group_A2:
            return "Плазма\n"\
                "→ Совместимость: группы A, AB"
        elif blood_group == blood_group_B and chimera_blood_group == blood_group_O\
            or blood_group in (blood_group_O, blood_group_A2) and chimera_blood_group == blood_group_B:
            return "Плазма\n"\
                "→ Совместимость: группы B, AB"
        else:
            return "Плазма\n"\
                "→ Совместимость: группа AB"   
        
    elif component == cryoprecipitate:        
        return "Криопреципитат:\n\n"\
                "→ Совместимость: 0, А, В, АВ"
    elif component == blood:      
        result = get_rh_combinations_from_values_chimera(rh_factor_common, chimera_rh_factor_common)
        message ="\n"
        for i, combo in enumerate(result, 1):
            message += f"{i}. {combo}\n"
        if blood_group in (blood_group_AB, blood_group_A2B) and chimera_blood_group == blood_group_B\
            or blood_group in (blood_group_B, blood_group_A2B) and chimera_blood_group == blood_group_AB\
            or blood_group in (blood_group_B, blood_group_AB) and chimera_blood_group == blood_group_A2B:
            return "Эритроциты:\n\n"\
                    "→ Совместимость: группы B, О\n"\
                    f"→ Возможная резус-принадлежность донора ЭСК: {message}"
        elif blood_group == blood_group_A and chimera_blood_group == blood_group_AB\
            or blood_group == blood_group_AB and chimera_blood_group == blood_group_A:
            return "Эритроциты:\n\n"\
                    "→ Совместимость: группы A, О\n"\
                    f"→ Возможная резус-принадлежность донора ЭСК: {message}"
        else:
            return "Эритроциты:\n\n"\
                    "→ Совместимость: группа О\n"\
                    f"→ Возможная резус-принадлежность донора ЭСК: {message}"
        

async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик неизвестных сообщений"""
    await update.message.reply_text(
        "Пожалуйста, используйте кнопки для навигации 🩺",
        reply_markup=components_keyboard
    )