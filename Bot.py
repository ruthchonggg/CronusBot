import logging
import ServerManager as sm

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackQueryHandler
from ServerManager import getToDoList

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)

def start(update, context):
    reply = " Hi there, welcome to Cronus bot to help you to keep track of your tasks and manage your time wisely! \n"
    reply += "/help - get information about the functions \n"
    reply += "/list - get to do list \n"
    reply += "/add - add tasks to your to do list in this format: <task>;<YYYY-MM-DD HH:MM:SS> \n"
    reply += "/done - remove tasks from your to do list"
    update.message.reply_text(reply) #reply to message

def help(update, context):
    update.message.reply_text("Help")

#Usage "<task>:<dd-mm-yy> <time in 24 hour>"
def add(update, context):
    #get user Id 
    userId = update.message.chat_id
    update.message.reply_text(userId)
    
    #get message 
    content = update.message.text.partition(' ')[2]
    ls = content.split(';')
    task = ls[0]
    deadline = ls[1]
    sm.addTask(userId, task, deadline)

def list(update, context):
    userId = update.message.chat_id
    update.message.reply_text(db.getToDoList(userId))

def remove(update, context):
    #print("/remove executed")
    userId = update.message.chat_id
    arr = sm.getArrayList(userId)
    keyboard= []
    
    for row in arr:
        option = str(row[0]) + " Due on: " + row[1].strftime('%d-%m-%Y %H:%M:%S') 
        rawData = str(userId) + "|" + str(row[0]) + "|" + row[1].strfttime('%Y-%m-%d %H:%M:%S') 
        keyboard.append([InlineKeyboardButton(str(option), callback_data = rawData)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Click on the completed task', reply_markup=reply_markup)

def button(update, context):
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. 

    query.answer()
    rawData = (query.data).split('|')
    db.removeTask(rawData[0], rawData[1], rawData[2])
    replyMsg = "\"" + rawData[1] + "\" due on " + rawData[2]
    query.edit_message_text(text="Well done! You have completed: \n{}".format(replyMsg))  
    
def dailytimer(update, context):
    context.job_queue.run_daily(sendlistdaily,8,context=update.message.chat_id)
    context.job_queue.run_daily(sendlistdaily,20,context=update.message.chat_id)

def monthlytimer(update, context):
    context.job_queue.run_monthly(sendlistmonthly,12,31,context=update.message.chat_id,day_is_strict=False)

def sendlistdaily(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text = sm.getToDoList(update.message.chat_id))

def sendlistmonthly(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text = sm.getDoneList(update.message.chat_id))

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    #Token: "1163662826:AAFiWa_icg17dZYWJ3ONZ6Jd9A7VABbo5fA"
    updater = Updater("1163662826:AAFiWa_icg17dZYWJ3ONZ6Jd9A7VABbo5fA", use_context=True)
    job = updater.job_queue
    dp = updater.dispatcher
  
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("add", add))    
    dp.add_handler(CommandHandler("list", list))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_error_handler(error)
    
    dp.add_handler(MessageHandler(Filters.text,sendlistdaily ,pass_job_queue=True))
    dp.add_handler(MessageHandler(Filters.text,sendlistmonthly ,pass_job_queue=True))
    
    updater.start_polling() #start bot   
    updater.idle() 

if __name__=='__main__':
    main() 

