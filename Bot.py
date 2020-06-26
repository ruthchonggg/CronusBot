import logging
import datetime
import ServerManager as sm

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackQueryHandler
from ServerManager import getToDoList

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)

TASK, DATE, INVALIDDATE, TIME, INVALIDTIME = range(5)

def start(update, context):
    reply = " Hi there, welcome to Cronus bot to help you to keep track of your tasks and manage your time wisely! \n"
    reply += "/help - get information about the functions \n"
    reply += "/list - get to do list \n"
    reply += "/add - add tasks to your to do list in this format: <task>;<YYYY-MM-DD HH:MM:SS> \n"
    reply += "/done - remove tasks from your to do list"
    update.message.reply_text(reply) 

def help(update, context):
    update.message.reply_text("Help")

def add(update, context):
    update.message.reply_text("Hi! What is the name of the task you would like to add?")
    return TASK

def getTask(update, context):
    taskName = update.message.text
    context.user_data['task'] = taskName
    update.message.reply_text(
        'What is the date {} is due on? Enter according to dd/mm/yyyy format'.format(taskName))
    return DATE

def getDate(update, context):
    date = update.message.text
    
    d,m,y = map(int, date.split('/'))
    try:
        validDate = datetime.date(y, m, d)
        context.user_data['date'] = date
        update.message.reply_text('What time is the task due? Enter in 24hr format')
        return TIME
    except ValueError:
        update.message.reply_text('Date entered is invalid, re-enter in dd/mm/yyyy format!')
        return INVALIDDATE
    
def invalidDate(update, context):
    date = update.message.text
    d, m, y = map(int, date.split('/'))

    try:
        validDate = datetime.date(y, m, d)
        context.user_data['date'] = date
        update.message.reply_text('What time is the task due? Enter in 24hr format.')
        return TIME
    except ValueError:
        update.message.reply_text('Date entered is invalid, re-enter in dd/mm/yyyy format!')
        return INVALIDDATE
        
def getTime(update, context):
    time = update.message.text
    newTime = time + ":00"

    try:
        validTime = datetime.datetime.strptime(newTime, "%H:%M:%S")
        context.user_data['time'] = time
        doneAdding(update, context)
    except ValueError:
        update.message.reply_text('Time entered is invalid, re-enter in HH:MM 24hr format!')
        return INVALIDTIME

def invalidTime(update, context):
    time = update.message.text
    newTime = time + ":00"

    try:
        validTime = datetime.datetime.strptime(newTime, "%H:%M:%S")
        context.user_data['time'] = time
        doneAdding(update, context)
    except ValueError:
        update.message.reply_text('Time entered is invalid, re-enter in HH:MM 24hr format!')
        return INVALIDTIME

def doneAdding(update, context):
    user_data = context.user_data
    #print(user_data)
    userId = update.message.chat_id
    task = user_data.get('task')
    date = user_data.get('date')
    time = user_data.get('time')
    update.message.reply_text('\"' + task + '\"' + ' due on ' + date + ' at ' + 
        time + ' has been added!') 

    deadline = formatDatetime(date, time)
    sm.addTask(userId, task, deadline)
    user_data.clear()
    return ConversationHandler.END

def formatDatetime(date, time):
    d, m, y = map(str, date.split("/"))
    formatted = y + "/" + m + "/" + d + " " + time + ":00"
    print(formatted)
    return formatted

def list(update, context):
    userId = update.message.chat_id
    update.message.reply_text(sm.getToDoList(userId))

def remove(update, context):
    userId = update.message.chat_id
    arr = sm.getArrayList(userId)
    keyboard= []
    
    for row in arr:
        option = str(row[0]) + " Due on: " + row[1].strftime('%d-%m-%Y %H:%M:%S') 
        rawData = str(userId) + "|" + str(row[0]) + "|" + row[1].strftime('%Y-%m-%d %H:%M:%S') 
        keyboard.append([InlineKeyboardButton(str(option), callback_data = rawData)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Click on the completed task', reply_markup=reply_markup)

def button(update, context):
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    
    query.answer()
    rawData = (query.data).split('|')
    sm.removeTask(rawData[0], rawData[1], rawData[2])
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
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add)],
        states={
            TASK: [MessageHandler(Filters.text, getTask)],
            DATE: [MessageHandler(Filters.text, getDate)],
            INVALIDDATE: [MessageHandler(Filters.text, invalidDate)],
            TIME: [MessageHandler(Filters.text, getTime)],
            INVALIDTIME: [MessageHandler(Filters.text, invalidTime)],
        },
        fallbacks=[MessageHandler(Filters.text, doneAdding)],
        allow_reentry = True
    )
    dp.add_error_handler(error)
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("list", list))
    dp.add_handler(CommandHandler("done", remove))
    dp.add_handler(CallbackQueryHandler(button))
    
    dp.add_handler(MessageHandler(Filters.text,sendlistdaily ,pass_job_queue=True))
    dp.add_handler(MessageHandler(Filters.text,sendlistmonthly ,pass_job_queue=True))
    
    updater.start_polling()  
    updater.idle() 

if __name__=='__main__':
    main() 

