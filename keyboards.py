from telegram import ReplyKeyboardMarkup, KeyboardButton
from elements import *

main_keyboard = ReplyKeyboardMarkup([
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