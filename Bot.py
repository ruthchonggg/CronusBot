import logging
import datetime
import ServerManager as sm
import os

from datetime import timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackQueryHandler
from ServerManager import getToDoList

PORT = int(os.environ.get('PORT', 5000))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)

token2 = "1389087532:AAF_mbgxdy15TI-swWBgMB6V3ggPHrrW7tU"

TASK, DATE, INVALIDDATE, TIME, INVALIDTIME = range(5)
reply_keyboard = [['List', 'Add','Remove','Help']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = True, one_time_keyboard = False)
keyboard2 = [['Cancel']]
markup2 = ReplyKeyboardMarkup(keyboard2, resize_keyboard = True, one_time_keyboard = True)


def start(update, context):
    reply = " Hi there, I'm Cronus and I can help you to keep track of your tasks and manage your time wisely!⌛️ \n \n"
    reply += "Here are some buttons that you may find useful: \n"
    reply += "*List*📝: Get the list of tasks you have \n"
    reply += "*Add*➕: Add tasks to your list \n"
    reply += "*Remove*🗑: Remove tasks from your list when you are done \n"
    reply += "*Help*🔍: Get information regarding Cronus \n \n"
    reply += "Let’s start by clicking on the *Add* button!"
            
    #update.message.reply_text(reply) 
    userId = update.message.chat_id
    context.bot.send_message(chat_id=update.message.chat_id, text=reply, parse_mode = ParseMode.MARKDOWN,
                             reply_markup = markup)


def help(update, context):
    reply = "*List*📝: Get the list of tasks you have \n"
    reply += "*Add*➕: Add tasks to your list \n"
    reply += "*Remove*🗑: Remove tasks from your list when you are done \n"
    reply += "Type */start* to reset the bot\n"
    update.message.reply_text(reply, parse_mode = ParseMode.MARKDOWN)

def add(update, context):
    update.message.reply_text("Hi! What is the name of the task you would like to add?", reply_markup = markup2)
    return TASK

def getTask(update, context):
    taskName = update.message.text
    context.user_data['task'] = taskName
    update.message.reply_text(
        'When is the due date for *{}*? \nEnter in the format: _DD/MM/YYYY_'.format(taskName), reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
    return DATE

def getDate(update, context):
    date = update.message.text
    try:
        d,m,y = map(int, date.split('/'))
        validDate = datetime.date(y, m, d)
        todayDate = datetime.date.today()
        if int((validDate - todayDate).days) >= 0:
            context.user_data['date'] = date
            update.message.reply_text('What time is it due? \nEnter in the format: _HH:MM AM/PM_', reply_markup = markup2,  parse_mode = ParseMode.MARKDOWN)
            return TIME
        else:
            update.message.reply_text('Please enter a future date!', reply_markup = markup2)
            return INVALIDDATE
    except ValueError:
        update.message.reply_text('Date entered is invalid! \nPlease re-enter in the format: _DD/MM/YYYY_', reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return INVALIDDATE
    
def invalidDate(update, context):
    date = update.message.text
    try:
        d, m, y = map(int, date.split('/'))
        validDate = datetime.date(y, m, d)
        todayDate = datetime.date.today()
        if int((validDate - todayDate).days) >= 0:
            context.user_data['date'] = date
            update.message.reply_text('What time is it due? \nEnter in the format: _HH:MM AM/PM_', reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
            return TIME
        else:
            update.message.reply_text('Please enter a future date!', reply_markup = markup2)
            return INVALIDDATE
    except ValueError:
        update.message.reply_text('Date entered is invalid! \nPlease re-enter in the format: _DD/MM/YYYY_', reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return INVALIDDATE
        
def getTime(update, context):
    time = update.message.text
    date = context.user_data.get('date')
    newTime = time.lower().replace('pm', '').replace('am', '')
    validTime = newTime + ":00"

    try:
        validTime = datetime.datetime.strptime(validTime, "%H:%M:%S")
        hr, minute = map(int, newTime.split(":")) 
        if "pm" in time.lower():
            hr += 12
        now = datetime.datetime.now()
        d,m,y = map(int, date.split('/'))
        new = datetime.datetime(y, m, d, hr, minute)
        time_diff = new - now 
        if (time_diff < datetime.timedelta(0)):
            update.message.reply_text('Please enter a future time!', reply_markup = markup2)
            return INVALIDTIME
        else:
            context.user_data['time'] = time
            context.user_data['formatTime'] = str(hr) + ":" + str(minute)
            doneAdding(update, context)
            return ConversationHandler.END
    except ValueError:
        update.message.reply_text('Time entered is invalid! \nPlease enter in the format: _HH:MM AM/PM_!', reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return INVALIDTIME

#have to re-code, too slow
def invalidTime(update, context):
    time = update.message.text
    date = context.user_data.get('date')
    newTime = time.lower().replace('pm', '').replace('am', '') 
    validTime = newTime + ":00"

    try:
        validTime = datetime.datetime.strptime(validTime, "%H:%M:%S")
        hr, minute = map(int, newTime.split(":")) 
        if "pm" in time.lower():
            hr += 12
        now = datetime.datetime.now()
        d,m,y = map(int, date.split('/'))
        new = datetime.datetime(y, m, d, hr, minute)
        time_diff = new - now 
        if (time_diff < datetime.timedelta(0)):
            update.message.reply_text('Please enter a future time!', reply_markup = markup2)
            return INVALIDTIME
        else:
            context.user_data['time'] = time
            context.user_data['formatTime'] = str(hr) + ":" + str(minute)
            doneAdding(update, context)
            return ConversationHandler.END
    except ValueError:
        update.message.reply_text('Time entered is invalid!\nPlease enter in the format _HH:MM AM/PM_!', reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return INVALIDTIME

def doneAdding(update, context):
    user_data = context.user_data
    #print(user_data)
    userId = update.message.chat_id
    task = user_data.get('task')
    date = user_data.get('date')
    time = user_data.get('time')
    update.message.reply_text('*' + task + '*' + ' due on *' + date + '* at *' + 
        time + '* has been added!', reply_markup = markup, parse_mode = ParseMode.MARKDOWN)

    formattedTime = user_data.get('formatTime')
    deadline = formatDatetime(date, formattedTime)
    sm.addTask(userId, task, deadline)
    user_data.clear()


def cancel(update, context): 
    context.user_data.clear()
    update.message.reply_text("Adding of task has been cancelled, until next time!", reply_markup = markup)
    return ConversationHandler.END

def formatDatetime(date, time):
    d, m, y = map(str, date.split("/"))
    formatted = y + "/" + m + "/" + d + " " + time + ":00"
    #print(formatted)
    return formatted

def list(update, context):
    userId = update.message.chat_id
    update.message.reply_text(sm.getToDoList(userId),parse_mode = ParseMode.MARKDOWN)

def remove(update, context):
    userId = update.message.chat_id
    arr = sm.getArrayList(userId)
    keyboard= []
    
    for row in arr:
        task = row[0]
        deadline = row[1]
        time = deadline.strftime('%H:%M')
        hr, minute = map(int, time.split(':'))
        if hr > 12: #account for 12am later
            hr -= 12
            time = str(hr) + ":" + deadline.strftime('%M') + "PM"
        elif hr == 12: 
            time = str(hr) + ":" + deadline.strftime('%M') + "PM"
        else:
            time = str(hr) + ":" + deadline.strftime('%M') + "AM"
        option = "\"" + str(task) + "\"\n Due on: " + deadline.strftime('%d/%m/%Y') + " " + time 
        rawData = str(userId) + "|" + str(row[0]) + "|" + row[1].strftime('%Y/%m/%d %H:%M:%S') 
        keyboard.append([InlineKeyboardButton(str(option), callback_data = rawData)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Click on the completed task!', reply_markup=reply_markup, parse_mode = ParseMode.MARKDOWN)

def button(update, context):
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    query.answer()

    rawData = (query.data).split('|')
    sm.removeTask(rawData[0], rawData[1], rawData[2])
    replyMsg = "\"" + rawData[1] + "\" due on " + rawData[2]
    query.edit_message_text(text="Great! You have completed: \n{}".format("*" + rawData[1]+ "*"), parse_mode = ParseMode.MARKDOWN) #edit later to include deadline
    
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
    #token1 = "1163662826:AAFiWa_icg17dZYWJ3ONZ6Jd9A7VABbo5fA"
    #token2 = "1389087532:AAF_mbgxdy15TI-swWBgMB6V3ggPHrrW7tU"
    updater = Updater(token2, use_context=True)
    job = updater.job_queue
    dp = updater.dispatcher
    
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Add$'), add)],
        states={
            TASK: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), getTask)],
            DATE: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), getDate)],
            INVALIDDATE: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), invalidDate)],
            TIME: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), getTime)],
            INVALIDTIME: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), invalidTime)]
        },
        fallbacks=[MessageHandler(Filters.regex('^Cancel$'), cancel)],
        allow_reentry = True
    )
    dp.add_error_handler(error)
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("start", start))
    #dp.add_handler(CommandHandler("help", help))
    #dp.add_handler(CommandHandler("list", list))
    #dp.add_handler(CommandHandler("done", remove))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.regex('^List$'), list))
    dp.add_handler(MessageHandler(Filters.regex('^Remove'), remove))
    dp.add_handler(MessageHandler(Filters.regex('^Help$'), help))

    
    dp.add_handler(MessageHandler(Filters.text,sendlistdaily ,pass_job_queue=True))
    dp.add_handler(MessageHandler(Filters.text,sendlistmonthly ,pass_job_queue=True))
    
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=token2)
    updater.bot.setWebhook('https://peaceful-ocean-73360.herokuapp.com/' + token2)
    #updater.start_polling() test test 
    updater.idle() 

if __name__=='__main__':
    main() 

