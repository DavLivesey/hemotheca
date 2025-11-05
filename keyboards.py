from telegram import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("🟥 Кровь + ЭСК"), KeyboardButton("🟨 Тромбоциты")],
    [KeyboardButton("🟪 Плазма"), KeyboardButton("❄️ Криопреципитат")], [KeyboardButton("🛡️ Гранулоциты")]
], resize_keyboard=True, one_time_keyboard=True)

# Второй уровень - подкатегории тромбоцитов
platelets_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("🟨 Из цельной крови"), KeyboardButton("🟦 Аферез в плазме")],
    [KeyboardButton("🟩 Аферез в растворе"), KeyboardButton("🔙 Назад")]
], resize_keyboard=True, one_time_keyboard=True)

# Второй уровень - подкатегории плазмы
plasma_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("🟪 Стандартная"), KeyboardButton("🟫 Плазма аферез")],
    [KeyboardButton("🔙 Назад")]
], resize_keyboard=True, one_time_keyboard=True)

#Выбор группы крови
blood_group_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("🅰️ Группа крови А"), KeyboardButton("🅱️ Группа крови Б")],
    [KeyboardButton("🆎 Группа крови АБ"), KeyboardButton("🅾️ Группа крови О")]
], resize_keyboard=True, one_time_keyboard=True)

#Выбор резус-фактора
rh_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("➕ Резус-положительный"), KeyboardButton("➖ Резус-отрицательный")]
], resize_keyboard=True, one_time_keyboard=True)