from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from elements import *

components_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton(blood), KeyboardButton(platelets)],
    [KeyboardButton(plasma), KeyboardButton(cryoprecipitate)], [KeyboardButton(granulocytes)]
], resize_keyboard=True, one_time_keyboard=True)

#Выбор группы крови
blood_group_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton(blood_group_O), KeyboardButton(blood_group_A), KeyboardButton(blood_group_A2)],
    [KeyboardButton(blood_group_B), KeyboardButton(blood_group_AB), KeyboardButton(blood_group_A2B)],
    [KeyboardButton(blood_group_unknown), KeyboardButton(back)]
], resize_keyboard=True, one_time_keyboard=True)

#Выбор резус-фактора
rh_keyboard_D = ReplyKeyboardMarkup([
    [KeyboardButton(rh_D), KeyboardButton(rh_dd), KeyboardButton(rh_D_weak), KeyboardButton(rh_D_partial), KeyboardButton(rh_D_unknown)], 
    [KeyboardButton(back)]
], resize_keyboard=True, one_time_keyboard=True)

rh_keyboard_C = ReplyKeyboardMarkup([
    [KeyboardButton(rh_CC), KeyboardButton(rh_Cc), KeyboardButton(rh_cc), KeyboardButton(rh_C_unknown)], 
    [KeyboardButton(back)]
], resize_keyboard=True, one_time_keyboard=True)

rh_keyboard_E = ReplyKeyboardMarkup([
    [KeyboardButton(rh_EE), KeyboardButton(rh_Ee), KeyboardButton(rh_ee), KeyboardButton(rh_E_unknown)],
    [KeyboardButton(back)]
], resize_keyboard=True, one_time_keyboard=True)

BMT_choice_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton(clear_patient), KeyboardButton(BMT_in_past)],
        [KeyboardButton(with_HDN), KeyboardButton(chimera)]
    ], resize_keyboard=True, one_time_keyboard=True
)

#клавиатуры для химеры
rh_keyboard_D_chimera = ReplyKeyboardMarkup([
    [KeyboardButton(rh_D), KeyboardButton(rh_dd), KeyboardButton(rh_D_weak), KeyboardButton(rh_D_partial)], 
    [KeyboardButton(back)]
], resize_keyboard=True, one_time_keyboard=True)

rh_keyboard_C_chimera = ReplyKeyboardMarkup([
    [KeyboardButton(rh_CC), KeyboardButton(rh_Cc), KeyboardButton(rh_cc)], 
    [KeyboardButton(back)]
], resize_keyboard=True, one_time_keyboard=True)

rh_keyboard_E_chimera = ReplyKeyboardMarkup([
    [KeyboardButton(rh_EE), KeyboardButton(rh_Ee), KeyboardButton(rh_ee)],
    [KeyboardButton(back)]
], resize_keyboard=True, one_time_keyboard=True)

def get_chimera_keyboard(rh_factor, recipient_element):
    # Функция подбора клавиатуры при химере
    if rh_factor == "group":
        possible_groups = [blood_group_O, blood_group_A, blood_group_A2, blood_group_B, blood_group_AB, blood_group_A2B]
        possible_groups.remove(recipient_element)
        blood_group_keyboard_chimera = ReplyKeyboardMarkup([
                    [KeyboardButton(possible_groups[0]), KeyboardButton(possible_groups[1]), KeyboardButton(possible_groups[2])],
                    [KeyboardButton(possible_groups[3]), KeyboardButton(possible_groups[4]), KeyboardButton(back)]
                ], resize_keyboard=True, one_time_keyboard=True)
        return blood_group_keyboard_chimera
    if rh_factor == "D":
        possible_factors = [rh_D, rh_dd, rh_D_weak, rh_D_partial]
        possible_factors.remove(recipient_element)
        rh_keyboard_chimera_D = ReplyKeyboardMarkup([
                    [KeyboardButton(possible_factors[0]), KeyboardButton(possible_factors[1]), KeyboardButton(possible_factors[2])], 
                    [KeyboardButton(back)]
                ], resize_keyboard=True, one_time_keyboard=True)
        return rh_keyboard_chimera_D
    if rh_factor == "E":
        possible_factors = [rh_EE, rh_ee, rh_Ee]
        possible_factors.remove(recipient_element)
        rh_keyboard_chimera_E = ReplyKeyboardMarkup([
                    [KeyboardButton(possible_factors[0]), KeyboardButton(possible_factors[1])], 
                    [KeyboardButton(back)]
                ], resize_keyboard=True, one_time_keyboard=True)
        return rh_keyboard_chimera_E
    if rh_factor == "C":
        possible_factors = [rh_CC, rh_Cc, rh_cc]
        possible_factors.remove(recipient_element)
        rh_keyboard_chimera_C = ReplyKeyboardMarkup([
                    [KeyboardButton(possible_factors[0]), KeyboardButton(possible_factors[1])], 
                    [KeyboardButton(back)]
                ], resize_keyboard=True, one_time_keyboard=True)
        return rh_keyboard_chimera_C
