from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from config import BOT_TOKEN
from keyboards import BMT_choice_keyboard
from simple_handlers import *
from BMT_handlers import *
from HDN_handlers import *
from chimera_handlers import *
from elements import *

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
👋 Добро пожаловать в бот для подбора компонентов крови!

Выберите тип пациента:
    """
    await update.message.reply_text(welcome_text, reply_markup=BMT_choice_keyboard)
    # Очищаем данные при старте
    context.chat_data.clear()

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ConversationHandler для пациентов с ТКМ
    bmt_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Text([BMT_in_past]), handle_BMT_choice_start)
        ],
        states={
            BMT_CHOICE: [
                MessageHandler(filters.Text([
                    blood, platelets, plasma, cryoprecipitate, granulocytes
                ]), handle_component_with_BMT)
            ],
            RECIPIENT_BLOOD_GROUP: [
                MessageHandler(filters.Text([
                    blood_group_A, blood_group_A2, blood_group_B, blood_group_AB, 
                    blood_group_A2B, blood_group_O, blood_group_unknown
                ]), handle_recipient_blood_group_with_BMT)
            ],
            RECIPIENT_RH_FACTOR: [
                MessageHandler(filters.Text([
                    rh_D, rh_dd, rh_D_weak, rh_D_partial, rh_D_unknown
                ]), handle_recipient_rh_factor_D_with_BMT),
                MessageHandler(filters.Text([
                    rh_CC, rh_Cc, rh_cc, rh_C_unknown
                ]), handle_recipient_rh_factor_C_with_BMT),
                MessageHandler(filters.Text([
                    rh_EE, rh_Ee, rh_ee, rh_E_unknown
                ]), handle_recipient_rh_factor_E_with_BMT)
            ],
            DONOR_BLOOD_GROUP: [
                MessageHandler(filters.Text([
                    blood_group_A, blood_group_A2, blood_group_B, blood_group_AB, 
                    blood_group_A2B, blood_group_O, blood_group_unknown
                ]), handle_donor_blood_group_with_BMT)
            ],
            DONOR_RH_FACTOR: [
                MessageHandler(filters.Text([
                    rh_D, rh_dd, rh_D_weak, rh_D_partial, rh_D_unknown
                ]), handle_donor_rh_factor_D_with_BMT),
                MessageHandler(filters.Text([
                    rh_CC, rh_Cc, rh_cc, rh_C_unknown
                ]), handle_donor_rh_factor_C_with_BMT),
                MessageHandler(filters.Text([
                    rh_EE, rh_Ee, rh_ee, rh_E_unknown
                ]), handle_donor_rh_factor_E_with_BMT)
            ],        
        },
        fallbacks=[
            CommandHandler("start", start),
            MessageHandler(filters.Text([back]), start)
        ]
    )
    
    hdn_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Text([with_HDN]), handle_HDN_choice_start)
        ],
        states={
            HDN_CHOICE: [
                MessageHandler(filters.Text([
                    blood, platelets, plasma, cryoprecipitate, granulocytes
                ]), handle_component_with_HDN)
            ],
            HDN_RECIPIENT_BLOOD_GROUP: [
                MessageHandler(filters.Text([
                    blood_group_A, blood_group_A2, blood_group_B, blood_group_AB, 
                    blood_group_A2B, blood_group_O, blood_group_unknown
                ]), handle_recipient_blood_group_with_HDN)
            ],
            HDN_RECIPIENT_RH_FACTOR: [
                MessageHandler(filters.Text([
                    rh_D, rh_dd, rh_D_weak, rh_D_partial, rh_D_unknown
                ]), handle_recipient_rh_factor_D_with_HDN),
                MessageHandler(filters.Text([
                    rh_CC, rh_Cc, rh_cc, rh_C_unknown
                ]), handle_recipient_rh_factor_C_with_HDN),
                MessageHandler(filters.Text([
                    rh_EE, rh_Ee, rh_ee, rh_E_unknown
                ]), handle_recipient_rh_factor_E_with_HDN)
            ],
            HDN_MOTHER_BLOOD_GROUP: [
                MessageHandler(filters.Text([
                    blood_group_A, blood_group_A2, blood_group_B, blood_group_AB, 
                    blood_group_A2B, blood_group_O, blood_group_unknown
                ]), handle_mother_blood_group_with_HDN)
            ],
            HDN_MOTHER_RH_FACTOR: [
                MessageHandler(filters.Text([
                    rh_D, rh_dd, rh_D_weak, rh_D_partial, rh_D_unknown
                ]), handle_mother_rh_factor_d_with_HDN),
                MessageHandler(filters.Text([
                    rh_CC, rh_Cc, rh_cc, rh_C_unknown
                ]), handle_mother_rh_factor_c_with_HDN),
                MessageHandler(filters.Text([
                    rh_EE, rh_Ee, rh_ee, rh_E_unknown
                ]), handle_mother_rh_factor_e_with_HDN)
            ],        
        },
        fallbacks=[
            CommandHandler("start", start),
            MessageHandler(filters.Text([back]), start)
        ]
    )

    chimera_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Text([chimera]), handle_chimera_choice_start)
        ],
        states={
            CHIMERA_CHOICE: [
                MessageHandler(filters.Text([
                    blood, platelets, plasma, cryoprecipitate, granulocytes
                ]), handle_component_chimera)
            ],
            CHIMERA_RECIPIENT_BLOOD_GROUP: [
                MessageHandler(filters.Text([
                    blood_group_A, blood_group_A2, blood_group_B, blood_group_AB, 
                    blood_group_A2B, blood_group_O, blood_group_unknown
                ]), handle_chimera_recipient_blood_group)
            ],
            CHIMERA_RECIPIENT_RH_FACTOR: [
                MessageHandler(filters.Text([
                    rh_D, rh_dd, rh_D_weak, rh_D_partial, rh_D_unknown
                ]), handle_chimera_recipient_rh_factor_D),
                MessageHandler(filters.Text([
                    rh_CC, rh_Cc, rh_cc, rh_C_unknown
                ]), handle_chimera_recipient_rh_factor_C),
                MessageHandler(filters.Text([
                    rh_EE, rh_Ee, rh_ee, rh_E_unknown
                ]), handle_chimera_recipient_rh_factor_E)
            ],
            CHIMERA_BLOOD_GROUP: [
                MessageHandler(filters.Text([
                    blood_group_A, blood_group_A2, blood_group_B, blood_group_AB, 
                    blood_group_A2B, blood_group_O, blood_group_unknown
                ]), handle_chimera_blood_group)
            ],
            CHIMERA_RH_FACTOR: [
                MessageHandler(filters.Text([
                    rh_D, rh_dd, rh_D_weak, rh_D_partial, rh_D_unknown
                ]), handle_chimera_rh_factor_d),
                MessageHandler(filters.Text([
                    rh_CC, rh_Cc, rh_cc, rh_C_unknown
                ]), handle_chimera_rh_factor_c),
                MessageHandler(filters.Text([
                    rh_EE, rh_Ee, rh_ee, rh_E_unknown
                ]), handle_chimera_rh_factor_e)
            ],        
        },
        fallbacks=[
            CommandHandler("start", start),
            MessageHandler(filters.Text([back]), start)
        ]
    )
    # Обработчики
    application.add_handler(CommandHandler("start", start))
    
    # Обработчики для обычных пациентов (без ТКМ)
    application.add_handler(MessageHandler(filters.Text([clear_patient]), handle_regular_patient_choice))
    
    # ConversationHandler для пациентов с ТКМ
    application.add_handler(bmt_conv_handler)

    # ConversationHandler для пациентов с ГБН
    application.add_handler(hdn_conv_handler)

    # ConversationHandler для пациентов с химерой
    application.add_handler(chimera_conv_handler)
    
    # Обработчики компонентов для обычных пациентов
    application.add_handler(MessageHandler(filters.Text([
        blood, platelets, plasma, cryoprecipitate, granulocytes
    ]), handle_component))
    
    # Обработчики группы крови для обычных пациентов
    application.add_handler(MessageHandler(filters.Text([
        blood_group_A, blood_group_A2, blood_group_B, blood_group_AB, 
        blood_group_A2B, blood_group_O, blood_group_unknown
    ]), handle_blood_group))
    
    # Обработчики резус-факторов
    application.add_handler(MessageHandler(filters.Text([
        rh_D, rh_dd, rh_D_weak, rh_D_partial, rh_D_unknown
    ]), handle_rh_factor_D))
    application.add_handler(MessageHandler(filters.Text([
        rh_CC, rh_Cc, rh_cc, rh_C_unknown
    ]), handle_rh_factor_C))
    application.add_handler(MessageHandler(filters.Text([
        rh_EE, rh_Ee, rh_ee, rh_E_unknown
    ]), handle_rh_factor_E))
    
    application.add_handler(MessageHandler(filters.ALL, handle_unknown))
    
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()