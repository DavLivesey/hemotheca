from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from keyboards import *
from elements import *


# Состояния для ConversationHandler

HDN_STATES = range(5, 10)


(HDN_CHOICE, HDN_RECIPIENT_BLOOD_GROUP, HDN_RECIPIENT_RH_FACTOR, HDN_MOTHER_BLOOD_GROUP, HDN_MOTHER_RH_FACTOR) = HDN_STATES



def get_rh_combinations_from_values_with_HDN(patient_values, mother_values):
    #Возвращает все возможные комбинации резус-фактора 
    #для генотипа, заданного значениями
    rh_dict = {
        "DD": ["D, dd"],
        "Ddd" : ["dd"],
        "DD неизвестен": ["dd"],
        "ddD неизвестен": ["dd"],
        "dddd": ["dd"],
        "ddD": ["dd"],
        "D неизвестенD": ["dd"],
        "D неизвестенdd": ["dd"],
        "D weakD неизвестен": ["dd"],
        "D weakD weak": ["dd"],
        "D weakD": ["dd"],
        "D weakdd": ["dd"],
        "DD weak": ["dd"],
        "ddD weak": ["dd"],
        "D partial неизвестен": ["dd"],
        "D partialD weak": ["dd"],
        "D partialD": ["dd"],
        "D partialdd": ["dd"],
        "DD partial": ["dd"],
        "ddD partial": ["dd"],
        "D weakD partial": ["dd"],
        "D partialD partial": ["dd"],
        "D неизвестенD weak": ["dd"],
        "D неизвестенD partial": ["dd"],
        "D неизвестенD неизвестен": ["dd"],

        "CCCC": ["CC"],
        "CCCc": ["CC"],
        "CCcc": ["CC"],
        "C неизвестенC неизвестен": ["CC"],
        "CCC неизвестен": ["CC"],
        "CcCC": ["CC"],
        "CcCc": ["CC", "Cc", "cc"],
        "Cccc": ["Cc", "cc"],
        "CcC неизвестен": ["CC"],
        "ccCC": ["CC"],
        "ccCc": ["Cc", "cc"],
        "cccc": ["Cc", "cc"],
        "ccC неизвестен": ["CC"],
        "C неизвестенCC": ["CC"],
        "C неизвестенCc": ["CC"],
        "C неизвестенcc": ["CC"],

        "EEEE": ["EE", "Ee"],
        "EEEe": ["EE", "Ee"],
        "EEee": ["ee"],
        "E неизвестенE неизвестен": ["ee"],
        "EEE неизвестен": ["ee"],
        "EeEE": ["EE", "Ee", "ee"],
        "EeEe": ["EE", "Ee", "ee"],
        "Eeee": ["ee"],
        "EeE неизвестен": ["ee"],
        "eeEE": ["ee"],
        "eeEe": ["ee"],
        "eeee": ["ee"],
        "eeE неизвестен": ["ee"],
        "E неизвестенEE": ["ee"],
        "E неизвестенEe": ["ee"],
        "E неизвестенee": ["ee"]

    }
    common_rh_factor = []
    for rh_factor in patient_values:
        common_rh_factor.append(rh_factor+mother_values[patient_values.index(rh_factor)])

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
    return combinations

async def handle_HDN_choice_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Начало ConversationHandler для пациентов с ГБН
    context.chat_data['patient_type'] = 'with_HDN'
    await update.message.reply_text(
        "Для пациента с ГБН выберите компонент крови:", 
        reply_markup=components_keyboard
    )
    return HDN_CHOICE

async def handle_component_with_HDN(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Обработчик выбора компонента для пациентов с ГБН
    context.chat_data['component'] = update.message.text
    await update.message.reply_text(
        "Выберите группу крови реципиента (пациента) (пациента):", 
        reply_markup=blood_group_keyboard
    )
    return HDN_RECIPIENT_BLOOD_GROUP


async def handle_recipient_blood_group_with_HDN(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.chat_data['recipient_blood_group']  = update.message.text
    component = context.chat_data['component']   
    if component == blood:
        await update.message.reply_text(
        f"Вы выбрали {context.chat_data['recipient_blood_group']}, теперь выберите резус-фактор D реципиента (пациента) ", 
        reply_markup=rh_keyboard_D, 
        parse_mode="Markdown"
        )
        return HDN_RECIPIENT_RH_FACTOR
    else:
        await update.message.reply_text(
        f"Вы выбрали {context.chat_data['recipient_blood_group']}, теперь выберите группу крови матери пациента", 
        reply_markup=blood_group_keyboard, 
        parse_mode="Markdown"
        )
        return HDN_MOTHER_BLOOD_GROUP


async def handle_mother_blood_group_with_HDN(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Обработчик группы крови матери для пациентов с ГБН
    context.chat_data['mother_blood_group'] = update.message.text
    component = context.chat_data['component']
    if component == blood:
        # Для ЭСК запрашиваем резус-факторы матери
        await update.message.reply_text("Выберите резус-фактор D матери:",
                                        reply_markup=rh_keyboard_D,
                                        parse_mode="Markdown"
        )
        return HDN_MOTHER_RH_FACTOR
    else:
        # Формируем результат
        result_text = f"✅ Подбор завершен!\n\n"\
              "**Параметры пациента:**\n"\
              f"• Группа крови: {context.chat_data['recipient_blood_group']}\n"\
              f"• Компонент: {component}\n\n"\
              "**Параметры матери:**\n"\
              f"• Группа крови: {context.chat_data['mother_blood_group']}\n\n"\
              "**Рекомендуемые компоненты:**\n"\
              f"• {get_compatible_components_with_HDN(component, context.chat_data['recipient_blood_group'], context.chat_data['mother_blood_group'], '', '')}"

        await update.message.reply_text(
            result_text, 
            reply_markup=BMT_choice_keyboard,
            parse_mode="Markdown"
        )
        return ConversationHandler.END

async def handle_recipient_rh_factor_D_with_HDN(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient_rh_D = update.message.text
    context.chat_data['recipient_rh_D'] = recipient_rh_D
    await update.message.reply_text("Выберите резус-фактор C реципиента (пациента):",      
        reply_markup=rh_keyboard_C,
        parse_mode="Markdown"
    )
    return HDN_RECIPIENT_RH_FACTOR

async def handle_recipient_rh_factor_C_with_HDN(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient_rh_C = update.message.text
    context.chat_data['recipient_rh_C'] = recipient_rh_C
    await update.message.reply_text("Выберите резус-фактор E реципиента (пациента):",      
        reply_markup=rh_keyboard_E,
        parse_mode="Markdown"
    )
    return HDN_RECIPIENT_RH_FACTOR

async def handle_recipient_rh_factor_E_with_HDN(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient_rh_E = update.message.text
    context.chat_data['recipient_rh_E'] = recipient_rh_E
    await update.message.reply_text("Выберите группу крови матери пациента:",      
        reply_markup=blood_group_keyboard,
        parse_mode="Markdown"
    )
    return HDN_MOTHER_BLOOD_GROUP

async def handle_mother_rh_factor_d_with_HDN(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient_rh_D = update.message.text
    context.chat_data['mother_rh_D'] = recipient_rh_D
    await update.message.reply_text("Выберите резус-фактор C матери пациента:",      
        reply_markup=rh_keyboard_C,
        parse_mode="Markdown"
    )
    return HDN_MOTHER_RH_FACTOR

async def handle_mother_rh_factor_c_with_HDN(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient_rh_C = update.message.text
    context.chat_data['mother_rh_C'] = recipient_rh_C
    await update.message.reply_text("Выберите резус-фактор E матери пациента:",      
        reply_markup=rh_keyboard_E,
        parse_mode="Markdown"
    )
    return HDN_MOTHER_RH_FACTOR

async def handle_mother_rh_factor_e_with_HDN(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Обработчик выбора резус-фактора матери
    mother_rh_factor_E = update.message.text
    component = context.chat_data['component']
    mother_blood_group = context.chat_data['mother_blood_group']
    recipient_blood_group = context.chat_data['recipient_blood_group']
    rh_factor_common = [context.chat_data['recipient_rh_D'], context.chat_data['recipient_rh_C'], context.chat_data['recipient_rh_E']]
    mother_rh_factor_common = [context.chat_data['mother_rh_D'], context.chat_data['mother_rh_C'], mother_rh_factor_E]
    
    # Формируем результат
    result_text = "✅ Подбор завершен!\n\n"\
        f"• Группа крови реципиента (пациента): {recipient_blood_group}\n"\
        f"• Резус-фактор реципиента (пациента): {context.chat_data['recipient_rh_D']}{context.chat_data['recipient_rh_C']}{context.chat_data['recipient_rh_E']}\n\n"\
        f"• Группа крови матери пациента: {context.chat_data['mother_blood_group']}\n"\
        f"• Резус-фактор матери пациента: {context.chat_data['mother_rh_D']}{context.chat_data['mother_rh_C']}{mother_rh_factor_E}\n\n"\
        "**Рекомендуемые компоненты:**\n"\
        f"• {get_compatible_components_with_HDN(component, recipient_blood_group, mother_blood_group, rh_factor_common, mother_rh_factor_common)}"
    
    await update.message.reply_text(
        result_text, 
        reply_markup=BMT_choice_keyboard,
        parse_mode='Markdown'
    )
    return ConversationHandler.END

def get_compatible_components_with_HDN(component: str, blood_group: str, mother_blood_group: str, rh_factor_common: str, MOTHER_RH_FACTOR_common: str) -> str:
    #Функция для определения совместимых компонентов крови
    if component == granulocytes:
        if mother_blood_group == blood_group_O \
            or (blood_group in (blood_group_O, blood_group_A2, blood_group_B, blood_group_A2B) and mother_blood_group == blood_group_A)\
            or mother_blood_group == blood_group_A2\
            or (blood_group in (blood_group_O, blood_group_A, blood_group_A2) and mother_blood_group == blood_group_B)\
            or(blood_group in (blood_group_O, blood_group_A2) and mother_blood_group == blood_group_AB)\
            or (blood_group in(blood_group_O, blood_group_A, blood_group_A2) and mother_blood_group == blood_group_A2B)\
            or blood_group == blood_group_unknown:
            return "Варианты гранулоцитов:\n\n"\
                    "→ Совместимость: группа О"
        elif blood_group == mother_blood_group == blood_group_A\
            or (blood_group == blood_group_AB and mother_blood_group ==blood_group_A)\
            or (blood_group == blood_group_A and mother_blood_group ==blood_group_AB):
            return "Варианты гранулоцитов:\n\n"\
                    "→ Совместимость: группа А, О"

        elif (blood_group in (blood_group_AB, blood_group_A2B, blood_group_B) and mother_blood_group == blood_group_B)\
            or (blood_group in (blood_group_B, blood_group_A2B) and mother_blood_group == blood_group_AB)\
            or (blood_group in (blood_group_B, blood_group_AB, blood_group_A2B) and mother_blood_group == blood_group_A2B):
            return "Варианты гранулоцитов:\n\n"\
                    "→ Совместимость: группа B, О"
        elif blood_group == mother_blood_group == blood_group_AB:
            return "Варианты гранулоцитов:\n\n"\
                    "→ Совместимость: группы группы О, А, В, АВ"
    if component == platelets:
        if blood_group == mother_blood_group == blood_group_O:
            return "Варианты тромбоцитов:\n\n"\
                    "• Тромбоциты в плазме донора \nиз единицы крови\n"\
                    "  → Совместимость: группа О\n\n"\
                    "• Тромбоциты в плазме донора (аферез)\n"\
                    "  → Совместимость: группы О, AB\n\n"\
                    "• Тромбоциты в добавочном растворе\n"\
                    "  → Совместимость: группы О, А, В, АВ"
        elif blood_group in (blood_group_A, blood_group_A2) and mother_blood_group == blood_group_O\
            or blood_group in (blood_group_O, blood_group_A, blood_group_A2) and mother_blood_group in (blood_group_A, blood_group_A2):
            return "Варианты тромбоцитов:\n\n"\
                    "• Тромбоциты в плазме донора \nиз единицы крови\n"\
                    "  → Совместимость: группы A, О\n\n"\
                    "• Тромбоциты в плазме донора (аферез)\n"\
                    "  → Совместимость: группы A, AB\n\n"\
                    "• Тромбоциты в добавочном растворе\n"\
                    "  → Совместимость: группы О, А, В, АВ"
        elif blood_group in (blood_group_B, blood_group_A2B) and mother_blood_group in (blood_group_O, blood_group_B)\
            or blood_group == blood_group_O and mother_blood_group in (blood_group_B, blood_group_A2B):
            return "Варианты тромбоцитов:\n\n"\
                    "• Тромбоциты в плазме донора \nиз единицы крови\n"\
                    "  → Совместимость: группы B, О\n\n"\
                    "• Тромбоциты в плазме донора (аферез)\n"\
                    "  → Совместимость: группы B, AB\n\n"\
                    "• Тромбоциты в добавочном растворе\n"\
                    "  → Совместимость: группы О, А, В, АВ"
        elif blood_group == blood_group_AB and mother_blood_group in (blood_group_O, blood_group_AB):
            return "Варианты тромбоцитов:\n\n"\
                    "• Тромбоциты в плазме донора \nиз единицы крови\n"\
                    "  → Совместимость: группы AB, О\n\n"\
                    "• Тромбоциты в плазме донора (аферез)\n"\
                    "  → Совместимость: группа AB\n\n"\
                    "• Тромбоциты в добавочном растворе\n"\
                    "  → Совместимость: группы О, А, В, АВ"
        elif blood_group in (blood_group_B, blood_group_AB, blood_group_A2B) and mother_blood_group == blood_group_A\
                or blood_group in (blood_group_B, blood_group_AB, blood_group_A2B) and mother_blood_group == blood_group_A2\
                or blood_group in (blood_group_A, blood_group_AB, blood_group_A2B) and mother_blood_group == blood_group_B\
                or blood_group in (blood_group_O, blood_group_A, blood_group_A2, blood_group_B, blood_group_A2B) and mother_blood_group == blood_group_AB\
                or mother_blood_group in (blood_group_A2B, blood_group_unknown)\
                or blood_group == blood_group_unknown:
            return "Варианты тромбоцитов:\n\n"\
                    "• Тромбоциты в плазме донора \nиз единицы крови\n"\
                    "  → Совместимость: группа О\n\n"\
                    "• Тромбоциты в плазме донора (аферез)\n"\
                    "  → Совместимость: группа AB\n\n"\
                    "• Тромбоциты в добавочном растворе\n"\
                    "  → Совместимость: группы О, А, В, АВ"
        else:
            return "Неизвестная комбинация компонентов"
    elif component == plasma:
        if blood_group == mother_blood_group == blood_group_O:
            return "Варианты плазмы:\n\n"\
                "• Плазма\n"\
                "→ Совместимость: группы О, A, B, AB"
                    
        elif blood_group in (blood_group_O, blood_group_A, blood_group_A2) and mother_blood_group in (blood_group_O, blood_group_A, blood_group_A2):
            return "Варианты плазмы:\n\n"\
                "• Плазма\n"\
                "→ Совместимость: группы A, AB"
        elif blood_group in(blood_group_O, blood_group_B, blood_group_A2) and mother_blood_group == blood_group_B:
            return "Варианты плазмы:\n\n"\
                "• Плазма\n"\
                "→ Совместимость: группы B, AB"
        elif blood_group in (blood_group_AB, blood_group_A2B) and mother_blood_group == blood_group_O\
                or blood_group in (blood_group_AB, blood_group_A2B, blood_group_B) and mother_blood_group == blood_group_A\
                or blood_group in (blood_group_B, blood_group_AB, blood_group_A2B) and mother_blood_group == blood_group_A2\
                or blood_group in (blood_group_A, blood_group_AB, blood_group_A2B) and mother_blood_group == blood_group_B\
                or mother_blood_group in (blood_group_AB, blood_group_A2B, blood_group_unknown)\
                or blood_group == blood_group_unknown:
            return "Варианты плазмы:\n\n"\
                "• Плазма\n"\
                "→ Совместимость: группа AB"
    elif component == cryoprecipitate:        
        return "Варианты криопреципитата:\n\n"\
                "→ Совместимость: 0, А, В, АВ"
    elif component == blood:        
        result = get_rh_combinations_from_values_with_HDN(rh_factor_common, MOTHER_RH_FACTOR_common)
        message ="\n"
        for i, combo in enumerate(result, 1):
            message += f"{i}. {combo}\n"
        if mother_blood_group in (blood_group_A2, blood_group_unknown, blood_group_O) \
            or blood_group in (blood_group_O, blood_group_A2, blood_group_B, blood_group_A2B) and mother_blood_group == blood_group_A\
            or blood_group in (blood_group_O, blood_group_A, blood_group_A2) and mother_blood_group == blood_group_B\
            or blood_group in (blood_group_O, blood_group_A2) and mother_blood_group == blood_group_AB\
            or blood_group in (blood_group_O, blood_group_A, blood_group_A2) and mother_blood_group == blood_group_A2B\
            or blood_group == blood_group_unknown:
            return "Варианты эритроцитов:\n\n"\
                    "→ Совместимость: группа О\n"\
                    f"→ Возможная резус-принадлежность донора ЭСК: {message}"
        elif blood_group in (blood_group_A, blood_group_AB) and mother_blood_group == blood_group_A\
            or blood_group == blood_group_A and mother_blood_group == blood_group_AB:
            return "Варианты эритроцитов:\n\n"\
                    "→ Совместимость: группы А, О\n"\
                    f"→ Возможная резус-принадлежность донора ЭСК: {message}"
        elif blood_group in (blood_group_B, blood_group_AB, blood_group_A2B) and mother_blood_group == blood_group_B\
            or blood_group in (blood_group_B, blood_group_A2B) and mother_blood_group == blood_group_AB\
            or blood_group in (blood_group_A2B, blood_group_AB, blood_group_B) and mother_blood_group == blood_group_A2B:
            return "Варианты эритроцитов:\n\n"\
                    "→ Совместимость: группы B, О\n"\
                    f"→ Возможная резус-принадлежность донора ЭСК: {message}"
        elif blood_group == mother_blood_group == blood_group_AB:
            return "Варианты эритроцитов:\n\n"\
                    "→ Совместимость: группы O, A, B, AB\n"\
                    f"→ Возможная резус-принадлежность донора ЭСК: {message}"
        

async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик неизвестных сообщений"""
    await update.message.reply_text(
        "Пожалуйста, используйте кнопки для навигации 🩺",
        reply_markup=components_keyboard
    )