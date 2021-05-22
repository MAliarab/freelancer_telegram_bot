# import logging

# from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
# from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
# )
# logger = logging.getLogger(__name__)


# def start(update: Update, _: CallbackContext) -> None:
#     keyboard = [
#         [
#             InlineKeyboardButton("Option 1", callback_data='1'),
#             InlineKeyboardButton("Option 2", callback_data='2'),
#         ],
#         [InlineKeyboardButton("Option 3", callback_data='3')],
#     ]

#     reply_markup = InlineKeyboardMarkup(keyboard)

#     update.message.reply_text('Please choose:', reply_markup=reply_markup)


# def button(update: Update, context: CallbackContext) -> None:
#     query = update.callback_query

#     # CallbackQueries need to be answered, even if no notification to the user is needed
#     # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
#     # query.answer()
#     print(query.id)
#     context.bot.answerCallbackQuery(query.id, "THIS IS AN ALERT", show_alert=True)



# def help_command(update: Update, _: CallbackContext) -> None:
#     update.message.reply_text("Use /start to test this bot.")


# def main() -> None:
#     # Create the Updater and pass it your bot's token.
#     updater = Updater("453030525:AAFlLIRaMcFhZcKqZPKM-D52hl3B_10R5YE")

#     updater.dispatcher.add_handler(CommandHandler('start', start))
#     updater.dispatcher.add_handler(CallbackQueryHandler(button))
#     updater.dispatcher.add_handler(CommandHandler('help', help_command))

#     # Start the Bot
#     updater.start_polling()

#     # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
#     # SIGTERM or SIGABRT
#     updater.idle()


# if __name__ == '__main__':
#     main()
































# import re
# import requests

# result = requests.post("https://gateway.zibal.ir/v1/verify",json={'merchant':'zibal','trackId':227477489})

# print(result.json())

import mysql.connector
from datetime import datetime
from datetime import timedelta
mydb = mysql.connector.connect(
    database='karbotdb',
    host="localhost",
    user="karbotadmin",
    password="458025166"
)

cursor = mydb.cursor()

# query = "INSERT INTO posts (full_text,username,category,user_id) VALUES (%s,%s,%s,%s)"
# vales = ('درود دوباره به شما','@haji','انجام کار ', 3)

# res = cursor.execute(query,vales)
# res2 = mydb.commit()
# yesterday = datetime.now() - timedelta(days=1)
# print(yesterday.replace(microsecond=0))
# query = "SELECT full_text FROM posts WHERE created_at >= '{}'".format(yesterday)
# query = "SELECT id,full_text FROM posts WHERE id={}".format(5)
query = "SELECT id, full_text FROM posts WHERE user_id = '{} AND active_flag={}' ORDER BY id DESC".format(1736424924,1)
q2 = "SELECT * FROM karbotdb.posts where user_id={} and active_flag={} ORDER BY id DESC".format(1736424924,1)
cursor.execute(q2)
result = cursor.fetchall()
print(result)


# print(mydb.database)

# text = "2||hello from"
# text2 = "new text"
# post_id = text2.split('||')
# print(post_id)
# import re
# print(bool(re.match('^([\d]{1,})[|].+',text)))
# print("b" in "ali")