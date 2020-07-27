import mysql.connector   
from _datetime import date
import datetime
import math
import Quotes as qt

#cnx = mysql.connector.connect(user='sql12351485', password='8dlb7NzbHF',
#                              host='sql12.freemysqlhosting.net',
#                              port='3306',
#                              database='sql12351485')

dateFormat = '%Y-%m-%d %H:%M:%S'
slotMapTime = {1: "10am - 12pm: ", 2 : "1pm - 3pm: ", 3: "4pm - 6pm: ", 4: "7pm - 9pm: "}


def getToDoList(userId):
    try:
        cnx = mysql.connector.connect(user='sql12351485', password='8dlb7NzbHF',
                              host='sql12.freemysqlhosting.net',
                              port='3306',
                              database='sql12351485')
        cursor = cnx.cursor(buffered=True)
        statement = "SELECT task, deadline FROM ToDoList WHERE userId = %s ORDER BY deadline"
        args = (userId,)

        cursor.execute(statement, args)
        result = cursor.fetchall()
        # for debugging---------------------------
        # print(result)
        # for row in result:
        #    task = row[0];
        #    deadline = row[1];

        #    print("Task: " + task + ", Deadline: " + deadline.strftime('%d-%m-%Y %H:%M:%S'))
        # ----------------------------------------
        toDoList = qt.getQuote()
        toDoList += "\nHere is the list of tasks you have!✨ \n"
        i = 1
        for row in result:
            days_left = (row[1].date() - datetime.date.today()).days
            now = datetime.datetime.now()
            time_left = row[1] - now
            diff = countDown(time_left)
            toDoList += str(i) + ") \"" + row[0] + "\" _due in_ *" + str(diff.get('days')) + "* day *" + str(
                diff.get('hours')) + "* hr *" + str(diff.get('min')) + "* min\n"
            i += 1
            # print(toDoList)
        return toDoList
    except mysql.connector.Error as e:
        print(e)
    finally:
        cnx.close()


def countDown(timeLeft):
    d = {"days": timeLeft.days}
    d["hours"], rem = divmod(timeLeft.seconds, 3600)
    d["min"], d["seconds"] = divmod(rem, 60)
    return d


def getArrayList(userId):
    try:
        cnx = mysql.connector.connect(user='sql12351485', password='8dlb7NzbHF',
                              host='sql12.freemysqlhosting.net',
                              port='3306',
                              database='sql12351485')

        cursor = cnx.cursor()
        statement = "SELECT task, deadline FROM ToDoList WHERE userId = %s ORDER BY deadline"
        args = (userId,)
        cursor.execute(statement, args)
        result = cursor.fetchall()
        # for debugging----------
        for row in result:
            rawData = str(row[0]) + "|" + row[1].strftime('%Y-%m-%d %H:%M:%S')
            #print(rawData)
        # -----------------------
        return result
    except mysql.connector.Error as e:
        print(e)
    finally:
        cnx.close()


def getDoneList(userId):
    try:
        cnx = mysql.connector.connect(user='sql12351485', password='8dlb7NzbHF',
                              host='sql12.freemysqlhosting.net',
                              port='3306',
                              database='sql12351485')

        cursor = cnx.cursor()
        statement = "SELECT task, deadline FROM ToDoList WHERE userId = %s"
        args = (userId,)
        cursor.execute(statement, args)
        result = cursor.fetchall()

        DoneList = "Done list: \n"
        for row in result:
            DoneList += row[0] + "\n"
        return DoneList
    
    except mysql.connector.Error as e:
        print(e)
    finally:
        print("DoneList done")
        cnx.close()


def duplicateTask(userId, task, deadline):
    try:
        cnx = mysql.connector.connect(user='sql12351485', password='8dlb7NzbHF',
                              host='sql12.freemysqlhosting.net',
                              port='3306',
                              database='sql12351485')

        cursor = cnx.cursor()
        statement = "SELECT COUNT(*) FROM ToDoList WHERE userId = %s AND task = %s AND deadline = %s"
        args = (userId, task, deadline) 
        cursor.execute(statement, args)
        result = cursor.fetchall()
        #print(result[0][0])
        if result[0][0] >= 1:
            return True
        else:
            return False
    except Exception as e:
        print(e)
    finally:
        cnx.close()

def addTask(userId, task, deadline):
    print("Server manager add task executed")

    try:
        cnx = mysql.connector.connect(user='sql12351485', password='8dlb7NzbHF',
                              host='sql12.freemysqlhosting.net',
                              port='3306',
                              database='sql12351485')
        cursor = cnx.cursor()
        statement = "INSERT INTO ToDoList(task, deadline, userId) VALUES (%s, %s, %s)"
        args = (task, deadline, userId)
        cursor.execute(statement, args)
    except mysql.connector.Error as e:
        print(e)
    finally:
        cnx.commit()
        cnx.close()



def removeTask(userId, task, deadline):
    # print("remove task")

    try:
        cnx = mysql.connector.connect(user='sql12351485', password='8dlb7NzbHF',
                              host='sql12.freemysqlhosting.net',
                              port='3306',
                              database='sql12351485')
        cursor = cnx.cursor()
        statement = "DELETE FROM ToDoList WHERE userId = %s AND task = %s AND deadline = %s "
        args = (userId, task, deadline)
        cursor.execute(statement, args)
    except mysql.connector.Error as e:
        print(e)
    finally:
        cnx.commit()
        cnx.close()


def removeAllOverdue(userId):
  
    try:
        cnx = mysql.connector.connect(user='sql12351485', password='8dlb7NzbHF',
                              host='sql12.freemysqlhosting.net',
                              port='3306',
                              database='sql12351485')

        curr = (datetime.datetime.now())
        new_curr = curr.strftime('%Y-%m-%d %H:%M:%S')
        cursor = cnx.cursor()
        statement = "SELECT * FROM ToDoList WHERE userId = %s AND deadline < \"" + new_curr + "\""
        args = (userId,)
        cursor.execute(statement, args)
        result = cursor.fetchall()
        overdueList = ""

        for row in result:
            time = row[1].strftime('%H:%M')
            hr, minute = map(int, time.split(':'))
            if hr > 12: #account for 12am later
                hr -= 12
                time = str(hr) + ":" + row[1].strftime('%M') + "pm"
            elif hr == 12: 
                time = str(hr) + ":" + row[1].strftime('%M') + "pm"
            else:
                time = str(hr) + ":" + row[1].strftime('%M') + "am"
            overdueList += "'_" + row[0] + "_' due on _" + row[1].strftime('%d/%m/%Y') + " " + time + "_\n"
        
        statement = "DELETE FROM ToDoList WHERE deadline < '" + new_curr + "'"
        cursor.execute(statement)
    except mysql.connector.Error as e:
        print(e)
    finally:
        cnx.commit()
        cnx.close()
        return overdueList

def editTaskName(new, rawData, userId):
    try:
        #print(rawData)
        cnx = mysql.connector.connect(user='sql12351485', password='8dlb7NzbHF',
                              host='sql12.freemysqlhosting.net',
                              port='3306',
                              database='sql12351485')

        rawData = rawData.split('|')
        oldName = rawData[1]
        deadline = rawData[2]
        cursor = cnx.cursor()
        statement = "Update ToDoList SET task = %s WHERE userId = %s AND deadline = %s AND task = %s"
        args = (new, userId, deadline, oldName)
        cursor.execute(statement, args)
    except mysql.connector.Error as e:
        print(e)
    finally:
        cnx.commit() 
        cnx.close()

def editTaskDate(new, rawData, userId):
    try:
        cnx = mysql.connector.connect(user='sql12351485', password='8dlb7NzbHF',
                              host='sql12.freemysqlhosting.net',
                              port='3306',
                              database='sql12351485')

  
        rawData = rawData.split('|')
        name = rawData[1]
        deadline = rawData[2]

        time = deadline.split()[1]
        new_deadline = str(new) + " " + time
        cursor = cnx.cursor()
        statement = "Update ToDoList SET deadline = %s WHERE userId = %s AND deadline = %s AND task = %s"
        args = (new_deadline, userId, deadline, name)
        cursor.execute(statement, args)
        return new_deadline
    except mysql.connector.Error as e:
        print(e)
    finally:
        cnx.commit() 
        cnx.close()

def editTaskTime(new, rawData, userId):
    try:
        cnx = mysql.connector.connect(user='sql12351485', password='8dlb7NzbHF',
                              host='sql12.freemysqlhosting.net',
                              port='3306',
                              database='sql12351485')

        rawData = rawData.split('|')
        name = rawData[1]
        deadline = rawData[2]

        date = deadline.split()[0]
        new_deadline = date + " " + new
        cursor = cnx.cursor()
        statement = "Update ToDoList SET deadline = %s WHERE userId = %s AND deadline = %s AND task = %s"
        args = (new_deadline, userId, deadline, name)
        cursor.execute(statement, args)
        return new_deadline
    except mysql.connector.Error as e:
        print(e)
    finally:
        cnx.commit() 
        cnx.close()

def insertSchedule(schedule, userId):
    try:
        cnx = mysql.connector.connect(user='sql12351485', password='8dlb7NzbHF',
                              host='sql12.freemysqlhosting.net',
                              port='3306',
                              database='sql12351485')

        cursor = cnx.cursor()
        for key in schedule:
            modForDate = schedule.get(key)
            print(modForDate)
            i = 1 #represent slotNum
            for mod in modForDate:
                statement = "INSERT INTO Schedule(userId, module, date, slotNum) VALUES (%s, %s, %s, %s)"
                args = (userId, mod, key, i)
                cursor.execute(statement, args)
                print("ID: " + str(userId) + " | Mod: " + mod + " Date: | " + key.strftime('%d/%m/%y') +  " Slot : " + str(i))
                i += 1
    except mysql.connector.Error as e:
        print(e)
        print('Error at: insertSchedule')
    finally:
        cnx.commit()
        cnx.close()


def deleteExistingSchedule(userId):
    try:
        cnx = mysql.connector.connect(user='sql12351485', password='8dlb7NzbHF',
                              host='sql12.freemysqlhosting.net',
                              port='3306',
                              database='sql12351485')
        cursor = cnx.cursor()
        statement = "DELETE FROM Schedule WHERE userId = %s"
        args = (userId,)
        cursor.execute(statement, args)
    except mysql.connector.Error as e:
        print(e)
        print('Error at: deleteSchedule')
    finally:
        cnx.commit()
        cnx.close()

def retrieveDaySch(userId):
    try:
        cnx = mysql.connector.connect(user='sql12351485', password='8dlb7NzbHF',
                              host='sql12.freemysqlhosting.net',
                              port='3306',
                              database='sql12351485')
        
        cursor = cnx.cursor()
        now = datetime.datetime.now()
        curr = now.strftime('%Y-%m-%d')
        curr = curr + " 00:00:00"
        print(curr)
        statement = "SELECT module, slotNum FROM Schedule WHERE date = %s AND userId = %s"
        args = (curr, userId)
        cursor.execute(statement, args)
        result = cursor.fetchall()
        #print(result)

        if len(result) == 0:
            print("No exam revision schedule")
            return False
        else:
            reply = "Today's revision schedule is: \n"
            for row in result:
                reply += slotMapTime.get(row[1]) + row[0] + "\n" 
                
                if row[1] != 4:
                    reply += " _(1hr break)_ \n"
            return reply
    except mysql.connector.Error as e:
        print(e)
        print('Error at: retreiveDay')
    finally:
        cnx.close()
