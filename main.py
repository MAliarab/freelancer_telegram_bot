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
     CHOOSE_UNIVERSITY, BACK_TO__MENU,CHOOSE_LOCATION,TEXT, ID, PAYMENT, SHOW_ADS, PAYED, EDIT,ADMIN_COM, ACCOUNT, AGREEMENT = range(18)

# Admin info
ADMIN_TOKEN = "Libr0na@dmin6320"
# Global variables
CHANNEL_COIN_LIMIT = 5
BOT_COIN_LIMIT = 2
PAY_AMOUNT = 50000
# Channel and Bot information
ARCHIVE_CHANNEL = -1001183381943
CHANNEL_ID = "@tempchann"
BOT_ID = "btiibot"
SUPPORT_ID = "@dashtab"
# Static messages
FIRST_TIME_GREETING = """🖐 سلام
🔸 به بات لیبرونا خوش آمدید
💰 با اولین ورودتان به بات لیبرونا «۵ امتیاز» دریافت کردید """

GREETING_MESSAGE = """🖐 سلام
🔸 به بات لیبرونا خوش آمدید"""

POLICY_MESSAGE = """⚠️ حتما ابتدا قوانین را بخوانید 
⚖️ راهنما و قوانین ثبت آگهی:

1️⃣ هزینه ی درج آگهی در «کانال و بات» ۵ هزار تومان (۵ امتیاز) و هزینه ی درج آگهی «فقط در بات» ۲ هزار تومان (۲ امتیاز) است

❓۱- درج آگهی در بات: آگهی ثبت شده فقط از طریق بات و از بخش «دیدن آگهی‌ها» قابل مشاهده است و هزینه ی آن ۲ هزار تومان یا ۲ امتیاز است
❓۲- درج آگهی در کانال و بات: آگهی ثبت شده هم در کانال و هم در بات نمایش داده می شود و هزینه ی آن ۵ هزار تومان یا ۵ امتیاز است

2️⃣ توی متن آگهی استفاده از لینک و موارد تبلیغاتی مجاز نیست! 

3️⃣  استفاده از کلمات مستجهن و توهین آمیز ممنوع است.🔒

4️⃣ متن آگهی باید برای یک خواسته و نیازمندی باشه یعنی نمیتوانید چند موضوع مختلف را در قالب یک آگهی ثبت کنید

5️⃣ آگهی ها بعد از ۵ روز به طور خودکار از بات و کانال حذف می شوند

🔸 برای تبلیغات و با پشتیبانی لیبرونا در تماس باشید

🆔 @Librona_ir

❌ در صورتی که آگهی تون قوانین ذکر شده رو رعایت نکرده باشه آگهی از کانال پاک میشه  و هیچ مسولیتی در قبال وجه پرداختی شما نیست ❌""" 

JOIN_TO_CHANNEL_MESSAGE = """🔶 برای ادامه در کانال عضو شوید"""

# Keyboard and matkup definitions 

# Keyboard
join_channel = [
    [
        InlineKeyboardButton("عضویت در کانال",url="https://t.me/tempchann"),
        InlineKeyboardButton("عضو شدم", callback_data='joined'),
    ],
]

continue_kb = [
    [InlineKeyboardButton("ادامه", callback_data='resume'),]
]

main_keyboard = [
    ['مدیریت آگهی‌ها', 'ثبت آگهی جدید'],
    ['حساب من'],
    ['دیدن آگهی‌ها'],
]
categories = [
    ["انجام دهنده", "درخواست کننده"],
    ["خریدار", "فروشنده"],
    ["فرصت شغلی"],
    ["بازگشت به منو"],
]
universities = [
    ["تهران", " شهید بهشتی"],
    ["علم و صنعت", "شریف"],
    ["دیگر"],
    ["بازگشت به منو"],
]


user_ads = [
    ['بازگشت به منو'],
]

admin_kb = [
    ['ارسال آگهی‌های تایید شده'],
    ['نمایش آگهی ها برای تایید'],
    ['بازگشت به منو'],
]

agreement_kb = [
    ['قوانین را میپذیرم'],
    ['بازگشت به منو']
]

show_ads_kb = [
    [
        InlineKeyboardButton("آگهی‌های ۱ روز اخیر", callback_data=1),
        InlineKeyboardButton("آگهی‌های ۳ روز اخیر", callback_data=3),
    ],
    [InlineKeyboardButton("تمام آگهی‌ها", callback_data=5),]
]

credit_kb = [
    ['شارژ حساب'],
    ['بازگشت به منو']
]

amount_kb = [
    ['۲ هزار تومان'],
    ['۵ هزار تومان'],
    ['۱۰ هزار تومان'],
    ['بازگشت به منو']
]
# Markup
main_menu_markup = ReplyKeyboardMarkup(main_keyboard,resize_keyboard=True)
user_ads_markup = ReplyKeyboardMarkup(user_ads,resize_keyboard=True)
categories_markup = ReplyKeyboardMarkup(categories,resize_keyboard=True)
universities_markup = ReplyKeyboardMarkup(universities,resize_keyboard=True)
join_channel_markup = InlineKeyboardMarkup(join_channel)
show_ads_markup = InlineKeyboardMarkup(show_ads_kb)
admin_markup = ReplyKeyboardMarkup(admin_kb,resize_keyboard=True)
credit_markup = ReplyKeyboardMarkup(credit_kb,resize_keyboard=True)
amount_markup = ReplyKeyboardMarkup(amount_kb,resize_keyboard=True)
agreement_markup = ReplyKeyboardMarkup(agreement_kb,resize_keyboard=True)
continue_markup = InlineKeyboardMarkup(continue_kb)
# Database settings
mydb = mysql.connector.connect(
    database='karbotdb',
    host="localhost",
    user="karbotadmin",
    password="458025166"
)
cursor = mydb.cursor()


def start(update: Update, context: CallbackContext) -> int:

    invited_by = None
    if len(update.message.text.split(' '))>1:
        invited_by = int(update.message.text.split(' ')[1])
    # ---------------------------------

    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    username = update.message.from_user.username
    firstname = update.message.from_user.first_name
    lastname = update.message.from_user.last_name
    
    # Add user to DB if there is not in DB
    q1 = "SELECT * FROM users WHERE id={}".format(user_id)
    cursor.execute(q1)
    user = cursor.fetchall()
    if len(user) == 0:

        q2 = ("INSERT INTO users (id,coin,chat_id,firstname,username,lastname,invited_by,joined_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)")
        values = (user_id,5,chat_id,firstname,username,lastname,invited_by,datetime.now())
        cursor.execute(q2,values)
        mydb.commit()

        update.message.reply_text(
            FIRST_TIME_GREETING,
            reply_markup=main_menu_markup,
        )

        return MAIN_MENU
        # add a coin to inviter 
        if invited_by:
            q3 = ("UPDATE users SET coin=coin+{} WHERE id={}").format(1,invited_by)
            cursor.execute(q3)
            mydb.commit()

    
    result = context.bot.get_chat_member(chat_id=CHANNEL_ID,user_id=user_id)
    
    # if result['status'] != "member" and result['status'] != 'creator':

    #     update.message.reply_text(
    #         JOIN_TO_CHANNEL_MESSAGE,
    #         reply_markup=join_channel_markup
    #         )

    #     return JOIN
    # else:
    update.message.reply_text(
        GREETING_MESSAGE,
        reply_markup=main_menu_markup,
    )

    return MAIN_MENU

def agreement_fn(update: Update, context: CallbackContext) -> int:

        update.message.reply_text(
            """لطفا نوع آگهی خود را از بین 5 مورد زیر انتخاب کنید

📜 درخواست_کننده
تمرین، پروژه و... دارم که میخواهم کسی در انجامش به من کمک کند.

📜 انجام_دهنده
توانایی‎هایی دارم که میخواهم آن‎ها را به اعضای کانال معرفی کنم.

📜 فروشنده
کتاب، وسایل دانشجویی و ... دارم که می‎خواهم آن را بفروشم.

📜 خریدار
کتاب، وسایل دانشجویی و ... نیاز دارم که می‎خواهم بخرم.

📜 فرصت_شغلی
موقعیت شغلی وجود دارد که میخواهم آن را به اعضا معرفی کنم.""",
                        
            reply_markup=categories_markup
        )

        return CHOOSE_CATEGORY


def verify_fn(update: Update, context: CallbackContext) -> int:

    query = update.callback_query
    
    post_id, command = query.data.split('|')
    
    if command == "verify":
        q = "UPDATE posts SET verify={} WHERE id = {}".format(1,int(post_id))

        cursor.execute(q)
        mydb.commit()

        query.message.reply_text(
            "number: {}\n ✅ verified".format(post_id)
        )
    elif command == "noverify":

        q = "UPDATE posts SET verify={} WHERE id = {}".format(-1,int(post_id))

        cursor.execute(q)
        mydb.commit()

        query.message.reply_text(
            "number: {}\n ⛔️ rejected".format(post_id)
        )
    
    return ADMIN_TOKEN


def admin_com_fn(update: Update, context: CallbackContext) -> int:
    message = update.message.text
    if message == admin_kb[0][0]:
        date = datetime.now()-timedelta(days=2)
        q = "SELECT full_text,id FROM posts WHERE verify={}".format(1)
        cursor.execute(q)
        posts = cursor.fetchall()
        if len(posts) == 0:
            update.message.reply_text(
            "آگهی تایید شده ی جدیدی وجود ندارد !!!",
            reply_markup=admin_markup
            )
            return ADMIN_TOKEN

        for post in posts:
            sent_message = context.bot.sendMessage(chat_id=CHANNEL_ID,text=post[0])

            q2 = "UPDATE posts SET verify={},message_id={} WHERE id={}".format(2,sent_message.message_id,post[1])
            cursor.execute(q2)
            mydb.commit()

        update.message.reply_text(
            "پیام ها ارسال شدند",
            reply_markup=admin_markup
        )

        return ADMIN_TOKEN
    elif message == admin_kb[1][0]:
        q = "SELECT full_text, id,channel_pub FROM posts WHERE bot_pub={} AND verify is NULL".format(True)
        cursor.execute(q)
        posts = cursor.fetchall()

        if len(posts) == 0:
            update.message.reply_text(
                "آگهی جدیدی وجود ندارد !!!",
                reply_markup=admin_markup
            )
        for post in posts:
            verify_kb = [
                    [
                        InlineKeyboardButton("✅تایید",callback_data=str(post[1])+"|"+"verify"),
                        InlineKeyboardButton("⛔️رد", callback_data=str(post[1])+"|"+"noverify"),
                    ],
                ]
            
            verify_markup = InlineKeyboardMarkup(verify_kb)

            
            update.message.reply_text(
                "پست شماره:" + str(post[1])+"\n"+post[0],
                reply_markup=verify_markup
            )
        return ADMIN_TOKEN
    else:
        q = "SELECT chat_id FROM users"
        cursor.execute(q)
        info = cursor.fetchall()

        
        for chat_id in info:
            context.bot.sendMessage(chat_id=chat_id[0],text=message)
        
        update.message.reply_text(
            "تبلیغ ارسال شد",
            reply_markup=main_menu_markup
        )
    return ADMIN_TOKEN

def join_channel_fn(update: Update, context: CallbackContext) -> int:

    if update.message != None:
        user_id = update.message.from_user.id
        result = context.bot.get_chat_member(chat_id=CHANNEL_ID,user_id=user_id)

        if result['status'] != "member" and result['status'] != 'creator':

            update.message.reply_text(
                JOIN_TO_CHANNEL_MESSAGE,
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
                "ممنون از عضویت شما در کانال لطفا برای ادامه کلید «ادامه» را بزنید",
                reply_markup=continue_markup,
            )
            
            return ID
    else:
        query.message.reply_text(
            JOIN_TO_CHANNEL_MESSAGE,
            reply_markup=join_channel_markup
            )

        return JOIN    

def back_to_main_menu(update: Update, context: CallbackContext) -> int:

    user_id = update.message.from_user.id
    result = context.bot.get_chat_member(chat_id=CHANNEL_ID,user_id=user_id)

    # if result['status'] != "member" and result['status'] != 'creator':

    #     update.message.reply_text(
    #         JOIN_TO_CHANNEL_MESSAGE,
    #         reply_markup=join_channel_markup
    #         )

    #     return JOIN

    
    update.message.reply_text(
        "منو",
        reply_markup=main_menu_markup,
    )

    return MAIN_MENU
    

def credit_fn(update: Update, context: CallbackContext) -> int:

    update.message.reply_text(
        "مبلغ مورد نظر خود برای شارژ را انتخاب کنید"+"\nهر هزار تومان معادل ۱ امتیاز است",
        reply_markup=amount_markup
    )

    return ACCOUNT

def amount_fn(update: Update, context: CallbackContext) -> int:
    query = update.callback_query

    if query != None:
        if query.data == "payed":
            user_id = query.from_user.id
            response = requests.post(
                "https://gateway.zibal.ir/v1/verify",
                json={'merchant':'zibal','trackId':context.user_data['credit_track_id']}
                )
            if response.json()['result']==100 and response.json()['status'] == 1:
                query.message.reply_text(
                    "امتیاز شما افزایش یافت میتوانید امتیاز خود را از بخش حساب من در منو اصلی مشاهده نمایید",
                    reply_markup=main_menu_markup
                )
                # print(context.user_data['post_id'],sent_message.message_id)
                q = "UPDATE users SET coin = coin+{} WHERE id = {}".format(context.user_data['amount'],user_id)
                cursor.execute(q)
                mydb.commit()
                
                return MAIN_MENU
            else:
                query.bot.answer_callback_query(query.id,
                    text="پرداخت نکرده اید و یا پرداختتان موفق نبوده با پشتیبانی در تماس باشید" +"\n"+SUPPORT_ID, show_alert=True
                    )
        return ACCOUNT
    message = update.message.text
    amount = None
    if message == amount_kb[0][0]:
        context.user_data['amount'] = 2
        amount = 20000
    elif message == amount_kb[1][0]:
        context.user_data['amount'] = 5
        amount = 50000
    elif message == amount_kb[2][0]:
        context.user_data['amount'] = 10
        amount = 100000
    
    update.message.reply_text(
        'لطفا منتظر بمانید ...'
    )
    response = requests.post(
            "https://gateway.zibal.ir/v1/request",
            json={'merchant':'zibal','amount':amount,'callbackUrl':"https://aversi.ir/verify"}
            )
    
    payment_kb = [
                    [
                        InlineKeyboardButton("پرداخت بانکی",url="https://gateway.zibal.ir/start/{}".format(response.json()['trackId'])),
                    ],
                    [InlineKeyboardButton("پرداخت کردم", callback_data='payed'),],
                    
                ]
    payment_markup = InlineKeyboardMarkup(payment_kb)
    
    update.message.reply_text(
        "پرداخت را تکمیل کنید و سپس بر روی گزینه ی پرداخت کردم کلیک کنید",
        reply_markup=payment_markup
    )

    context.user_data['credit_track_id'] = response.json()['trackId']



def main_menu_fn(update: Update, context: CallbackContext) -> int:

    user_id = update.message.from_user.id
    result = context.bot.get_chat_member(chat_id=CHANNEL_ID,user_id=user_id)
    if update.message.text == ADMIN_TOKEN:
        update.message.reply_text(
            'پیام را بفرست',
            reply_markup=admin_markup
        )
        return ADMIN_TOKEN

    # if result['status'] != "member" and result['status'] != 'creator':

    #     update.message.reply_text(
    #         JOIN_TO_CHANNEL_MESSAGE,
    #         reply_markup=join_channel_markup
    #         )

    #     return JOIN

    message = update.message.text   
    if message == main_keyboard[2][0]:
        update.message.reply_text(
            """🗂در این بخش می‌توانید آگهی های دیگران را ببینید و با آنها همکاری کنید
لطفا بازه ی زمانی مورد نظر خود را انتخاب کنید""",
            reply_markup=show_ads_markup
        )
        return SHOW_ADS

    elif message == main_keyboard[0][0]:
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
            reply_markup=agreement_markup
        )        
        return AGREEMENT
    elif message == main_keyboard[1][0]:
        invite_message = """➕ با استفاده از لینک اختصاصی خودتان  که در پیام زیر میبینید میتوانید دوستانتان را به ربات دعوت کنید و با هر دعوت ۱ امتیاز بگیرید

➕ با هر «۲ امتیاز» میتوانید یک آگهی رایگان «در بات» و با هر « ۵ امتیاز » یک آگهی رایگان «در کانال و بات» ثبت کنید

🔶 پیام زیر را برای دوستانتان ارسال کنید و آنها را به بات دعوت کنید 👇"""

        update.message.reply_text(
            invite_message,
            # TODO add new button list for this
            reply_markup=user_ads_markup
        )
        invite_special_link = "دانشجوهایی که دنبال کار پاره وقت هستن، توو این کانال کلی پروژه و تمرین هست که میتونی انجام بدی و درآمد عالی داشته باشی. خودتونم اگه نیاز به کمک داشته باشید میتونید از دانشجوهای دیگه کمک بگیرید "+ \
            "\nاز طریق لینک زیر عضو شو:\n"+ "https://t.me/{}?start={}".format(BOT_ID,user_id)
        update.message.reply_text(
            invite_special_link,
            reply_markup=user_ads_markup
        )
        q = "SELECT coin FROM users WHERE id={}".format(user_id)
        cursor.execute(q)
        coin = cursor.fetchone()
        update.message.reply_text(
            "💰 امتیاز شما: {}".format(coin[0]),
            reply_markup=credit_markup
        )
        
        return ACCOUNT

def show_ads_fn(update: Update,context:CallbackContext) -> int:

    query = update.callback_query
    try:
        date = datetime.now()-timedelta(days=int(query.data))
    except Exception as e:
        print("exception occured")
    q = "SELECT full_text from posts WHERE active_flag = {} AND created_at >= '{}' AND bot_pub = {} AND verify = {}".format(True, date, True,1)

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
    
    # if result['status'] != "member" and result['status'] != 'creator':

    #     update.message.reply_text(
    #         JOIN_TO_CHANNEL_MESSAGE,
    #         reply_markup=join_channel_markup
    #         )

    #     return JOIN
    q = "SELECT * FROM posts WHERE id={}".format(post_id)
    cursor.execute(q)
    post_obj = cursor.fetchone()
    if post_obj==None:
        update.message.reply_text(
            'آگهی یافت نشد'
        )
    
    else:
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
                if post_obj[12]==False: # if post published in bot
                    payment_kb = [
                        [
                            InlineKeyboardButton("پرداخت بانکی",url="https://gateway.zibal.ir/start/{}".format(response.json()['trackId'])),
                            InlineKeyboardButton("پرداخت با امتیاز (۵ امتیاز)", callback_data='freepay'),
                        ],
                        [InlineKeyboardButton("پرداخت کردم", callback_data='payed'),],
                        [InlineKeyboardButton("انتشار در ربات (۲ امتیاز)", callback_data='botpub'),],
                        [InlineKeyboardButton("حذف آگهی از لیست من", callback_data='delete|'+str(post_id)),],
                        
                    ]
                else:
                    payment_kb = [
                        [
                            InlineKeyboardButton("پرداخت بانکی",url="https://gateway.zibal.ir/start/{}".format(response.json()['trackId'])),
                            InlineKeyboardButton("پرداخت با امتیاز (۵ امتیاز)", callback_data='freepay'),
                        ],
                        [InlineKeyboardButton("پرداخت کردم", callback_data='payed'),],
                        [InlineKeyboardButton("حذف آگهی از لیست من", callback_data='delete|'+str(post_id)),],
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
    action, post_id = query.data.split("|")
    if action=='assigned':
        q = "SELECT * FROM posts WHERE id={}".format(int(post_id))
        cursor.execute(q)
        post_obj = cursor.fetchone()
        
        context.bot.editMessageText(chat_id=CHANNEL_ID,message_id=post_obj[9],text=post_obj[3]+"\nواگذار شد 🛑"+"\n---------------\n"+CHANNEL_ID)
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
    # if result['status'] != "member" and result['status'] != 'creator':

    #     update.message.reply_text(
    #         JOIN_TO_CHANNEL_MESSAGE,
    #         reply_markup=join_channel_markup
    #         )

    #     return JOIN

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

    # if result['status'] != "member" and result['status'] != 'creator':

    #     update.message.reply_text(
    #         JOIN_TO_CHANNEL_MESSAGE,
    #         reply_markup=join_channel_markup
    #         )

    #     return JOIN

    message = update.message.text
    context.user_data['university'] = message.replace(' ','_')
    update.message.reply_text(
        """ابتدا متن آگهی خود را برای ما بفرستید

مثال: به یک نفر مسلط به برنامه نویسی برای رفع اشکال نیازمندم""",
        reply_markup=user_ads_markup
    )
    return TEXT

def choose_text_fn(update: Update,context:CallbackContext) -> int:

    user_id = update.message.from_user.id
    result = context.bot.get_chat_member(chat_id=CHANNEL_ID,user_id=user_id)

    # if result['status'] != "member" and result['status'] != 'creator':

    #     update.message.reply_text(
    #         JOIN_TO_CHANNEL_MESSAGE,
    #         reply_markup=join_channel_markup
    #         )

    #     return JOIN

    message = update.message.text
    if len(message) > 450:
        update.message.reply_text(
            """طول متن آگهی نباید بیشتر از ۴۵۰ کاراکتر باشد""",
        reply_markup=user_ads_markup
        )

        return TEXT
    else:
        context.user_data['text'] = message
        update.message.reply_text(
            """لطفا آیدی که میخواهید برای آگهیتان درج شود را بفرستید
    مثال: @Librona_ir""",
            reply_markup=user_ads_markup
        )
        return ID

def choose_id_fn(update: Update,context:CallbackContext) -> int:
    query = update.callback_query
    if query:
        message = query.data
        user_id = query.from_user.id
        update = query
    else:
        
        message = update.message.text
        user_id = update.message.from_user.id

    result = context.bot.get_chat_member(chat_id=CHANNEL_ID,user_id=user_id)

    
    
    if not bool(re.match(r"^@[A-Za-z0-9_.]{3,}", message)) and message != 'resume':
        update.message.reply_text(
            "آی دی باید با @ شروع و بیشتر از 3 کاراکتر انگلیسی باشد",
            reply_markup=user_ads_markup
        )
        return ID
    elif len(message) > 45 and message != 'resume':
        update.message.reply_text(
            "طول آیدی نباید بیشتر از ۴۵ کاراکتر باشد",
            reply_markup=user_ads_markup
        )
        return ID
    
        
    elif result['status'] != "member" and result['status'] != 'creator' and message != 'resume':
        context.user_data['id'] = message
        update.message.reply_text(
            JOIN_TO_CHANNEL_MESSAGE,
            reply_markup=join_channel_markup
            )

        return JOIN
    else:
        if not query:
            context.user_data['id'] = message

        # payment configs
        
        update.message.reply_text(
            """📌 مبلغ انتشار آگهی در کانال و ربات ۵ هزار تومان (۵ امتیاز) و برای انتشار «فقط در بات» ۲ هزار تومان (۲ امتیاز) می باشد.

    🔺۱- انتشار در «کانال و بات»: با این گزینه آگهی شما هم در کانال منتشر می شود و هم در بات که از بخش «دیدن آگهی ها» در منو اصلی قابل مشاهده است
   🔺 ۲- انتشار «فقط در بات»: با این گزینه آگهی فقط در بات و از قسمت «دیدن آگهی ها» از منو اصلی برای دیگران قابل مشاهده است

🛑 حتما بعد از پرداخت بانکی گزینه ی «پرداخت کردم» را انتخاب کنید.

🔸 برای {افزایش امتیاز} میتوانید از بخش «حساب من» در منو اصلی استفاده کنید.

در حال ایجاد آگهی ..."""
        )
        
        response = requests.post(
            "https://gateway.zibal.ir/v1/request",
            json={'merchant':'zibal','amount':PAY_AMOUNT,'callbackUrl':"https://aversi.ir/verify"}
            )
        # response_bot = 
        if response.json()['result']==100:
            context.user_data['trackId'] = response.json()['trackId']
            payment_kb = [
                [
                    InlineKeyboardButton("پرداخت بانکی",url="https://gateway.zibal.ir/start/{}".format(response.json()['trackId'])),
                    InlineKeyboardButton("پرداخت با امتیاز (۵ امتیاز)", callback_data='freepay'),
                ],
                [InlineKeyboardButton("پرداخت کردم", callback_data='payed'),],
                [
                    InlineKeyboardButton("انتشار در بات (۲ امتیاز)", callback_data='botpub'),
                    # InlineKeyboardButton("انتشار در بات (پرداخت بانکی)", callback_data='botpubpay'),
                
                ]
            ]

            payment_kb_markup = InlineKeyboardMarkup(payment_kb)

            
            final_message = "#"+context.user_data['category']+"\n"+"#"+context.user_data['university']+"\n"+ context.user_data['text']+"\n"+context.user_data['id']+"\n"+"----------------\n"+CHANNEL_ID
            update.message.reply_text(
                "متن نهایی آگهی شما به صورت زیر نمایش داده خواهد شد: \n"+ final_message,
                reply_markup=payment_kb_markup
            )
            context.user_data['final_message'] = final_message
            print(user_id)
            # Add post to DB
            query = "INSERT INTO posts (full_text,username,content,university,category,user_id,state,created_at,active_flag,bot_pub,channel_pub) \
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            values = (
                context.user_data['final_message'],
                context.user_data['id'],
                context.user_data['text'],
                context.user_data['university'],
                context.user_data['category'],
                user_id,
                PAYMENT,
                datetime.now(),
                True,
                False,
                False,
                )
            cursor.execute(query,values)
            mydb.commit()
            context.user_data['post_id'] = cursor.lastrowid

            return PAYMENT

def check_payment_fn(update: Update,context:CallbackContext):


    query = update.callback_query
    user_id = query.from_user.id
    if query!=None and "delete" in query.data:
        edit_post_fn(update,context)
        return MAIN_MENU
    elif query!=None and query.data == "payed":
        response = requests.post(
            "https://gateway.zibal.ir/v1/verify",
            json={'merchant':'zibal','trackId':context.user_data['trackId']}
            )
        if response.json()['result']==100 and response.json()['status'] == 1:
            sent_message = context.bot.sendMessage(chat_id=ARCHIVE_CHANNEL,text=context.user_data['final_message'])
            query.message.reply_text(
                "آگهی شما ثبت شد و بعد از تایید در کانال قرار میگیرد",
                reply_markup=main_menu_markup
            )
            # print(context.user_data['post_id'],sent_message.message_id)
            q = "UPDATE posts SET state = {},message_id={},channel_pub={},bot_pub={} WHERE id = {}".format(
                PAYED,sent_message.message_id,True,True,context.user_data['post_id']
                )
            cursor.execute(q)
            mydb.commit()
            
            return MAIN_MENU
        else:
            query.bot.answer_callback_query(query.id,
                text="پرداخت نکرده اید و یا پرداختتان موفق نبوده اگر مشکلی دارید با پشتیبانی مطرح کنید" +"\n"+SUPPORT_ID, show_alert=True
                )
            # return PAYMENT
    elif query!=None and query.data == "botpub":

        q = "SELECT coin from users WHERE id={}".format(user_id)
        cursor.execute(q)
        coin = cursor.fetchone()[0]
        if coin >= BOT_COIN_LIMIT:

            sent_message = context.bot.sendMessage(chat_id=ARCHIVE_CHANNEL,text=context.user_data['final_message'])

            q2 = "UPDATE users SET coin=coin-{} WHERE id={}".format(BOT_COIN_LIMIT,user_id,)
            cursor.execute(q2)
            mydb.commit()

            q = "UPDATE posts SET bot_pub={} WHERE id = {}".format(True,context.user_data['post_id'])
            cursor.execute(q)
            mydb.commit()
            query.message.reply_text(
                "آگهی شما با موفقیت ثبت شد و بعد از تایید در بات منتشر خواهد شد"+"\nآگهی های منتشر شده در ربات از بخش (دیدن آگهی‌ها) در منو اصلی قابل مشاهده است",
                reply_markup=main_menu_markup,
            )
        else:
            query.bot.answer_callback_query(query.id,
                text="امتیاز شما کافی نیست حداقل باید {} امتیاز داشته باشید. میتوانید از بخش حساب من در منو اصلی امتیاز خود را افزایش دهید".format(BOT_COIN_LIMIT), show_alert=True
            )

        return MAIN_MENU
    
        
    elif query!=None and query.data == "freepay":
        q = "SELECT coin from users WHERE id={}".format(user_id)
        cursor.execute(q)
        coin = cursor.fetchone()[0]
        if coin >= CHANNEL_COIN_LIMIT:
            sent_message = context.bot.sendMessage(chat_id=ARCHIVE_CHANNEL,text=context.user_data['final_message'])
            query.message.reply_text(
                "آگهی شما ثبت شد و بعد از تایید ادمین بلافاصله در کانال قرار میگیرد",
                reply_markup=main_menu_markup
            )
            q2 = "UPDATE users SET coin=coin-{} WHERE id={}".format(CHANNEL_COIN_LIMIT,user_id,)
            cursor.execute(q2)
            mydb.commit()

            q = "UPDATE posts SET state = {},message_id={},channel_pub={},bot_pub={} WHERE id = {}".format(
                PAYED,sent_message.message_id,True,True,context.user_data['post_id']
                )
            cursor.execute(q)
            mydb.commit()

            return MAIN_MENU
        else:
            query.bot.answer_callback_query(query.id,
                text="امتیاز شما کافی نیست حداقل باید {} امتیاز داشته باشید. میتوانید از بخش حساب من در منو اصلی امتیاز خود را افزایش دهید".format(CHANNEL_COIN_LIMIT), show_alert=True
            )

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater("453030525:AAF-ME2fRI3IHs9P6zVpYSZXeMImbqZGIjE")
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),MessageHandler(Filters.regex('^بازگشت به منو$'),back_to_main_menu),],
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
                    Filters.regex('^(مدیریت آگهی‌ها|ثبت آگهی جدید|حساب من|دیدن آگهی‌ها|{})$'.format(ADMIN_TOKEN)), main_menu_fn
                ),
                MessageHandler(Filters.regex('^بازگشت به منو$'),back_to_main_menu),
            ],
            MANAGE_ADS: [
                CommandHandler('start', start),
                MessageHandler(
                    Filters.regex('^([\d]{1,})[|].+'), manage_ads_fn
                ),
                MessageHandler(Filters.regex('^بازگشت به منو$'),back_to_main_menu),
            ], 
            SHOW_ADS: [
                CallbackQueryHandler(show_ads_fn),
                MessageHandler(Filters.regex('^بازگشت به منو$'),back_to_main_menu),
                MessageHandler(
                    Filters.regex('^(مدیریت آگهی‌ها|ثبت آگهی جدید|حساب من|دیدن آگهی‌ها)$'), main_menu_fn
                ),

            ],   
            CHOOSE_CATEGORY: [
                CommandHandler('start', start),
                MessageHandler(
                    Filters.regex('^(خریدار|فروشنده|انجام دهنده|درخواست کننده|فرصت شغلی)$') , choose_category_fn,
                ),
                MessageHandler(Filters.regex('^بازگشت به منو$'),back_to_main_menu),
            ],
            CHOOSE_UNIVERSITY: [
                CommandHandler('start', start),
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('بازگشت به منو')) , choose_university_fn
                ),
                MessageHandler(Filters.regex('^بازگشت به منو$'),back_to_main_menu),
            ],
            TEXT: [
                CommandHandler('start', start),
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('بازگشت به منو')) , choose_text_fn
                ),
                MessageHandler(Filters.regex('^بازگشت به منو$'),back_to_main_menu),
            ],
            ID: [
                CommandHandler('start', start),
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('بازگشت به منو')) , choose_id_fn
                ),
                MessageHandler(Filters.regex('^بازگشت به منو$'),back_to_main_menu),
                CallbackQueryHandler(choose_id_fn)
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
            ],

            ADMIN_TOKEN: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('بازگشت به منو')) , admin_com_fn
                ),
                MessageHandler(Filters.regex('^بازگشت به منو$'),back_to_main_menu),
                CallbackQueryHandler(verify_fn)
            ],

            ACCOUNT: [
                MessageHandler(Filters.regex('^بازگشت به منو$'),back_to_main_menu),
                MessageHandler(Filters.regex('^شارژ حساب$'),credit_fn),
                MessageHandler(Filters.regex('^۵ هزار تومان|۲ هزار تومان|۱۰ هزار تومان$'),amount_fn),
                CallbackQueryHandler(amount_fn)


            ],
            AGREEMENT: [
                MessageHandler(Filters.regex('^بازگشت به منو$'),back_to_main_menu),
                MessageHandler(Filters.regex('^قوانین را میپذیرم$'),agreement_fn),
            ]
            

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