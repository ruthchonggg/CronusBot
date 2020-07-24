import logging
import datetime
import ServerManager as sm

from datetime import timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackQueryHandler
from ServerManager import getToDoList
from pytz import timezone

TOKEN = "1163662826:AAFiWa_icg17dZYWJ3ONZ6Jd9A7VABbo5fA"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)

#State definitions for add
TASK, DATE, INVALIDDATE, TIME, INVALIDTIME = range(5)

#State definitions for edit
START, SELECT_CAT, EDIT_DATE, EDIT_TIME, EDIT_TASK, INVALID_DATE, INVALID_TIME, DONE_EDIT = map(chr, range(8))

END = ConversationHandler.END

#keyboards
reply_keyboard = [['List', 'Add','Remove','Edit']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = True, one_time_keyboard = False)

keyboard2 = [['Cancel']]
markup2 = ReplyKeyboardMarkup(keyboard2, resize_keyboard = True, one_time_keyboard = True)

editKb = [['Task', 'Date', 'Time']]
markup3 = ReplyKeyboardMarkup(editKb, resize_keyboard = True, one_time_keyboard = True)

cont = [['Yes', 'No']]
markup4 = ReplyKeyboardMarkup(cont, resize_keyboard = True, one_time_keyboard = True)



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

#add convo
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
    date = date.strip()
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
    date = date.strip()
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
    newTime = newTime.strip()
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
    newTime = newTime.strip()
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

#cancelAdd
def cancelAdd(update, context): 
    context.user_data.clear()
    update.message.reply_text("Adding of task has been cancelled, until next time!", reply_markup = markup)
    return ConversationHandler.END
 
#return keyboard of the list of task
def getList(arr, userId, func):
    keyboard = []
    for row in arr:
        task = row[0]
        deadline = row[1]
        time = deadline.strftime('%H:%M')
        hr, minute = map(int, time.split(':'))
        if hr > 12: #account for 12am later
            hr -= 12
            time = str(hr) + ":" + deadline.strftime('%M') + " pm"
        elif hr == 12: 
            time = str(hr) + ":" + deadline.strftime('%M') + " pm"
        else:
            time = str(hr) + ":" + deadline.strftime('%M') + " am"
        option = "\"" + str(task) + "\"\n Due on: " + deadline.strftime('%d/%m/%Y') + " " + time 
        rawData = func + "|" + str(userId) + "|" + str(row[0]) + "|" + row[1].strftime('%Y/%m/%d %H:%M:%S')
        #print(rawData)
        keyboard.append([InlineKeyboardButton(str(option), callback_data = rawData)])
    
    return keyboard

#convert original datetime into more readable format 
def datetime_user(datetime):
    arr = datetime.split()
    date = arr[0]
    date = date.replace("-","/")
    y,m,d = map(str, date.split('/'))
    date = d + '/' + m + '/' + y 
    time = arr[1]
    hr, mins, sec = map(str, time.split(':'))
    if int(hr) > 12:
        hr = int(hr) - 12
        time = str(hr) + ":" + mins + "PM"
    elif int(hr) == 12:
        time = hr + ":" + mins + "PM"
    else:
        time = hr + ":" + mins + "AM" 
    return date + " " + time


def edit(update, context):
    userId = update.message.chat_id
    context.user_data['id'] = userId
    context.user_data['msgId'] = update.message.message_id
    arr = sm.getArrayList(userId)
    keyboard = getList(arr, userId, 'e')
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Click on the task you want to edit', reply_markup=reply_markup)
    return START

#Callbackqueryhandler for edit function
def editCallBack(update, context):
    query = update.callback_query
    query.answer()
    
    context.user_data['editTask'] = query.data #store userdate
    data = query.data.split('|')
    date = (data[3].split())[0]
    y,m,d = map(str, date.split('/'))
    time = (data[3].split())[1]
    hr, min, s = map(str, time.split(':'))
    if int(hr) > 12: 
        hr = int(hr) - 12
        time = str(hr) + ":" + str(min) + "PM"
    elif int(hr) == 12: 
            time = str(hr) + ":" + str(min) + "PM"
    else:
        time = str(hr) + ":" + str(min) + "AM"
    deadline = d + "/" + m + "/" + y + " " + time
    reply = "Editing <*{}* _due on_ *{}*>".format(data[2], deadline)
    reply += '\n \nWhich category would you like to edit?'
    context.bot.delete_message(chat_id=context.user_data.get('id'), message_id=query.message.message_id)
    context.bot.send_message(chat_id=context.user_data.get('id'),
                             text=reply, 
                             parse_mode = ParseMode.MARKDOWN,
                             reply_markup = markup3)
    return SELECT_CAT

def selectCategory(update, context):
    context.bot.send_message(chat_id=context.user_data.get('id'),
                             text="Which category would you like to edit?", 
                             parse_mode = ParseMode.MARKDOWN,
                             reply_markup = markup3)
    return SELECT_CAT

def inputTask(update, context):
    newName = update.message.text
    sm.editTaskName(newName, context.user_data.get('editTask'))

    #update in user_data
    raw = context.user_data['editTask']
    raw = raw.split('|')
    old_name = raw[2]
    new_data = "e|" + raw[1] + '|' + newName + '|' + raw[3] 
    context.user_data['editTask'] = new_data
    #print('==' + new_data)
    reply = "Sucessfully updated to *" + newName + "* due on *" + datetime_user(raw[3]) + "* \nContinue editing current task?"
    update.message.reply_text(reply, parse_mode = ParseMode.MARKDOWN, reply_markup = markup4)
    return DONE_EDIT


def choosingCategory(update, context):
    context.user_data['cat'] = update.message.text
    cat = context.user_data.get('cat')

    if cat == 'Date':
        update.message.reply_text('Enter new date in the format DD/MM/YYYY', reply_markup = markup2)
        return EDIT_DATE
    elif cat == 'Time':
        update.message.reply_text('Enter the new time in 12-hr format HR:MIN', reply_markup = markup2)
        return EDIT_TIME
    elif cat == 'Task':
        update.message.reply_text('Enter the new task name', reply_markup = markup2)
        return EDIT_TASK


def inputDate(update, context):
    date = update.message.text
    date = date.strip()

    try:
        d, m, y = map(int, date.split('/'))
        validDate = datetime.date(y, m, d)
        todayDate = datetime.date.today()
        if int((validDate - todayDate).days) < 0:
            update.message.reply_text('Please enter a future date', reply_markup = markup2)
            return INVALID_DATE
        else:
            #update database
            raw = context.user_data.get('editTask')
            new_deadline = sm.editTaskDate(validDate, raw)

            #update user_data
            raw = raw.split('|')
            new_data = "e|" + raw[1] + '|' + raw[2] + '|' + new_deadline
            context.user_data['editTask'] = new_data 

            new_datetime = datetime_user(new_deadline)
            reply = "Sucessfully updated to *" + raw[1] + "* due on *" + new_datetime + "* \nContinue editing current task?"
            update.message.reply_text(reply, parse_mode = ParseMode.MARKDOWN, reply_markup = markup4)
            return DONE_EDIT

    except ValueError:
        update.message.reply_text('Date entered is invalid!\nPlease re-enter in the format: _DD/MM/YYYY_',
                                  reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return INVALID_DATE

def inputTime(update, context):
    time = update.message.text
    raw = context.user_data.get('editTask')
    date = ((raw.split('|')[3]).split())[0]
    newTime = time.lower().replace('pm', '').replace('am', '')
    newTime = newTime.strip() #remove spaces in string
    validTime = newTime + ":00"

    try:
        validTime = datetime.datetime.strptime(validTime, "%H:%M:%S")
        hr, mins = map(str, newTime.split(':')) 
        if ("pm" in time.lower()) and (hr != '12'):
            hr = int(hr) + 12
        validTime = str(hr) + ':' + mins + ':00'
        
        #check if time is of the future
        now = datetime.datetime.now()
        y,m,d = map(int, date.split('/'))
        new = datetime.datetime(y, m, d, int(hr), int(mins))
        time_diff = new - now 
        
        if (time_diff < datetime.timedelta(0)):
            update.message.reply_text('Please enter a future time!', reply_markup = markup2)
            return INVALID_TIME
        else:
            #update database
            raw = context.user_data.get('editTask')
            new_deadline = sm.editTaskTime(validTime, raw)
            raw = raw.split('|')
            new_data = "e|" + raw[1] + '|' + raw[2] + '|' + new_deadline
            context.user_data['editTask'] = new_data
            reply = "Sucessfully updated to *" + raw[1] + "* due on *" + datetime_user(new_deadline) + "* \nContinue editing current task?"
            update.message.reply_text(reply, parse_mode = ParseMode.MARKDOWN, reply_markup = markup4)
            return DONE_EDIT
    except ValueError:
        update.message.reply_text('Time entered is invalid!\nPlease enter in the format _HH:MM AM/PM_!', reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return INVALID_TIME

def done(update, context):
    context.user_data.clear()
    return ConversationHandler.END

def formatDatetime(date, time):
    d, m, y = map(str, date.split("/"))
    formatted = y + "/" + m + "/" + d + " " + time + ":00"
    return formatted

def list(update, context):
    userId = update.message.chat_id
    update.message.reply_text(sm.getToDoList(userId),parse_mode = ParseMode.MARKDOWN)

def remove(update, context):
    userId = update.message.chat_id
    arr = sm.getArrayList(userId)
    buttons = getList(arr, userId, 'r')
    buttons.append([InlineKeyboardButton(text = 'Remove all overdue tasks', 
                                  callback_data = "r all|" + str(userId))])
    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Click on the completed task!', reply_markup = keyboard)
    
def removeButton(update, context):
    #print('call back')
    query = update.callback_query
    query.answer()

    data = query.data
    rawData = (data).split('|')
    print(rawData)
    remove_all = rawData[0]

    if 'all' in remove_all:
        overdueList = sm.removeAllOverdue(rawData[1])
        reply = "Great! You have completed: \n" + overdueList
        query.edit_message_text(text=reply, parse_mode = ParseMode.MARKDOWN)
    else:
        sm.removeTask(rawData[1], rawData[2], rawData[3])
        replyMsg = "\"" + rawData[2] + "\" due on " + datetime_user(rawData[3])
        query.edit_message_text(text="Great! You have completed: \n " + replyMsg, parse_mode = ParseMode.MARKDOWN)
    
def dailytimer(update, context):
    print("reminders activated")
    date1 = datetime.datetime(2020, 7, 6, 5, 36)
    date2 = datetime.datetime(2020, 7,6, 5, 37)
    sg = timezone('Asia/Singapore')
    morn = sg.localize(date1)
    night = sg.localize(date2)

    context.job_queue.run_daily(sendlistdaily,morn.time(),context=update.message.chat_id)
    context.job_queue.run_daily(sendlistdaily,night.time(),context=update.message.chat_id)
    
def sendlistdaily(context):
    print("sending reminder")
    context.bot.send_message(chat_id=context.job.context, 
                             text = sm.getToDoList(context.job.context),
                             parse_mode = ParseMode.MARKDOWN)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater(TOKEN, use_context=True)
    job = updater.job_queue
    dp = updater.dispatcher
    
    add_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Add$'), add)],
        states={
            TASK: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), getTask)],
            DATE: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), getDate)],
            INVALIDDATE: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), invalidDate)],
            TIME: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), getTime)],
            INVALIDTIME: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), invalidTime)]
        },
        fallbacks=[MessageHandler(Filters.regex('^Cancel$'), cancelAdd)],
        allow_reentry = True
    )

    edit_handler = ConversationHandler(
        entry_points = [MessageHandler(Filters.regex('^Edit$'), edit)],

        states = {
            START: [CallbackQueryHandler(editCallBack, pattern = '^e')],
            SELECT_CAT: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), choosingCategory)],
            EDIT_DATE: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), inputDate)],
            EDIT_TIME: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), inputTime)],
            INVALID_DATE: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), inputDate)],
            INVALID_TIME: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), inputTime)],
            EDIT_TASK: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), inputTask)],
            DONE_EDIT: [MessageHandler(Filters.regex('^Yes$'), selectCategory),
                        MessageHandler(Filters.regex('^No$'), done)],
        },

        fallbacks = [MessageHandler(Filters.regex('^Cancel$'),done)],
        allow_reentry = True,
    )
    dp.add_error_handler(error)
    dp.add_handler(CallbackQueryHandler(removeButton, pattern = '^r'))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(add_handler)
    dp.add_handler(edit_handler)
    dp.add_handler(MessageHandler(Filters.regex('^List$'), list))
    dp.add_handler(MessageHandler(Filters.regex('^Remove'), remove))
    dp.add_handler(MessageHandler(Filters.regex('^Help$'), help))
    dp.add_handler(CommandHandler("reminders", dailytimer, pass_job_queue = True))
  
    dp.add_handler(edit_handler)
    


    updater.start_polling()
    updater.idle() 

if __name__=='__main__':
    main() 

