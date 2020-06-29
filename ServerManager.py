import mysql.connector   
from _datetime import date
import datetime

cnx = mysql.connector.connect(user='root', password='root',
                              host='127.0.0.1',
                              port='8889',
                              database='Cronus')

dateFormat = '%Y-%m-%d %H:%M:%S'

def getToDoList(userId):
    try:
        cursor = cnx.cursor()
        statement = "SELECT task, deadline, isCompleted FROM ToDoList WHERE userId = %s AND isCompleted = 0"
        args = (userId,)
        
        cursor.execute(statement, args)
        result = cursor.fetchall()
        #for debugging---------------------------
        #print(result)
        #for row in result:
        #    task = row[0];
        #    deadline = row[1];
            
        #    print("Task: " + task + ", Deadline: " + deadline.strftime('%d-%m-%Y %H:%M:%S'))
        #----------------------------------------
        toDoList = "\"_Today is your opportunity to build the tomorrow you want.” \n- Ken Poirot_ \n"
        toDoList += "\nHere is the list of task you have, spend your day productively!✨ \n"
        i = 1
        for row in result:
            days_left = (row[1].date() - datetime.date.today()).days
            now = datetime.datetime.now()
            time_left = row[1] - now
            diff = countDown(time_left)
            toDoList += str(i) + ") \"" + row[0] + "\" _due in_ *" + str(diff.get('days')) + "* day *" + str(diff.get('hours')) + "* hr *" + str(diff.get('min')) + "* min\n"
            i += 1
            #print(toDoList)  
        return toDoList
    finally:
        print()


#remember to chang
def countDown(timeLeft):
    d = {"days": timeLeft.days}
    d["hours"], rem = divmod(timeLeft.seconds, 3600)
    d["min"], d["seconds"] = divmod(rem, 60)
    return d

def getArrayList(userId):
    try:
        cursor = cnx.cursor()
        statement = "SELECT task, deadline, isCompleted FROM ToDoList WHERE userId = %s AND isCompleted = 0"
        args = (userId,)
        cursor.execute(statement, args)
        result = cursor.fetchall()
        #for debugging----------
        for row in result:
            rawData = str(userId) + "|" + str(row[0]) + "|" + row[1].strftime('%Y-%m-%d %H:%M:%S') 
            print(rawData)
        #-----------------------    
        return result
    finally: 
        print('')

def getDoneList(userId):
    try:
        cursor = cnx.cursor()
        statement = "SELECT task, deadline, isCompleted FROM ToDoList WHERE userId = %s AND isCompleted = 1"
        args = (userId,)
        cursor.execute(statement, args)
        result = cursor.fetchall()

        DoneList = "Done list: \n"
        for row in result:
            DoneList += row[0] + "\n"  
        return DoneList 
    finally:
        print("DoneList done")

def addTask(userId, task, deadline):

    #print("Server manager add task executed")
    
    try: 
        cursor = cnx.cursor()
        statement = "INSERT INTO ToDoList(task, deadline, isCompleted, userId) VALUES (%s, %s, %s, %s)"
        args = (task, deadline, 0, userId) 
        cursor.execute(statement, args)
    finally:
        cnx.commit()

def removeTask(userId, task, deadline):
    #print("remove task")
    
    try: 
        cursor = cnx.cursor()
        statement = """UPDATE ToDoList 
                     SET isCompleted = 1 
                     WHERE userId = %s AND task = %s AND deadline = %s """  
        args = (userId, task, deadline)   
        cursor.execute(statement, args)
    finally:
        cnx.commit()
