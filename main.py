import logging
from typing import Dict
import re
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

MAIN_MENU, MANAGE_ADS,FREE_AD, NEW_AD, CHOOSE_CATEGORY, CHOOSE_UNIVERSITY, BACK_TO__MENU,CHOOSE_LOCATION,TEXT, ID, PAYMENT = range(11)

GREETING_MESSAGE = "سلام"+"\n"+"به ربات خوش آمدید"
POLICY_MESSAGE = "لطفا ابتدا قوانین را بخوانید"

main_keyboard = [
    ['مدیریت آگهی ها 🗄', 'ثبت آگهی جدید 📋'],
    ['ثبت آگهی رایگان 🆓'],
]
categories = [
    ["انجام دهنده", "درخواست کننده"],
    ["خریدار", "فروشنده"],
    ["فرصت شغلی"],
]

universities = [
    ["تهران", " شهید بهشتی"],
    ["علم و صنعت", "شریف"],
    ["دیگر"],
]

user_ads = [
    ['بازگشت به منو'],
]


main_menu_markup = ReplyKeyboardMarkup(main_keyboard,resize_keyboard=True)
user_ads_markup = ReplyKeyboardMarkup(user_ads,resize_keyboard=True)
categories_markup = ReplyKeyboardMarkup(categories,resize_keyboard=True)
universities_markup = ReplyKeyboardMarkup(universities,resize_keyboard=True)
# def facts_to_str(user_data: Dict[str, str]) -> str:
#     facts = list()

#     for key, value in user_data.items():
#         facts.append(f'{key} - {value}')

#     return "\n".join(facts).join(['\n', '\n'])


def start(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        GREETING_MESSAGE,
        reply_markup=main_menu_markup,
    )

    return MAIN_MENU

def back_to_main_menu(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        "منو اصلی",
        reply_markup=main_menu_markup,
    )

    return MAIN_MENU
    

def main_menu_fn(update: Update, context: CallbackContext) -> int:
    message = update.message.text   
    if message == main_keyboard[0][0]:
        update.message.reply_text(
            "شما آگهی ثبت شده ای ندارید",
            reply_markup=user_ads_markup
        )
        return MANAGE_ADS
    elif message == main_keyboard[0][1]:
        update.message.reply_text(
            POLICY_MESSAGE,
        )
        update.message.reply_text(
            "لطفا نوع آگهی خود را از بین 5 مورد زیر انتخاب کنید",
            # TODO add new button list for this
            reply_markup=categories_markup
        )
        
        return CHOOSE_CATEGORY
    elif message == main_keyboard[1][0]:
        update.message.reply_text(
            "با استفاده از لینک زیر دوستاتو دعوت کن و جایزه بگیر",
            # TODO add new button list for this
            reply_markup=user_ads_markup
        )
        
        return FREE_AD

def manage_ads_fn(undate:Update,context:CallbackContext) -> int:
    update.message.reply_text(
        "لیست آگهی های شما:",
    )
    # TODO change this to FOLLOW_AD stat
    return MAIN_MENU

def choose_category_fn(update: Update,context:CallbackContext) -> int:
    message = update.message.text
    context.user_data['category'] = message.replace(' ','_')
    update.message.reply_text(
        "لطفا دانشگاه خود را انتخاب کنید و یا اسم دانشگاه خود را تایپ کنید",
        reply_markup=universities_markup
    )
    return CHOOSE_UNIVERSITY

def choose_university_fn(update: Update,context:CallbackContext) -> int:
    message = update.message.text
    context.user_data['university'] = message.replace(' ','_')
    update.message.reply_text(
        "متنی آگهیت رو بفرست",
        reply_markup=user_ads_markup
    )
    return TEXT

def choose_text_fn(update: Update,context:CallbackContext) -> int:
    message = update.message.text
    context.user_data['text'] = message
    update.message.reply_text(
        "آیدی ای که میخوای تو آگهیت درج بشه رو بفرست",
        reply_markup=user_ads_markup
    )
    return ID

def choose_id_fn(update: Update,context:CallbackContext) -> int:
    message = update.message.text
    if not bool(re.match(r"^@[A-Za-z0-9_.]{3,}", message)):
        update.message.reply_text(
            "آی دی باید با @ شروع و بیشتر از 3 کاراکتر انگلیسی باشد",
            reply_markup=user_ads_markup
        )
        return ID
    else:
        context.user_data['id'] = message
        final_message = "#"+context.user_data['category']+"\n"+"#"+context.user_data['university']+"\n"+ context.user_data['text']+"\n"+context.user_data['id']
        update.message.reply_text(
            "متن نهایی آگهی شما به صورت زیر نمایش داده خواهد شد: \n"+ final_message,
            reply_markup=user_ads_markup
        )

        
def regular_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(f'Your {text.lower()}? Yes, I would love to hear about that!')

#     return TYPING_REPLY


# def custom_choice(update: Update, _: CallbackContext) -> int:
#     update.message.reply_text(
#         'Alright, please send me the category first, for example "Most impressive skill"'
#     )

#     return TYPING_CHOICE


# def received_information(update: Update, context: CallbackContext) -> int:
#     user_data = context.user_data
#     text = update.message.text
#     category = user_data['choice']
#     user_data[category] = text
#     del user_data['choice']

#     update.message.reply_text(
#         "Neat! Just so you know, this is what you already told me:"
#         f"{facts_to_str(user_data)} You can tell me more, or change your opinion"
#         " on something.",
#         reply_markup=markup,
#     )

#     return CHOOSING



def done(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text(
        f"I learned these facts about you: {facts_to_str(user_data)}Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater("453030525:AAFlLIRaMcFhZcKqZPKM-D52hl3B_10R5YE")
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                MessageHandler(
                    Filters.regex('^(مدیریت آگهی ها 🗄|ثبت آگهی جدید 📋|ثبت آگهی رایگان 🆓)$'), main_menu_fn
                ),
            ],
            MANAGE_ADS: [
                MessageHandler(
                    Filters.regex('^$'), manage_ads_fn
                ),
                # MessageHandler(Filters.regex('^Something else...$'), custom_choice),
            ],    
            CHOOSE_CATEGORY: [
                MessageHandler(
                    Filters.regex('^(خریدار|فروشند|انجام کار|درخواست کار|فرصت شغلی)$') , choose_category_fn
                ),
                # MessageHandler(Filters.regex('^Something else...$'), custom_choice),
            ],
            CHOOSE_UNIVERSITY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('#فوری')) , choose_university_fn
                ),
                # MessageHandler(Filters.regex('^Something else...$'), custom_choice),
            ],
            TEXT: [
                MessageHandler(
                    Filters.text , choose_text_fn
                ),
                # MessageHandler(Filters.regex('^Something else...$'), custom_choice),
            ],
            ID: [
                MessageHandler(
                    Filters.text , choose_id_fn
                ),
                # MessageHandler(Filters.regex('^Something else...$'), custom_choice),
            ],
            # TYPING_CHOICE: [
            #     MessageHandler(
            #         Filters.text & ~(Filters.command | Filters.regex('^Done$')), regular_choice
            #     )
            # ],
            # TYPING_REPLY: [
            #     MessageHandler(
            #         Filters.text & ~(Filters.command | Filters.regex('^Done$')),
            #         received_information,
            #     )
            # ],
        },
        fallbacks=[MessageHandler(Filters.regex('^بازگشت به منو$'), back_to_main_menu)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()