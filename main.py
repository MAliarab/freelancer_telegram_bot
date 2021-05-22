import logging
from typing import Dict, Text
import re
from datetime import datetime, timedelta
import requests
import mysql.connector
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup, chat
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Initialize states
JOIN, MAIN_MENU, MANAGE_ADS,FREE_AD, NEW_AD, CHOOSE_CATEGORY, \
     CHOOSE_UNIVERSITY, BACK_TO__MENU,CHOOSE_LOCATION,TEXT, ID, PAYMENT, SHOW_ADS, PAYED, EDIT = range(15)

# Channel and Bot information
CHANNEL_ID = "@tempchann"
SUPPORT_ID = "@dashtab"
# Static messages
GREETING_MESSAGE = "سلام"+"\n"+"به ربات خوش آمدید"
POLICY_MESSAGE = "لطفا ابتدا قوانین را بخوانید"

# Keyboard and matkup definitions 

# Keyboard
join_channel = [
    [
        InlineKeyboardButton("عضویت در کانال",url="https://t.me/tempchann"),
        InlineKeyboardButton("عضو شدم", callback_data='joined'),
    ],
]

main_keyboard = [
    ['مدیریت آگهی ها 🗄', 'ثبت آگهی جدید 📋'],
    ['ثبت آگهی رایگان 🆓'],
    ['دیدن آگهی ها']
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

show_ads_kb = [
    [
        InlineKeyboardButton("آگهی های ۱ روز اخیر", callback_data=1),
        InlineKeyboardButton("آگهی های ۲ روز اخیر", callback_data=2),
    ],
    [InlineKeyboardButton("تمام آگهی ها", callback_data=5),]
]
# Markup
main_menu_markup = ReplyKeyboardMarkup(main_keyboard,resize_keyboard=True)
user_ads_markup = ReplyKeyboardMarkup(user_ads,resize_keyboard=True)
categories_markup = ReplyKeyboardMarkup(categories,resize_keyboard=True)
universities_markup = ReplyKeyboardMarkup(universities,resize_keyboard=True)
join_channel_markup = InlineKeyboardMarkup(join_channel)
show_ads_markup = InlineKeyboardMarkup(show_ads_kb)

# Database settings
mydb = mysql.connector.connect(
    database='karbotdb',
    host="localhost",
    user="karbotadmin",
    password="458025166"
)
cursor = mydb.cursor()


def start(update: Update, context: CallbackContext) -> int:
    # TODO set invitation coin for user
    # print(update.message.text.split(' ')[1])
    # print(type(update.message.text.split(' ')[1]))
    # ---------------------------------


    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    
    # Add user to DB if there is not in DB
    q1 = "SELECT * FROM users WHERE id={}".format(user_id)
    cursor.execute(q1)
    user = cursor.fetchall()
    if len(user) == 0:
        q2 = ("INSERT INTO users (id,coin,chat_id) VALUES (%s,%s,%s)")
        values = (user_id,0,chat_id)
        cursor.execute(q2,values)
        mydb.commit()
    
    result = context.bot.get_chat_member(chat_id=CHANNEL_ID,user_id=user_id)
    
    if result['status'] != "member" and result['status'] != 'creator':

        update.message.reply_text(
            'ابتدا در کانال عضو شوید',
            reply_markup=join_channel_markup
            )

        return JOIN
    else:
        update.message.reply_text(
            GREETING_MESSAGE,
            reply_markup=main_menu_markup,
        )
    
        return MAIN_MENU

def join_channel_fn(update: Update, context: CallbackContext) -> int:

    if update.message != None:
        user_id = update.message.from_user.id
        result = context.bot.get_chat_member(chat_id=CHANNEL_ID,user_id=user_id)

        if result['status'] != "member" and result['status'] != 'creator':

            update.message.reply_text(
                'ابتدا در کانال عضو شوید',
                reply_markup=join_channel_markup
                )

            return JOIN

    query = update.callback_query
    user_id = query.from_user.id
    if query.data == 'joined':
        result = context.bot.get_chat_member(chat_id=CHANNEL_ID,user_id=user_id)
        if result['status'] != "member" and result['status'] != 'creator':
            res = context.bot.answer_callback_query(query.id, "هنوز عضو کانال نشده اید", show_alert=True)
        else:
            query.message.reply_text(
                GREETING_MESSAGE,
                reply_markup=main_menu_markup,
            )
        
            return MAIN_MENU
    else:
        query.message.reply_text(
            'ابتدا در کانال عضو شوید',
            reply_markup=join_channel_markup
            )

        return JOIN    

def back_to_main_menu(update: Update, context: CallbackContext) -> int:

    user_id = update.message.from_user.id
    result = context.bot.get_chat_member(chat_id=CHANNEL_ID,user_id=user_id)

    if result['status'] != "member" and result['status'] != 'creator':

        update.message.reply_text(
            'ابتدا در کانال عضو شوید',
            reply_markup=join_channel_markup
            )

        return JOIN

    update.message.reply_text(
        "منو",
        reply_markup=main_menu_markup,
    )

    return MAIN_MENU
    

def main_menu_fn(update: Update, context: CallbackContext) -> int:

    user_id = update.message.from_user.id
    result = context.bot.get_chat_member(chat_id=CHANNEL_ID,user_id=user_id)

    if result['status'] != "member" and result['status'] != 'creator':

        update.message.reply_text(
            'ابتدا در کانال عضو شوید',
            reply_markup=join_channel_markup
            )

        return JOIN

    message = update.message.text   
    if message == main_keyboard[2][0]:
        update.message.reply_text(
            "تعداد آگهی هایی که میخواهید نمایش داده شود را انتخاب کنید",
            reply_markup=show_ads_markup
        )
        return SHOW_ADS

    elif message == main_keyboard[0][0]:
        print("heyyyy")
        # q = "SELECT id, full_text FROM posts WHERE user_id = '{} AND active_flag={}' ORDER BY id DESC".format(user_id,1)
        q = "SELECT id, full_text FROM posts where user_id={} and active_flag={} ORDER BY id DESC".format(user_id,1)
        cursor.execute(q)
        posts = cursor.fetchall()
        posts_keyboard = [['بازگشت به منو']]
        for post in posts:
            posts_keyboard.append([str(post[0])+"|"+post[1]])
        
        if len(posts) == 0:
            update.message.reply_text(
                "شما آگهی ثبت شده ای ندارید",
                reply_markup=main_menu_markup
            )
            return MAIN_MENU
        else:
            posts_markup = ReplyKeyboardMarkup(posts_keyboard,resize_keyboard=True)
            update.message.reply_text(
                "لیست آگهی های شما",
                reply_markup=posts_markup
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

def show_ads_fn(update: Update,context:CallbackContext) -> int:

    query = update.callback_query
    
    date = datetime.now()-timedelta(days=int(query.data))
    
    q = "SELECT full_text from posts WHERE created_at >= '{}'".format(date)

    cursor.execute(q)

    posts = cursor.fetchall()
    query.message.reply_text(
        "لیست آگهی ها:",
        reply_markup=user_ads_markup
    )
    for post in posts:
        query.message.reply_text(
            post[0]
            
        )
    return SHOW_ADS


def manage_ads_fn(update: Update,context:CallbackContext) -> int:
    user_id = update.message.from_user.id
    result = context.bot.get_chat_member(chat_id=CHANNEL_ID,user_id=user_id)
    post_id = int(update.message.text.split('|')[0])
    
    if result['status'] != "member" and result['status'] != 'creator':

        update.message.reply_text(
            'ابتدا در کانال عضو شوید',
            reply_markup=join_channel_markup
            )

        return JOIN
    q = "SELECT * FROM posts WHERE id={}".format(post_id)
    cursor.execute(q)
    post_obj = cursor.fetchone()
    if post_obj==None:
        update.message.reply_text(
            'آگهی یافت نشد'
        )
    
    else:
        print(post_obj[8])
        if post_obj[8]==PAYMENT:

            update.message.reply_text(
                "در حال بررسی وضعیت آگهی ..."
            )
            
            response = requests.post(
                "https://gateway.zibal.ir/v1/request",
                json={'merchant':'zibal','amount':100000,'callbackUrl':"https://aversi.ir/verify"}
                )
            if response.json()['result']==100:
                context.user_data['trackId'] = response.json()['trackId']
                payment_kb = [
                    [
                        InlineKeyboardButton("پرداخت بانکی",url="https://gateway.zibal.ir/start/{}".format(response.json()['trackId'])),
                        InlineKeyboardButton("پرداخت با امتیاز", callback_data='freepay'),
                    ],
                    [InlineKeyboardButton("پرداخت کردم", callback_data='payed'),]
                ]

                payment_kb_markup = InlineKeyboardMarkup(payment_kb)

                update.message.reply_text(
                    "متن نهایی آگهی شما به صورت زیر نمایش داده خواهد شد: \n"+ post_obj[1],
                    reply_markup=payment_kb_markup
                )

                context.user_data['final_message'] = post_obj[1]
                context.user_data['post_id'] = post_id

                return PAYMENT
        elif post_obj[8]==PAYED:
            edit_kb = [
                [
                    InlineKeyboardButton("آگهی واگذار شد",callback_data="assigned|"+str(post_id)),
                    InlineKeyboardButton("حذف آگهی از لیست من", callback_data='delete|'+str(post_id)),
                ],
            ]
            edit_kb_markup = InlineKeyboardMarkup(edit_kb)
            update.message.reply_text(
                    post_obj[1],
                    reply_markup=edit_kb_markup
            )
            return EDIT

    # TODO change this to FOLLOW_AD stat
    return MAIN_MENU

def edit_post_fn(update: Update,context:CallbackContext):

    query = update.callback_query
    print(query.data)
    action, post_id = query.data.split("|")
    if action=='assigned':
        q = "SELECT message_id FROM posts WHERE id={}".format(int(post_id))
        cursor.execute(q)
        post_obj = cursor.fetchone()
        context.bot.editMessageText(chat_id=CHANNEL_ID,message_id=post_obj[9],text=post_obj[3])
        query.message.reply_text(
            "تغییرات با موفقیت اعمال شد",
            reply_markup=main_menu_markup
        )
        return MAIN_MENU
    elif action=="delete":
        q = "UPDATE posts SET active_flag={} WHERE id={}".format(False,post_id)
        cursor.execute(q)
        mydb.commit()
        query.message.reply_text(
            "آگهی از لیست آگهی های شما حذف گردید",
            reply_markup=main_menu_markup
        )
        return MAIN_MENU


        
        

def choose_category_fn(update: Update,context:CallbackContext) -> int:

    user_id = update.message.from_user.id
    result = context.bot.get_chat_member(chat_id=CHANNEL_ID,user_id=user_id)
    if result['status'] != "member" and result['status'] != 'creator':

        update.message.reply_text(
            'ابتدا در کانال عضو شوید',
            reply_markup=join_channel_markup
            )

        return JOIN

    message = update.message.text
    context.user_data['category'] = message.replace(' ','_')
    update.message.reply_text(
        "لطفا دانشگاه خود را انتخاب کنید و یا اسم دانشگاه خود را تایپ کنید",
        reply_markup=universities_markup
    )
    return CHOOSE_UNIVERSITY

def choose_university_fn(update: Update,context:CallbackContext) -> int:

    user_id = update.message.from_user.id
    result = context.bot.get_chat_member(chat_id=CHANNEL_ID,user_id=user_id)

    if result['status'] != "member" and result['status'] != 'creator':

        update.message.reply_text(
            'ابتدا در کانال عضو شوید',
            reply_markup=join_channel_markup
            )

        return JOIN

    message = update.message.text
    context.user_data['university'] = message.replace(' ','_')
    update.message.reply_text(
        "متنی آگهیت رو بفرست",
        reply_markup=user_ads_markup
    )
    return TEXT

def choose_text_fn(update: Update,context:CallbackContext) -> int:

    user_id = update.message.from_user.id
    result = context.bot.get_chat_member(chat_id=CHANNEL_ID,user_id=user_id)

    if result['status'] != "member" and result['status'] != 'creator':

        update.message.reply_text(
            'ابتدا در کانال عضو شوید',
            reply_markup=join_channel_markup
            )

        return JOIN

    message = update.message.text
    context.user_data['text'] = message
    update.message.reply_text(
        "آیدی ای که میخوای تو آگهیت درج بشه رو بفرست",
        reply_markup=user_ads_markup
    )
    return ID

def choose_id_fn(update: Update,context:CallbackContext) -> int:

    user_id = update.message.from_user.id
    result = context.bot.get_chat_member(chat_id=CHANNEL_ID,user_id=user_id)

    if result['status'] != "member" and result['status'] != 'creator':

        update.message.reply_text(
            'ابتدا در کانال عضو شوید',
            reply_markup=join_channel_markup
            )

        return JOIN

    message = update.message.text

    if not bool(re.match(r"^@[A-Za-z0-9_.]{3,}", message)):
        update.message.reply_text(
            "آی دی باید با @ شروع و بیشتر از 3 کاراکتر انگلیسی باشد",
            reply_markup=user_ads_markup
        )
        return ID
    else:

        # payment configs
        
        update.message.reply_text(
            "در حال ایجاد آگهی ..."
        )
        
        response = requests.post(
            "https://gateway.zibal.ir/v1/request",
            json={'merchant':'zibal','amount':100000,'callbackUrl':"https://aversi.ir/verify"}
            )
        if response.json()['result']==100:
            context.user_data['trackId'] = response.json()['trackId']
            payment_kb = [
                [
                    InlineKeyboardButton("پرداخت بانکی",url="https://gateway.zibal.ir/start/{}".format(response.json()['trackId'])),
                    InlineKeyboardButton("پرداخت با امتیاز", callback_data='freepay'),
                ],
                [InlineKeyboardButton("پرداخت کردم", callback_data='payed'),]
            ]

            payment_kb_markup = InlineKeyboardMarkup(payment_kb)

            context.user_data['id'] = message
            final_message = "#"+context.user_data['category']+"\n"+"#"+context.user_data['university']+"\n"+ context.user_data['text']+"\n"+context.user_data['id']+"\n"+"----------------\n"+CHANNEL_ID
            update.message.reply_text(
                "متن نهایی آگهی شما به صورت زیر نمایش داده خواهد شد: \n"+ final_message,
                reply_markup=payment_kb_markup
            )
            context.user_data['final_message'] = final_message

            # Add post to DB
            query = "INSERT INTO posts (full_text,username,content,university,category,user_id,state,created_at,active_flag) \
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            values = (
                context.user_data['final_message'],
                context.user_data['id'],
                context.user_data['text'],
                context.user_data['university'],
                context.user_data['category'],
                user_id,
                PAYMENT,
                datetime.now(),
                True
                )
            cursor.execute(query,values)
            mydb.commit()
            context.user_data['post_id'] = cursor.lastrowid

            return PAYMENT

def check_payment_fn(update: Update,context:CallbackContext):

    query = update.callback_query
    # print(query.id)
    # print(query.data)
    if query!=None and query.data == "payed":
        response = requests.post(
            "https://gateway.zibal.ir/v1/verify",
            json={'merchant':'zibal','trackId':context.user_data['trackId']}
            )
        if response.json()['result']==100 and response.json()['status'] == 1:
            sent_message = context.bot.sendMessage(chat_id=CHANNEL_ID,text=context.user_data['final_message'])
            query.message.reply_text(
                "آگهی شما ثبت شد و بعد از تایید ادمین بلافاصله در کانال قرار میگیرد",
                reply_markup=main_menu_markup
            )
            print(context.user_data['post_id'],sent_message.message_id)
            q = "UPDATE posts SET state = {},message_id={} WHERE id = {}".format(PAYED,sent_message.message_id, context.user_data['post_id'])
            cursor.execute(q)
            mydb.commit()
            
            return MAIN_MENU
        else:
            query.bot.answer_callback_query(query.id,
                text="پرداخت نکرده اید و یا پرداختتان موفق نبوده با پشتیبانی در تماس باشید" +"\n"+SUPPORT_ID, show_alert=True
                )
            # return PAYMENT
        
    else:
        print('not payed')

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater("453030525:AAF-ME2fRI3IHs9P6zVpYSZXeMImbqZGIjE")
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            JOIN: [
                MessageHandler(
                    Filters.text, join_channel_fn
                ),
                CallbackQueryHandler(join_channel_fn)
            ],
            MAIN_MENU: [
                CommandHandler('start', start),
                MessageHandler(
                    Filters.regex('^(مدیریت آگهی ها 🗄|ثبت آگهی جدید 📋|ثبت آگهی رایگان 🆓|دیدن آگهی ها)$'), main_menu_fn
                ),
            ],
            MANAGE_ADS: [
                CommandHandler('start', start),
                MessageHandler(
                    Filters.regex('^([\d]{1,})[|].+'), manage_ads_fn
                ),
            ], 
            SHOW_ADS: [
                CallbackQueryHandler(show_ads_fn),
                MessageHandler(Filters.regex('^بازگشت به منو$'),back_to_main_menu),

            ],   
            CHOOSE_CATEGORY: [
                CommandHandler('start', start),
                MessageHandler(
                    Filters.regex('^(خریدار|فروشنده|انجام دهنده|درخواست کننده|فرصت شغلی)$') , choose_category_fn
                ),
            ],
            CHOOSE_UNIVERSITY: [
                CommandHandler('start', start),
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('#فوری')) , choose_university_fn
                ),
            ],
            TEXT: [
                CommandHandler('start', start),
                MessageHandler(
                    Filters.text , choose_text_fn
                ),
            ],
            ID: [
                CommandHandler('start', start),
                MessageHandler(
                    Filters.text , choose_id_fn
                ),
            ],
            PAYMENT: [
                CommandHandler('start', start),
                MessageHandler(Filters.regex('^بازگشت به منو$'),back_to_main_menu),
                CallbackQueryHandler(check_payment_fn)
            ],
            EDIT: [
                CommandHandler('start', start),
                MessageHandler(Filters.regex('^بازگشت به منو$'),back_to_main_menu),
                CallbackQueryHandler(edit_post_fn)
            ]
            
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
        fallbacks=[MessageHandler(Filters.regex('^بازگشت به منو$'), back_to_main_menu),CommandHandler('start', start)],
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