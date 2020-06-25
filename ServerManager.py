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
        #for debugging--------------------------------------
        print(result)
        for row in result:
            task = row[0];
            deadline = row[1];
            
            print("Task: " + task + ", Deadline: " + deadline.strftime('%d-%m-%Y %H:%M:%S'))
        #----------------------------------------
        toDoList = ""
        
        for row in result:
            days_left = (row[1].date() - datetime.date.today()).days
            
            toDoList += row[0] + " (" + str(days_left) + " days left)" + "\n"
        print(toDoList)  
        return toDoList
    finally:
        print()
        #cnx.close()

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
        cnx.close()

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
    
    try: 
        cursor = cnx.cursor()
        statement = "INSERT INTO ToDoList(task, deadline, isCompleted, userId) VALUES (%s, %s, %s, %s)"
        args = (task, deadline, 0, userId) 
        cursor.execute(statement, args)
    finally:
        cnx.commit()

def removeTask(userId, task, deadline):
    print("remove task")
    try: 
        cursor = cnx.cursor()
        statement = """UPDATE ToDoList 
                     SET isCompleted = 1 
                     WHERE userId = %s AND task = %s AND deadline = %s """  
        args = (userId, task, deadline)   
        cursor.execute(statement, args)
    finally:
        cnx.commit()
