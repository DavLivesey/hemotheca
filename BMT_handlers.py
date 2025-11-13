from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from keyboards import *
from elements import *


BMT_STATES = range(5)
(BMT_CHOICE, RECIPIENT_BLOOD_GROUP, RECIPIENT_RH_FACTOR, DONOR_BLOOD_GROUP, DONOR_RH_FACTOR) = BMT_STATES


def get_rh_combinations_from_values_with_BTM(patient_values, donor_values):
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
        common_rh_factor.append(rh_factor+donor_values[patient_values.index(rh_factor)])

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

async def handle_BMT_choice_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало ConversationHandler для пациентов с ТКМ"""
    context.chat_data['patient_type'] = 'with_bmt'
    await update.message.reply_text(
        "Для пациента с ТКМ в анамнезе выберите компонент крови:", 
        reply_markup=components_keyboard
    )
    return BMT_CHOICE

async def handle_BMT_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Обработчик главного меню
    context.chat_data['status'] = update.message.text
    if update.message.text == BMT_in_past:
        await update.message.reply_text("Выберите компонент крови:", reply_markup=components_keyboard)
    elif update.message.text == clear_patient:
        await update.message.reply_text("Выберите компонент крови:", reply_markup=components_keyboard)
    else:
        await update.message.reply_text("Эта часть еще в разработке", reply_markup=BMT_choice_keyboard)

async def handle_component_with_BMT(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Обработчик выбора компонента для пациентов с ТКМ
    context.chat_data['component'] = update.message.text
    await update.message.reply_text(
        "Выберите группу крови РЕЦИПИЕНТА (пациента):", 
        reply_markup=blood_group_keyboard
    )
    return RECIPIENT_BLOOD_GROUP


async def handle_recipient_blood_group_with_BMT(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.chat_data['recipient_blood_group']  = update.message.text
    component = context.chat_data['component']   
    if component == blood:
        await update.message.reply_text(
        f"Вы выбрали {context.chat_data['recipient_blood_group']}, теперь выберите резус-фактор D реципиента (пациента)", 
        reply_markup=rh_keyboard_D, 
        parse_mode="Markdown"
        )
        return RECIPIENT_RH_FACTOR
    else:
        await update.message.reply_text(
        f"Вы выбрали {context.chat_data['recipient_blood_group']}, теперь выберите группу крови донора КМ или ГСК", 
        reply_markup=blood_group_keyboard, 
        parse_mode="Markdown"
        )
        return DONOR_BLOOD_GROUP


async def handle_donor_blood_group_with_BMT(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик группы крови донора для пациентов с ТКМ"""
    context.chat_data['donor_blood_group'] = update.message.text
    component = context.chat_data['component']
    if component == blood:
        # Для ЭСК запрашиваем резус-факторы донора
        await update.message.reply_text("Выберите резус-фактор D донора:",
                                        reply_markup=rh_keyboard_D,
                                        parse_mode="Markdown"
        )
        return DONOR_RH_FACTOR
    else:
        # Формируем результат
        result_text = f"✅ Подбор завершен!\n\n"\
              "**Параметры пациента:**\n"\
              f"• Группа крови: {context.chat_data['recipient_blood_group']}\n"\
              f"• Компонент: {component}\n\n"\
              "**Параметры донора КМ или ГСК:**\n"\
              f"• Группа крови: {context.chat_data['donor_blood_group']}\n\n"\
              f"• {get_compatible_components_with_BMT(component, context.chat_data['recipient_blood_group'], context.chat_data['donor_blood_group'], '', '')}"

        await update.message.reply_text(
            result_text, 
            reply_markup=BMT_choice_keyboard,
            parse_mode="Markdown"
        )
        return ConversationHandler.END

async def handle_recipient_rh_factor_D_with_BMT(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient_rh_D = update.message.text
    context.chat_data['recipient_rh_D'] = recipient_rh_D
    await update.message.reply_text("Выберите резус-фактор C реципиента:",      
        reply_markup=rh_keyboard_C,
        parse_mode="Markdown"
    )
    return RECIPIENT_RH_FACTOR

async def handle_recipient_rh_factor_C_with_BMT(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient_rh_C = update.message.text
    context.chat_data['recipient_rh_C'] = recipient_rh_C
    await update.message.reply_text("Выберите резус-фактор E реципиента:",      
        reply_markup=rh_keyboard_E,
        parse_mode="Markdown"
    )
    return RECIPIENT_RH_FACTOR

async def handle_recipient_rh_factor_E_with_BMT(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient_rh_E = update.message.text
    context.chat_data['recipient_rh_E'] = recipient_rh_E
    await update.message.reply_text("Выберите группу крови донора:",      
        reply_markup=blood_group_keyboard,
        parse_mode="Markdown"
    )
    return DONOR_BLOOD_GROUP

async def handle_donor_rh_factor_D_with_BMT(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient_rh_D = update.message.text
    context.chat_data['donor_rh_D'] = recipient_rh_D
    await update.message.reply_text("Выберите резус-фактор C донора:",      
        reply_markup=rh_keyboard_C,
        parse_mode="Markdown"
    )
    return DONOR_RH_FACTOR

async def handle_donor_rh_factor_C_with_BMT(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient_rh_C = update.message.text
    context.chat_data['donor_rh_C'] = recipient_rh_C
    await update.message.reply_text("Выберите резус-фактор E донора:",      
        reply_markup=rh_keyboard_E,
        parse_mode="Markdown"
    )
    return DONOR_RH_FACTOR

async def handle_donor_rh_factor_E_with_BMT(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Обработчик выбора резус-фактора донора
    donor_rh_factor_E = update.message.text
    component = context.chat_data['component']
    donor_blood_group = context.chat_data['donor_blood_group']
    recipient_blood_group = context.chat_data['recipient_blood_group']
    rh_factor_common = [context.chat_data['recipient_rh_D'], context.chat_data['recipient_rh_C'], context.chat_data['recipient_rh_E']]
    donor_rh_factor_common = [context.chat_data['donor_rh_D'], context.chat_data['donor_rh_C'], donor_rh_factor_E]
    
    # Формируем результат
    result_text = "✅ Подбор завершен!\n\n"\
        f"• Группа крови реципиента (пациента): {recipient_blood_group}\n"\
        f"• Резус-фактор реципиента (пациента): {context.chat_data['recipient_rh_D']}{context.chat_data['recipient_rh_C']}{context.chat_data['recipient_rh_E']}\n\n"\
        f"• Группа крови донора: {context.chat_data['donor_blood_group']}\n"\
        f"• Резус-фактор донора: {context.chat_data['donor_rh_D']}{context.chat_data['donor_rh_C']}{donor_rh_factor_E}\n\n"\
        f"• {get_compatible_components_with_BMT(component, recipient_blood_group, donor_blood_group, rh_factor_common, donor_rh_factor_common)}"
    
    await update.message.reply_text(
        result_text, 
        reply_markup=BMT_choice_keyboard,
        parse_mode='Markdown'
    )
    return ConversationHandler.END

def get_compatible_components_with_BMT(component: str, blood_group: str, donor_blood_group: str, rh_factor_common: str, donor_rh_factor_common: str) -> str:
    #Функция для определения совместимых компонентов крови
    if component == granulocytes:
        if donor_blood_group == blood_group_O \
            or (blood_group in (blood_group_O, blood_group_A2, blood_group_B, blood_group_A2B) and donor_blood_group == blood_group_A)\
            or donor_blood_group == blood_group_A2\
            or (blood_group in (blood_group_O, blood_group_A, blood_group_A2) and donor_blood_group == blood_group_B)\
            or(blood_group in (blood_group_O, blood_group_A2) and donor_blood_group == blood_group_AB)\
            or (blood_group in(blood_group_O, blood_group_A, blood_group_A2) and donor_blood_group == blood_group_A2B)\
            or blood_group == blood_group_unknown:
            return "Совместимость: группа О"
        elif blood_group == donor_blood_group == blood_group_A\
            or (blood_group == blood_group_AB and donor_blood_group ==blood_group_A)\
            or (blood_group == blood_group_A and donor_blood_group ==blood_group_AB):
            return "Совместимость: группы А, О"

        elif (blood_group in (blood_group_AB, blood_group_A2B, blood_group_B) and donor_blood_group == blood_group_B)\
            or (blood_group in (blood_group_B, blood_group_A2B) and donor_blood_group == blood_group_AB)\
            or (blood_group in (blood_group_B, blood_group_AB, blood_group_A2B) and donor_blood_group == blood_group_A2B):
            return "Совместимость: группы B, О"
        elif blood_group == donor_blood_group == blood_group_AB:
            return "Совместимость: группы О, А, В, АВ"
    if component == platelets:
        if blood_group == donor_blood_group == blood_group_O:
            return "Варианты тромбоцитов:\n\n"\
                    "• Тромбоциты в плазме донора \nиз единицы крови\n"\
                    "  → Совместимость: группа О\n\n"\
                    "• Тромбоциты в плазме донора (аферез)\n"\
                    "  → Совместимость: группы О, AB\n\n"\
                    "• Тромбоциты в добавочном растворе\n"\
                    "  → Совместимость: группы О, А, В, АВ"
        elif blood_group in (blood_group_A, blood_group_A2) and donor_blood_group == blood_group_O\
            or blood_group in (blood_group_O, blood_group_A, blood_group_A2) and donor_blood_group in (blood_group_A, blood_group_A2):
            return "Варианты тромбоцитов:\n\n"\
                    "• Тромбоциты в плазме донора \nиз единицы крови\n"\
                    "  → Совместимость: группы A, О\n\n"\
                    "• Тромбоциты в плазме донора (аферез)\n"\
                    "  → Совместимость: группы A, AB\n\n"\
                    "• Тромбоциты в добавочном растворе\n"\
                    "  → Совместимость: группы О, А, В, АВ"
        elif blood_group in (blood_group_B, blood_group_A2B) and donor_blood_group in (blood_group_O, blood_group_B)\
            or blood_group == blood_group_O and donor_blood_group in (blood_group_B, blood_group_A2B):
            return "Варианты тромбоцитов:\n\n"\
                    "• Тромбоциты в плазме донора \nиз единицы крови\n"\
                    "  → Совместимость: группы B, О\n\n"\
                    "• Тромбоциты в плазме донора (аферез)\n"\
                    "  → Совместимость: группы B, AB\n\n"\
                    "• Тромбоциты в добавочном растворе\n"\
                    "  → Совместимость: группы О, А, В, АВ"
        elif blood_group == blood_group_AB and donor_blood_group in (blood_group_O, blood_group_AB):
            return "Варианты тромбоцитов:\n\n"\
                    "• Тромбоциты в плазме донора \nиз единицы крови\n"\
                    "  → Совместимость: группы AB, О\n\n"\
                    "• Тромбоциты в плазме донора (аферез)\n"\
                    "  → Совместимость: группа AB\n\n"\
                    "• Тромбоциты в добавочном растворе\n"\
                    "  → Совместимость: группы О, А, В, АВ"
        elif blood_group in (blood_group_B, blood_group_AB, blood_group_A2B) and donor_blood_group == blood_group_A\
                or blood_group in (blood_group_B, blood_group_AB, blood_group_A2B) and donor_blood_group == blood_group_A2\
                or blood_group in (blood_group_A, blood_group_AB, blood_group_A2B) and donor_blood_group == blood_group_B\
                or blood_group in (blood_group_O, blood_group_A, blood_group_A2, blood_group_B, blood_group_A2B) and donor_blood_group == blood_group_AB\
                or donor_blood_group in (blood_group_A2B, blood_group_unknown)\
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
        if blood_group == donor_blood_group == blood_group_O:
            return "Плазма\n"\
                "→ Совместимость: группы О, A, B, AB"
                    
        elif blood_group in (blood_group_O, blood_group_A, blood_group_A2) and donor_blood_group in (blood_group_O, blood_group_A, blood_group_A2):
            return "Плазма\n"\
                "→ Совместимость: группы A, AB"
        elif blood_group in(blood_group_O, blood_group_B, blood_group_A2) and donor_blood_group == blood_group_B:
            return "Плазма\n"\
                "→ Совместимость: группы B, AB"
        elif blood_group in (blood_group_AB, blood_group_A2B) and donor_blood_group == blood_group_O\
                or blood_group in (blood_group_AB, blood_group_A2B, blood_group_B) and donor_blood_group == blood_group_A\
                or blood_group in (blood_group_B, blood_group_AB, blood_group_A2B) and donor_blood_group == blood_group_A2\
                or blood_group in (blood_group_A, blood_group_AB, blood_group_A2B) and donor_blood_group == blood_group_B\
                or donor_blood_group in (blood_group_AB, blood_group_A2B, blood_group_unknown)\
                or blood_group == blood_group_unknown:
            return "Плазма\n"\
                "→ Совместимость: группа AB"
    elif component == cryoprecipitate:        
        return "Криопреципитат:\n\n"\
                "→ Совместимость: 0, А, В, АВ"
    elif component == blood:        
        result = get_rh_combinations_from_values_with_BTM(rh_factor_common, donor_rh_factor_common)
        message ="\n"
        for i, combo in enumerate(result, 1):
            message += f"{i}. {combo}\n"
        if donor_blood_group in (blood_group_A2, blood_group_unknown, blood_group_O) \
            or blood_group in (blood_group_O, blood_group_A2, blood_group_B, blood_group_A2B) and donor_blood_group == blood_group_A\
            or blood_group in (blood_group_O, blood_group_A, blood_group_A2) and donor_blood_group == blood_group_B\
            or blood_group in (blood_group_O, blood_group_A2) and donor_blood_group == blood_group_AB\
            or blood_group in (blood_group_O, blood_group_A, blood_group_A2) and donor_blood_group == blood_group_A2B\
            or blood_group == blood_group_unknown:
            return "Эритроциты:\n\n"\
                    "→ Совместимость: группа О\n"\
                    f"→ Возможная резус-принадлежность донора ЭСК: {message}"
        elif blood_group in (blood_group_A, blood_group_AB) and donor_blood_group == blood_group_A\
            or blood_group == blood_group_A and donor_blood_group == blood_group_AB:
            return "Эритроциты:\n\n"\
                    "→ Совместимость: группы А, О\n"\
                    f"→ Возможная резус-принадлежность донора ЭСК: {message}"
        elif blood_group in (blood_group_B, blood_group_AB, blood_group_A2B) and donor_blood_group == blood_group_B\
            or blood_group in (blood_group_B, blood_group_A2B) and donor_blood_group == blood_group_AB\
            or blood_group in (blood_group_A2B, blood_group_AB, blood_group_B) and donor_blood_group == blood_group_A2B:
            return "Эритроциты:\n\n"\
                    "→ Совместимость: группы B, О\n"\
                    f"→ Возможная резус-принадлежность донора ЭСК: {message}"
        elif blood_group == donor_blood_group == blood_group_AB:
            return "Эритроциты:\n\n"\
                    "→ Совместимость: группы O, A, B, AB\n"\
                    f"→ Возможная резус-принадлежность донора ЭСК: {message}"
        

async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик неизвестных сообщений"""
    await update.message.reply_text(
        "Пожалуйста, используйте кнопки для навигации 🩺",
        reply_markup=components_keyboard
    )