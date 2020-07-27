import logging
import datetime
import ServerManager as sm
import os
import schedule
import telegram
import ExamSchedule as examsch

from threading import Thread
from time import sleep
from datetime import timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackQueryHandler
from ServerManager import getToDoList
from pytz import timezone

TOKEN = '1389087532:AAF_mbgxdy15TI-swWBgMB6V3ggPHrrW7tU'
bot = telegram.Bot(TOKEN)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)

#State definitions for add
#TASK, TASK_LIMIT, DATE, INVALIDDATE, TIME, INVALIDTIME, DONE_ADD = range(7)
TASK, TASK_LIMIT, DATE, TIME, DONE_ADD = range(5)

#State definitions for edit
START, SELECT_CAT, EDIT_DATE, EDIT_TIME, EDIT_TASK, MAX_LIMIT, INVALID_DATE, INVALID_TIME, DONE_EDIT = map(chr, range(9))
END = ConversationHandler.END

#State definitions for exam
RECESSDATE,EXAMDATE,EXAM,LEVEL = range(4)
lvlmapweight = {3 : 1.25, 2 : 1, 1 : 0.75}


#State definitions for todayGoals
TODAY_TASK, DONE_TODAY = range(2)

#keyboards
reply_keyboard = [['List', 'Add','Remove','Edit'],['TodayGoals','Exam', 'Help']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = True, one_time_keyboard = False)

keyboard2 = [['Cancel']]
markup2 = ReplyKeyboardMarkup(keyboard2, resize_keyboard = True, one_time_keyboard = True)

editKb = [['Task', 'Date', 'Time']]
markup3 = ReplyKeyboardMarkup(editKb, resize_keyboard = True, one_time_keyboard = True)

cont = [['Yes', 'No']]
markup4 = ReplyKeyboardMarkup(cont, resize_keyboard = True, one_time_keyboard = True)

dc = [['Done','Cancel']]
markup5 = ReplyKeyboardMarkup(dc, resize_keyboard = True, one_time_keyboard = True)


def start(update, context):
    reply = " Hi there, I'm Cronus and I can help you to keep track of your tasks and manage your time wisely!⌛️ \n \n"
    reply += "Here are some buttons and commands that you may find useful: \n"
    reply += "*List*📝: Get the list of tasks you have \n"
    reply += "*Add*➕: Add tasks to your list \n"
    reply += "*Remove*🗑: Remove tasks from your list when you are done \n"
    reply += "*Edit*🔧: Edit current tasks \n"
    reply += "*TodayGoals*🎯: List down the tasks that you aim to complete today \n"
    reply += "*Exam*🤓: Generate your exam revision schedule \n"
    reply += "*/reminder*🔔: Receive reminders regarding your to do list at 8am and 8pm daily\n"
    reply += "*/off*🔕: Turn off daily reminders\n"
    reply += "*Help*🔍: Get information regarding Cronus \n\n"
    reply += "Let’s start by clicking on the *Add* button!"
    userId = update.message.chat_id
    context.bot.send_message(chat_id=update.message.chat_id, text=reply, parse_mode = ParseMode.MARKDOWN,
                             reply_markup = markup)

def help(update, context):
    reply = "Here are some buttons and commands that you may find useful: \n\n"
    reply += "*List*📝: Get the list of tasks you have \n"
    reply += "*Add*➕: Add tasks to your list \n"
    reply += "*Remove*🗑: Remove tasks from your list when you are done \n"
    reply += "*Edit*🔧: Edit current tasks \n"
    reply += "*TodayGoals*🎯: List down the tasks that you aim to complete today \n"
    reply += "*Exam*🤓: Generate your exam revision schedule \n"
    reply += "*/reminder*🔔: Receive reminders regarding your to do list at 8am and 8pm daily\n"
    reply += "*/off*🔕: Turn off daily reminders\n"
    reply += "*Help*🔍: Get information regarding Cronus \n"
    update.message.reply_text(reply, parse_mode = ParseMode.MARKDOWN)

def exam(update, context):
    
    reply = "Hi there, Cronus will aid you in planning your revision schedule🗓 Let's begin by entering the date your recess week starts!\n\n *Enter*: dd/mm/yyyy"
    update.message.reply_text(reply, reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
    return RECESSDATE

def getRecessDate(update, context):
    date = update.message.text
    date = date.strip()
    try:
        d,m,y = map(int, date.split('/'))
        validDate = datetime.date(y, m, d)
        todayDate = datetime.date.today()
        if int((validDate - todayDate).days) >= 0:
            context.user_data['recessdate'] = date
            reply = "Okay got it! How about the date of your first exam?\n\n*Enter*: _dd/mm/yyyy_"
            update.message.reply_text(reply, reply_markup = markup2,  parse_mode = ParseMode.MARKDOWN)
            return EXAMDATE
        else:
            update.message.reply_text("Please enter a future date\n\n*Enter*: _dd/mm/yyyy_", 
                                      reply_markup=markup2)
            return RECESSDATE
    except ValueError:
        update.message.reply_text("Date entered is invalid\n\n*Enter*: _dd/mm/yyyy_'", reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return RECESSDATE

def getExamDate(update, context):
    date = update.message.text
    date = date.strip()
    try:
        d, m, y = map(int, date.split('/'))
        validDate = datetime.date(y, m, d)
        todayDate = datetime.date.today()
        recess = context.user_data.get('recessdate')
        recessStart = datetime.datetime.strptime(recess, '%d/%m/%Y')
        examDate = datetime.datetime.strptime(date, '%d/%m/%Y')
        daysToExam = (examDate - recessStart).days

        if int((validDate - todayDate).days) >= 0 and daysToExam > 0:
            context.user_data['examdate'] = date
            reply = "What module you would like to add?\n\n*Enter*: Module name"
            update.message.reply_text(reply, reply_markup=markup2,
                                      parse_mode=ParseMode.MARKDOWN)
            context.user_data['mod:weight'] = {}
            return EXAM
        elif daysToExam <= 0:
            update.message.reply_text("Date of your first exam must be after the start of recess week \n*Enter*: _dd/mm/yyyy_", reply_markup=markup2, parse_mode = ParseMode.MARKDOWN)
            return EXAMDATE
        else:
            update.message.reply_text("Please enter a future date\n\n*Enter*: _dd/mm/yyyy_", reply_markup=markup2, parse_mode = ParseMode.MARKDOWN)

            return EXAMDATE
    except ValueError:
        update.message.reply_text("Date entered is invalid\n\n*Enter*: _dd/mm/yyyy_", reply_markup=markup2, parse_mode=ParseMode.MARKDOWN)
        return EXAMDATE

def addExam(update, context):
    moduleName = update.message.text
    context.user_data['currMod'] = moduleName
    reply = "Rank the importance/difficulty of the module, with *'3'* being the most _important/difficult_ and *'1'* being the _least important/difficult_. \n\n*Enter*: 3/2/1"
    update.message.reply_text(reply,reply_markup=markup2,parse_mode=ParseMode.MARKDOWN)
    return LEVEL
    
def addLevel(update,context):
    level = update.message.text
    level = level.strip()

    if level != '1' and level != '2' and level != '3':
        reply = "Rank the importance/difficulty of the module, with *'3'* being the most _important/difficult_ and *'1'* being the _least important/difficult_. \n\n*Enter*: 3/2/1"
        update.message.reply_text(reply,parse_mode=ParseMode.MARKDOWN)
        return LEVEL
    else:
        module_dict = context.user_data.get('mod:weight')
        currMod = context.user_data.get('currMod')
        module_dict[currMod] = lvlmapweight.get(int(level))
        reply = "What module you would like to add? Enter or click 'Done' when you are done entering all the modules ✔️ \n\n*Enter*: Module name"
        update.message.reply_text(reply, reply_markup=markup5,
                                  parse_mode=ParseMode.MARKDOWN)
        return EXAM

def doneExam(update, context):
    module_dict = context.user_data.get('mod:weight')
    print(module_dict)
    recessStart = context.user_data.get('recessdate')
    examStart = context.user_data.get('examdate')
    schedule, modBlocks = examsch.getSlots(recessStart, examStart, module_dict)
    reply = examsch.generateText(schedule, modBlocks)
    update.message.reply_text(reply, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
 
    #update database
    sm.deleteExistingSchedule(update.message.chat_id)
    sm.insertSchedule(schedule, update.message.chat_id)
    context.user_data.clear()
    return ConversationHandler.END
    
#add convo
def add(update, context):
    update.message.reply_text("Hey there! What is the name of the task you would like to add?", reply_markup = markup2)
    return TASK

def getTask(update, context):
    taskName = update.message.text

    if len(taskName) <= 42:
        context.user_data['task'] = taskName
        update.message.reply_text('When is *{}* due?\n*Enter*: _dd/mm/yyyy_'.format(taskName), reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return DATE
    else:
        update.message.reply_text("Exceeded max characters of 42, please re-enter", reply_markup = markup2)
        return TASK_LIMIT

def getDate(update, context):
    date = update.message.text
    date = date.strip()

    try:
        d,m,y = map(int, date.split('/'))
        validDate = datetime.date(y, m, d)
        todayDate = datetime.date.today()
        if int((validDate - todayDate).days) >= 0:
            context.user_data['date'] = date
            update.message.reply_text('What time is it due?\n*Enter*: _hh:mm am/pm_ (12hr format)', reply_markup = markup2,  parse_mode = ParseMode.MARKDOWN)
            return TIME
        else:
            update.message.reply_text('Please enter a future date!', reply_markup = markup2)
            return DATE
    except ValueError:
        update.message.reply_text("Date entered is invalid\n*Enter*: _dd/mm/yyyy_", reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return DATE
    
def getTime(update, context):
    time = update.message.text
    time = time.lower()

    if ("pm" not in time) and ("am" not in time):
        update.message.reply_text("Time entered is invalid!\n*Enter*: _hh:mm am/pm_ (12hr format)", reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return TIME
        
    date = context.user_data.get('date')
    newTime = time.replace('pm', '').replace('am', '')
    newTime = newTime.strip()
    validTime = newTime + ":00"

    try:
        validTime = datetime.datetime.strptime(validTime, "%H:%M:%S")
        hr, minute = map(int, newTime.split(":")) 
        if "pm" in time.lower() and hr != 12:
            hr += 12
        now = datetime.datetime.now()
        d,m,y = map(int, date.split('/'))
        new = datetime.datetime(y, m, d, hr, minute)
        time_diff = new - now 
        if (time_diff < datetime.timedelta(0)):
            update.message.reply_text('Please enter a future time!', reply_markup = markup2)
            return TIME
        else:
            context.user_data['time'] = time
            context.user_data['formatTime'] = str(hr) + ":" + str(minute)
            doneAdding(update, context)
            update.message.reply_text('Continue adding tasks?', reply_markup = markup4)
            return DONE_ADD
    except ValueError:
        update.message.reply_text("Time entered is invalid!\n*Enter*: _hh:mm am/pm_ (12hr format)", reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return TIME

#===rmbr to delete
def doneAdding(update, context):
    user_data = context.user_data
    #print(user_data)
    userId = update.message.chat_id
    task = user_data.get('task')
    date = user_data.get('date')
    time = user_data.get('time')
    formattedTime = user_data.get('formatTime')
    deadline = formatDatetime(date, formattedTime)

    if (sm.duplicateTask(userId, task, deadline)) == True:
        reply = "There is already an existing task, adding of \"_" + task + "_\"" + " due on _" + date + "_ at _" + time + "_ has been cancelled"
        update.message.reply_text(reply, parse_mode = ParseMode.MARKDOWN)
    else:
        sm.addTask(userId, task, deadline)
        update.message.reply_text('\"_' + task + '\"_' + ' due on _' + date + '_ at _' + 
        time + '_ has been added!', parse_mode = ParseMode.MARKDOWN)

    user_data.clear()

def cancel(update, context): 
    context.user_data.clear()
    update.message.reply_text("Adding of task has been cancelled, until next time!", reply_markup = markup)
    return ConversationHandler.END

def examcancel(update, context): 
    context.user_data.clear()
    update.message.reply_text("Generating exam revision schedule has been cancelled, until next time!", reply_markup = markup)
    return ConversationHandler.END

def formatDatetime(date, time):
    d, m, y = map(str, date.split("/"))
    formatted = y + "/" + m + "/" + d + " " + time + ":00"
    #print(formatted)
    return formatted

#return keyboard of the list of tasks
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
        rawData = func + "|" + str(row[0]) + "|" + row[1].strftime('%Y/%m/%d %H:%M:%S')
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

#Edit: Edit exisiting tasks
def edit(update, context):
    userId = update.message.chat_id
    context.user_data['id'] = userId
    context.user_data['msgId'] = update.message.message_id
    arr = sm.getArrayList(userId)
    keyboard = getList(arr, userId, 'e')
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Hi there, click on the task you want to edit. \n_(Type 'Cancel' if you wish to exit)_", reply_markup=reply_markup)
    return START

def editCallBack(update, context):
    query = update.callback_query
    query.answer()
    
    context.user_data['editTask'] = query.data
    data = query.data.split('|')
    date = (data[2].split())[0]
    y,m,d = map(str, date.split('/'))
    time = (data[2].split())[1]
    hr, min, s = map(str, time.split(':'))
    if int(hr) > 12: 
        hr = int(hr) - 12
        time = str(hr) + ":" + str(min) + "PM"
    elif int(hr) == 12: 
        time = str(hr) + ":" + str(min) + "PM"
    else:
        time = str(hr) + ":" + str(min) + "AM"
    deadline = d + "/" + m + "/" + y + " " + time
    reply = "Editing '_{}_' due on _{}_".format(data[1], deadline)
    reply += '\n\nWhich category would you like to edit?'
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
    userId = update.message.chat_id

    #number of characters
    if len(newName) <= 42:
        sm.editTaskName(newName, context.user_data.get('editTask'), userId)
        #update in user_data
        raw = context.user_data['editTask']
        raw = raw.split('|')
        new_data = "e|" + newName + '|' + raw[2]
        context.user_data['editTask'] = new_data
        reply = "Sucessfully updated to *" + newName + "* due on *" + datetime_user(raw[2]) + "* \nContinue editing current task?"
        update.message.reply_text(reply, parse_mode = ParseMode.MARKDOWN, reply_markup = markup4)
        return DONE_EDIT
    else:
        update.message.reply_text("Exceeded max characters of 42, please re-enter", reply_markup = markup2)
        return MAX_LIMIT

def choosingCategory(update, context):
    context.user_data['cat'] = update.message.text
    cat = context.user_data.get('cat')

    if cat == 'Date':
        update.message.reply_text('What is the new due date?\n*Enter*: _dd/mm/yyyy_', reply_markup = markup2, parse_mode = ParseMode.MARKDOWN,)
        return EDIT_DATE
    elif cat == 'Time':
        update.message.reply_text('What is the new time?\n*Enter*: _hh:mm am/pm_ (12hr format)', reply_markup = markup2, parse_mode = ParseMode.MARKDOWN,)
        return EDIT_TIME
    elif cat == 'Task':
        update.message.reply_text('What is the new task name?', reply_markup = markup2)
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
            dateStr = validDate.strftime('%Y/%m/%d')
            new_deadline = sm.editTaskDate(dateStr, raw, update.message.chat_id)

            #update user_data
            raw = raw.split('|')
            new_data = "e|" + raw[1] + '|' + new_deadline
            context.user_data['editTask'] = new_data 
            new_datetime = datetime_user(new_deadline)
            reply = "Sucessfully updated to *" + raw[1] + "* due on *" + new_datetime + "* \nContinue editing current task?"
            update.message.reply_text(reply, parse_mode = ParseMode.MARKDOWN, reply_markup = markup4)
            return DONE_EDIT

    except ValueError:
        update.message.reply_text("Date entered is invalid\n*Enter*: _dd/mm/yyyy_",
                                  reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return INVALID_DATE

def inputTime(update, context):
    time = update.message.text
    raw = context.user_data.get('editTask')
    date = ((raw.split('|')[2]).split())[0]
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
            new_deadline = sm.editTaskTime(validTime, raw, update.message.chat_id)
            raw = raw.split('|')
            new_data = "e|" + raw[1] + '|' + new_deadline
            context.user_data['editTask'] = new_data
            reply = "Sucessfully updated to *" + raw[1] + "* due on *" + datetime_user(new_deadline) + "* \nContinue editing current task?"
            update.message.reply_text(reply, parse_mode = ParseMode.MARKDOWN, reply_markup = markup4)
            return DONE_EDIT
    except ValueError:
        update.message.reply_text("Time entered is invalid!\n*Enter*: _hh:mm am/pm_ (12hr format)", reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return INVALID_TIME

def done(update, context):
    update.message.reply_text('Until next time!',reply_markup=markup)
    context.user_data.clear()
    return ConversationHandler.END

#List
def list(update, context):
    userId = update.message.chat_id
    reply = sm.getToDoList(userId)
    revisionSch = sm.retrieveDaySch(userId)
    if revisionSch != False:
        reply += "\n" + revisionSch
    update.message.reply_text(reply,parse_mode = ParseMode.MARKDOWN)

#Remove: remove tasks
def remove(update, context):
    userId = update.message.chat_id
    context.user_data['id'] = userId
    arr = sm.getArrayList(userId)
    buttons = getList(arr, userId, 'r')
    buttons.append([InlineKeyboardButton(text = 'Remove all overdue tasks', 
                                  callback_data = "r all|" + str(userId))])
    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Hi there, click on the completed task!', reply_markup = keyboard)

def removeButton(update, context):
    #print('call back')
    query = update.callback_query
    query.answer()

    data = query.data
    chat_id = context.user_data.get('id')
    rawData = (data).split('|')
    remove_all = rawData[0]

    if 'all' in remove_all:
        overdueList = sm.removeAllOverdue(chat_id)
        reply = "Great👏🏻 You have completed: \n" + overdueList
        query.edit_message_text(text=reply, parse_mode = ParseMode.MARKDOWN)
    else:
        sm.removeTask(chat_id, rawData[1], rawData[2])
        replyMsg = "\"_" + rawData[1] + "_\" due on _" + datetime_user(rawData[2]) + "_"
        query.edit_message_text(text="Great👏🏻 You have completed: \n " + replyMsg, parse_mode = ParseMode.MARKDOWN)
        
#TodayGoals: Set daily task
def todayTask(update, context):
    reply = "List down your goals for today!📝 \n\n*Enter*:Task 1;Task 2;Task 3;Task 4\n(_My apologies, Cronus is still learning, please do not click on 'return' to go to the next line_)"
    update.message.reply_text(reply, reply_markup = markup2, parse_mode=ParseMode.MARKDOWN)
    return TODAY_TASK

def saveToday(update, context):
    today_goals = (update.message.text).split(";")
    reply = "Today's goal is to complete 🎯 " + "\n\n"
    for goal in today_goals:
        reply += "✔️" + goal.lstrip(' ') + "\n"

    #context.user_data['todayGoals'] = today_goals
    print(reply)
    update.message.reply_text(reply, reply_markup = markup)
    return ConversationHandler.END


#Activate notifications
def dailytimer(update, context):

    if 'morn_job' not in context.chat_data:
        update.message.reply_text('Turning on reminders, Cronus will send you your to-do-list at 8am and 8pm daily!🔔')
        date1 = datetime.datetime(2020, 7, 6, 8, 00)
        date2 = datetime.datetime(2020, 7, 24, 20, 00)
        sg = timezone('Asia/Singapore')
        morn = sg.localize(date1)
        night = sg.localize(date2)
    
        morn_context = str(update.message.chat_id) + "|m"
        night_context = str(update.message.chat_id) + "|n"
        morn_job = context.job_queue.run_daily(sendlistdaily,morn.time(), days=tuple(range(7)), 
                                               context=morn_context)
        night_job = context.job_queue.run_daily(sendlistdaily,night.time(), days=tuple(range(7)), 
                                                context=night_context)
        context.chat_data['morn_job'] = morn_job
        context.chat_data['night_job'] = night_job
        print("Reminder activated!!!")
    else:
        update.message.reply_text("Reminders has been turned on already, Cronus will send your to-do-list at 8am and 8pm daily!🔔")
        print("Activated alr")

#Send notification
def sendlistdaily(context):
    print("sending reminder")
    data = context.job.context
    userId = data.split("|")[0]
    msg_type = data.split("|")[1]
    print("sending reminder to: " + str(userId) + msg_type)
    reply = sm.getToDoList(userId) 
    revisionSch = sm.retrieveDaySch(userId)
    
    if revisionSch != False:
        reply += "\n" + revisionSch
        
    if 'm' in msg_type:
        reply += "\nRise and shine 🐣 ☀️ Click on 'TodayGoals' to set your goals for today!"
    else:
        reply += "\nClick on the 'Remove' button to remove tasks that you have completed! Hope you have spent your day productively, rest well！😴"

    context.bot.send_message(userId, 
                             text = reply,
                             parse_mode = ParseMode.MARKDOWN)

def offnotif(update, context):
    if 'morn_job' not in context.chat_data:
        update.message.reply_text('Reminders has not been turned on')
    else:
        morn_job = context.chat_data['morn_job']
        night_job = context.chat_data['night_job']
        morn_job.schedule_removal()
        night_job.schedule_removal()
        update.message.reply_text('Reminders has been turned off 🔕')
        chatData = context.chat_data
        chatData.pop('morn_job')
        chatData.pop('night_job')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
   #sm.creatTable()
    updater = Updater(TOKEN, use_context=True)
    job = updater.job_queue
    dp = updater.dispatcher

    add_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Add$'), add)],
        states={
            TASK: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), getTask)],
            TASK_LIMIT: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), getTask)],
            DATE: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), getDate)],
            TIME: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), getTime)],
            DONE_ADD: [MessageHandler(Filters.regex('^Yes$'), add),
                       MessageHandler(Filters.regex('^No$'), done)],

        },
        fallbacks=[MessageHandler(Filters.regex('^Cancel$'), cancel)],
        allow_reentry = True
    )

    exam_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Exam$'), exam)],
        states={
            RECESSDATE: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), getRecessDate)],
            EXAMDATE : [MessageHandler(Filters.regex('^((?!Cancel).)*$'), getExamDate)],
            EXAM : [MessageHandler(Filters.regex('^Done$'), doneExam),
                    MessageHandler(Filters.regex('^((?!Cancel).)*$'), addExam)],  
            LEVEL: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), addLevel)]
        },
         fallbacks=[MessageHandler(Filters.regex('^Cancel$'), examcancel),
                   MessageHandler(Filters.regex('^Done$'), doneExam)],
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
            MAX_LIMIT: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), inputTask)],
            DONE_EDIT: [MessageHandler(Filters.regex('^Yes$'), selectCategory),
                        MessageHandler(Filters.regex('^No$'), done)],
        },

        fallbacks = [MessageHandler(Filters.regex('^Cancel$'),done)],
        allow_reentry = True,
    )

    dailyTasks_handler = ConversationHandler(
        entry_points = [MessageHandler(Filters.regex('^TodayGoals$'), todayTask)],

        states = {
            TODAY_TASK: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), saveToday)],
        },

        fallbacks = [MessageHandler(Filters.regex('^Cancel$'),done)],
        allow_reentry = True,
    )

    dp.add_error_handler(error)
    dp.add_handler(add_handler)
    dp.add_handler(exam_handler)
    dp.add_handler(edit_handler)
    dp.add_handler(dailyTasks_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(removeButton, pattern = '^r'))
    dp.add_handler(MessageHandler(Filters.regex('^List$'), list))
    dp.add_handler(MessageHandler(Filters.regex('^Remove$'), remove))
    dp.add_handler(MessageHandler(Filters.regex('^Help$'), help))
    dp.add_handler(CommandHandler("reminder", dailytimer, pass_job_queue = True, pass_chat_data = True))
    dp.add_handler(CommandHandler("off", offnotif, pass_job_queue = True, pass_chat_data = True))

    PORT = int(os.environ.get('PORT', '8443'))
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://whispering-falls-53932.herokuapp.com/' + TOKEN)
    #updater.start_polling()
    updater.idle() 

if __name__=='__main__':
    main() 



