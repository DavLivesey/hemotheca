from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from keyboards import *
from elements import *


BMT_STATES = range(10, 15)
BMT_MULTI_STATES = range(15, 18)

(BMT_CHOICE, RECIPIENT_BLOOD_GROUP, RECIPIENT_RH_FACTOR, DONOR_BLOOD_GROUP, DONOR_RH_FACTOR) = BMT_STATES
(BMT_QUANTITY, BMT_MULTI_DATA, BMT_MULTI_RESULT) = BMT_MULTI_STATES


def get_rh_combinations_from_values_with_BTM(patient_values, donor_values):
    #Возвращает все возможные комбинации резус-фактора 
    #для генотипа, заданного значениями
    rh_dict = {
        "DD": [" D, dd"],
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

async def handle_bmt_procedure_cycle(update: Update, context: ContextTypes.DEFAULT_TYPE, next_step):
    #Обработчик цикла для множественных ТКМ
    current_procedure = context.chat_data['bmt_current_procedure']
    total_procedures = context.chat_data['bmt_quantity']
    
    # Сохраняем данные текущей процедуры
    procedure_data = {
        'component': context.chat_data.get('component'),
        'recipient_blood_group': context.chat_data.get('recipient_blood_group'),
        'recipient_rh_D': context.chat_data.get('recipient_rh_D'),
        'recipient_rh_C': context.chat_data.get('recipient_rh_C'),
        'recipient_rh_E': context.chat_data.get('recipient_rh_E'),
        'donor_blood_group': context.chat_data.get('donor_blood_group'),
        'donor_rh_D': context.chat_data.get('donor_rh_D'),
        'donor_rh_C': context.chat_data.get('donor_rh_C'),
        'donor_rh_E': context.chat_data.get('donor_rh_E'),
    }
    
    context.chat_data['bmt_procedures_data'].append(procedure_data)
    
    # Очищаем временные данные
    keys_to_clear = ['donor_blood_group', 'donor_rh_D', 'donor_rh_C', 'donor_rh_E']
    for key in keys_to_clear:
        context.chat_data.pop(key, None)
    
    # Увеличиваем счетчик
    current_procedure += 1
    context.chat_data['bmt_current_procedure'] = current_procedure
    
    if current_procedure < total_procedures:
        # Запрашиваем данные для следующей процедуры
        await update.message.reply_text(
            f"Данные для процедуры №{current_procedure} сохранены. "
            f"Переходим к процедуре №{current_procedure + 1}. Выберите группу крови донора №{current_procedure + 1}:",
            reply_markup=blood_group_keyboard
        )
        return DONOR_BLOOD_GROUP
    else:
        # Все процедуры обработаны, формируем итоговый результат
        return await generate_final_bmt_result(update, context)

def format_blood_compatibility(component, compatible_groups):
    #Форматирует текст совместимости по группам крови
    if component in [cryoprecipitate]:
        return "→ Совместимость: 0, А, В, АВ"
    if not compatible_groups:
        return "Совместимость: не определена"    
    if len(compatible_groups) == 1:
        return f"Совместимость: группа {compatible_groups[0]}"
    else:
        groups_text = ", ".join(compatible_groups)
        return f"Совместимость: группы {groups_text}"

async def generate_final_bmt_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Формирование итогового результата для множественных ТКМ
    procedures_data = context.chat_data['bmt_procedures_data']
    component = procedures_data[0]['component']  # Компонент одинаков для всех процедур
    
    # Собираем данные реципиента (они одинаковы для всех процедур)
    recipient_data = {
        'blood_group': procedures_data[0]['recipient_blood_group'],
        'rh_D': procedures_data[0]['recipient_rh_D'],
        'rh_C': procedures_data[0]['recipient_rh_C'],
        'rh_E': procedures_data[0]['recipient_rh_E']
    }
    
    # Собираем данные доноров
    donors_data = []
    for procedure in procedures_data:
        donors_data.append({
            'blood_group': procedure['donor_blood_group'],
            'rh_D': procedure['donor_rh_D'],
            'rh_C': procedure['donor_rh_C'],
            'rh_E': procedure['donor_rh_E']
        })
    
    # Формируем резус-факторы в нужном формате
    recipient_rh = recipient_data['rh_D'] + recipient_data['rh_C'] + recipient_data['rh_E']
    donors_rh = [donor['rh_D'] + donor['rh_C'] + donor['rh_E'] for donor in donors_data]
    
    # Вычисляем итоговые комбинации
    final_rh_combinations = get_final_rh_combinations(recipient_rh, donors_rh)
    final_blood_groups = get_final_blood_group_compatibility(
        component,
        recipient_data['blood_group'], 
        [donor['blood_group'] for donor in donors_data]
    )
    
    # Формируем результат
    result_text = "✅ Подбор завершен для всех процедур!\n\n"
    result_text += f"**Компонент:** {component}\n"
    result_text += f"**Группа крови реципиента:** {recipient_data['blood_group']}\n"
    result_text += f"**Резус-фактор реципиента:** {recipient_rh}\n\n"
    
    result_text += "**Трансплантации:**\n"
    for i, donor in enumerate(donors_data, 1):
        result_text += f"ТКМ №{i}:\n"
        result_text += f"• Группа крови донора: {donor['blood_group']}\n"
        result_text += f"• Резус-фактор донора: {donor['rh_D']}{donor['rh_C']}{donor['rh_E']}\n\n"
    
    # Добавляем итоговую совместимость
    result_text += "**Итоговая совместимость:**\n\n"
    
    if component == blood:
        # Для эритроцитов
        blood_compatibility = format_blood_compatibility(component, final_blood_groups)
        rh_compatibility = "→ Возможная резус-принадлежность донора ЭСК:\n"
        for i, combo in enumerate(final_rh_combinations, 1):
            rh_compatibility += f"{i}. {combo}\n"
        
        result_text += f"Эритроциты:\n\n{blood_compatibility}\n{rh_compatibility}"
        
    elif component == platelets:
        # Для тромбоцитов с детализацией
        result_text += get_compatible_components_with_BMT(
            component, 
            recipient_data['blood_group'],
            donors_data[-1]['blood_group'],  # Для отображения вариантов берем последнего донора
            "", ""
        )
        
    elif component in [plasma, cryoprecipitate, granulocytes]:
        # Для других компонентов
        blood_compatibility = format_blood_compatibility(component, final_blood_groups)
        
        if component == plasma:
            result_text += f"Плазма\n{blood_compatibility}"
        elif component == cryoprecipitate:
            result_text += f"Криопреципитат\n{blood_compatibility}"
        elif component == granulocytes:
            result_text += f"Гранулоциты\n{blood_compatibility}"
    
    # Очищаем временные данные
    context.chat_data.pop('bmt_quantity', None)
    context.chat_data.pop('bmt_current_procedure', None)
    context.chat_data.pop('bmt_procedures_data', None)
    
    await update.message.reply_text(
        result_text,
        reply_markup=BMT_choice_keyboard,
        parse_mode="Markdown"
    )
    return ConversationHandler.END

def get_final_rh_combinations(recipient_rh, donors_rh_list):
    #Вычисляет итоговые комбинации резус-фактора через все процедуры ТКМ
    current_combinations = [recipient_rh]    
    for donor_rh in donors_rh_list:
        new_combinations = []        
        for current_rh in current_combinations:
            possible_combinations = get_rh_combinations_from_values_with_BTM(
                [current_rh[0:2], current_rh[2:4], current_rh[4:6]],  # D, C, E реципиента
                [donor_rh[0:2], donor_rh[2:4], donor_rh[4:6]]         # D, C, E донора
            )
            new_combinations.extend(possible_combinations)        
        current_combinations = list(set(new_combinations))    
    return current_combinations

async def handle_BMT_choice_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Начало ConversationHandler для пациентов с ТКМ
    context.chat_data['patient_type'] = 'with_bmt'
    await update.message.reply_text(
        "Для пациента с ТКМ в анамнезе выберите количество трансплантаций", 
        reply_markup=ReplyKeyboardRemove()
    )
    return BMT_QUANTITY

def get_final_blood_group_compatibility(component, recipient_blood_group, donors_blood_groups):
    #Вычисляет итоговую совместимость по группе крови через все процедуры ТКМ с учетом компонента
    current_compatibility = [recipient_blood_group]
    
    for donor_blood_group in donors_blood_groups:
        new_compatibility = []
        
        for current_bg in current_compatibility:
            # Определяем совместимость в зависимости от компонента
            if component == granulocytes:
                # Логика для гранулоцитов
                if donor_blood_group == blood_group_O \
                    or (current_bg in (blood_group_O, blood_group_A2, blood_group_B, blood_group_A2B) and donor_blood_group == blood_group_A)\
                    or donor_blood_group == blood_group_A2\
                    or (current_bg in (blood_group_O, blood_group_A, blood_group_A2) and donor_blood_group == blood_group_B)\
                    or (current_bg in (blood_group_O, blood_group_A2) and donor_blood_group == blood_group_AB)\
                    or (current_bg in (blood_group_O, blood_group_A, blood_group_A2) and donor_blood_group == blood_group_A2B)\
                    or current_bg == blood_group_unknown:
                    compatible_groups = [blood_group_O]
                elif current_bg == donor_blood_group == blood_group_A\
                    or (current_bg == blood_group_AB and donor_blood_group == blood_group_A)\
                    or (current_bg == blood_group_A and donor_blood_group == blood_group_AB):
                    compatible_groups = [blood_group_A, blood_group_O]
                elif (current_bg in (blood_group_AB, blood_group_A2B, blood_group_B) and donor_blood_group == blood_group_B)\
                    or (current_bg in (blood_group_B, blood_group_A2B) and donor_blood_group == blood_group_AB)\
                    or (current_bg in (blood_group_B, blood_group_AB, blood_group_A2B) and donor_blood_group == blood_group_A2B):
                    compatible_groups = [blood_group_B, blood_group_O]
                elif current_bg == donor_blood_group == blood_group_AB:
                    compatible_groups = [blood_group_O, blood_group_A, blood_group_B, blood_group_AB]
                else:
                    compatible_groups = [blood_group_O]
                    
            elif component == platelets:
                # Логика для тромбоцитов
                if current_bg == donor_blood_group == blood_group_O:
                    compatible_groups = [blood_group_O]
                elif current_bg in (blood_group_A, blood_group_A2) and donor_blood_group == blood_group_O\
                    or current_bg in (blood_group_O, blood_group_A, blood_group_A2) and donor_blood_group in (blood_group_A, blood_group_A2):
                    compatible_groups = [blood_group_A, blood_group_O]
                elif current_bg in (blood_group_B, blood_group_A2B) and donor_blood_group in (blood_group_O, blood_group_B)\
                    or current_bg == blood_group_O and donor_blood_group in (blood_group_B, blood_group_A2B):
                    compatible_groups = [blood_group_B, blood_group_O]
                elif current_bg == blood_group_AB and donor_blood_group in (blood_group_O, blood_group_AB):
                    compatible_groups = [blood_group_AB, blood_group_O]
                else:
                    compatible_groups = [blood_group_O]
                    
            elif component == plasma:
                # Логика для плазмы
                if current_bg == donor_blood_group == blood_group_O:
                    compatible_groups = [blood_group_O, blood_group_A, blood_group_B, blood_group_AB]
                elif current_bg in (blood_group_O, blood_group_A, blood_group_A2) and donor_blood_group in (blood_group_O, blood_group_A, blood_group_A2):
                    compatible_groups = [blood_group_A, blood_group_AB]
                elif current_bg in (blood_group_O, blood_group_B, blood_group_A2) and donor_blood_group == blood_group_B:
                    compatible_groups = [blood_group_B, blood_group_AB]
                else:
                    compatible_groups = [blood_group_AB]
                    
            elif component == cryoprecipitate:
                # Для криопреципитата всегда все группы
                compatible_groups = [blood_group_O, blood_group_A, blood_group_B, blood_group_AB]
                
            elif component == blood:
                # Логика для эритроцитов
                if donor_blood_group in (blood_group_A2, blood_group_unknown, blood_group_O) \
                    or current_bg in (blood_group_O, blood_group_A2, blood_group_B, blood_group_A2B) and donor_blood_group == blood_group_A\
                    or current_bg in (blood_group_O, blood_group_A, blood_group_A2) and donor_blood_group == blood_group_B\
                    or current_bg in (blood_group_O, blood_group_A2) and donor_blood_group == blood_group_AB\
                    or current_bg in (blood_group_O, blood_group_A, blood_group_A2) and donor_blood_group == blood_group_A2B\
                    or current_bg == blood_group_unknown:
                    compatible_groups = [blood_group_O]
                elif current_bg in (blood_group_A, blood_group_AB) and donor_blood_group == blood_group_A\
                    or current_bg == blood_group_A and donor_blood_group == blood_group_AB:
                    compatible_groups = [blood_group_A, blood_group_O]
                elif current_bg in (blood_group_B, blood_group_AB, blood_group_A2B) and donor_blood_group == blood_group_B\
                    or current_bg in (blood_group_B, blood_group_A2B) and donor_blood_group == blood_group_AB\
                    or current_bg in (blood_group_A2B, blood_group_AB, blood_group_B) and donor_blood_group == blood_group_A2B:
                    compatible_groups = [blood_group_B, blood_group_O]
                elif current_bg == donor_blood_group == blood_group_AB:
                    compatible_groups = [blood_group_O, blood_group_A, blood_group_B, blood_group_AB]
                else:
                    compatible_groups = [blood_group_O]
            else:
                compatible_groups = [blood_group_O]
            
            new_compatibility.extend(compatible_groups)
        
        # Убираем дубликаты и оставляем только уникальные группы
        current_compatibility = list(set(new_compatibility))
    
    return current_compatibility

async def handle_BMT_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quantity_text = update.message.text
    
    try:
        quantity = int(quantity_text)
        if quantity < 0:
            await update.message.reply_text(
                "Пожалуйста, введите положительное количество трансплантаций", 
                reply_markup=ReplyKeyboardRemove()
            )
            return BMT_QUANTITY
        elif quantity == 0:
            await update.message.reply_text(
                "В анамнезе данного пациента не было ТКМ, пожалуйста, сделайте правильный выбор", 
                reply_markup=BMT_choice_keyboard
            )
            return ConversationHandler.END
        elif quantity == 1:
            await update.message.reply_text("Выберите компонент крови:", reply_markup=components_keyboard)
            return BMT_CHOICE
        else:
            context.chat_data['bmt_quantity'] = quantity
            context.chat_data['bmt_current_procedure'] = 0
            context.chat_data['bmt_procedures_data'] = []
            
            await update.message.reply_text(
                f"Будет введено данных для {quantity} трансплантаций. "
                f"Начнем с процедуры №1. Выберите компонент крови:",
                reply_markup=components_keyboard
            )
            return BMT_CHOICE
            
    except ValueError:
        await update.message.reply_text(
            "Пожалуйста, введите число",
            reply_markup=ReplyKeyboardRemove()
        )
        return BMT_QUANTITY

"""async def handle_BMT_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Обработчик главного меню
    context.chat_data['status'] = update.message.text
    if update.message.text == BMT_in_past:
        await update.message.reply_text("Выберите компонент крови:", reply_markup=components_keyboard)
    else:
        await update.message.reply_text("Эта часть еще в разработке", reply_markup=BMT_choice_keyboard)"""

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
              f"• Компонент: {component}\n\n"\
              "Параметры пациента:\n"\
              f"• Группа крови: {context.chat_data['recipient_blood_group']}\n"\
              "Параметры донора КМ или ГСК:\n"\
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
    donor_rh_factor_E = update.message.text
    context.chat_data['donor_rh_E'] = donor_rh_factor_E
    
    # Проверяем, множественные ли ТКМ
    if context.chat_data.get('bmt_quantity', 1) > 1:
        return await handle_bmt_procedure_cycle(update, context, None)
    else:
        # Одиночная процедура - стандартная логика
        component = context.chat_data['component']
        donor_blood_group = context.chat_data['donor_blood_group']
        recipient_blood_group = context.chat_data['recipient_blood_group']
        rh_factor_common = [
            context.chat_data['recipient_rh_D'], 
            context.chat_data['recipient_rh_C'], 
            context.chat_data['recipient_rh_E']
        ]
        donor_rh_factor_common = [
            context.chat_data['donor_rh_D'], 
            context.chat_data['donor_rh_C'], 
            donor_rh_factor_E
        ]
        
        result_text = "✅ Подбор завершен!\n\n"\
            f"• Группа крови реципиента: {recipient_blood_group}\n"\
            f"• Резус-фактор реципиента: {context.chat_data['recipient_rh_D']}{context.chat_data['recipient_rh_C']}{context.chat_data['recipient_rh_E']}\n\n"\
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