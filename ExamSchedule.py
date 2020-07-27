#id, userId, module, weight
#block = 2h | 10am-12pm, 1pm-3pm, 4pm-6pm, 7pm-9pm (10)
#Start recess week - Start of exam

import datetime as dt
from datetime import timedelta as td
import math

DAY_SLOTS = ['10am-12pm', '1pm-3pm', '4pm-6pm', '7pm-9pm']

def getSlots(recessStartStr, recessEndStr, subjectWeightList): #subjectWeightList - Dict<Subject: String, weight: Double>
    recessStart = dt.datetime.strptime(recessStartStr, '%d/%m/%Y')
    recessEnd = dt.datetime.strptime(recessEndStr, '%d/%m/%Y')
    noOfDays = (recessEnd - recessStart).days
    if noOfDays <= 0:
        print("Invalid recess span")
        return None
    totalNoOfBlocks = noOfDays * len(DAY_SLOTS)
    totalNoOfSubjects = len(subjectWeightList.keys())
    totalWeight = sum(subjectWeightList.values()) #Get total weight
    
    #Get understated number of blocks (i.e. rounded down blocks)
    calculated_SBList = {} #Dict<Subject: String, Understated no. of blocks: Int>
    for subject, weight in subjectWeightList.items():
        calculated_SBList[subject] = math.floor(weight/totalWeight * totalNoOfBlocks)
        #print(f"{subject}: {calculated_SBList[subject]}")

    totalUnderstatedWeight = sum(calculated_SBList.values()) #Get total understated blocks
    
    #Distribute remaining blocks | Precedence: Zero blocks, From the highest weighted subject
    remainingBlocks = totalNoOfBlocks - totalUnderstatedWeight
    sortedImportanceSubjectList = list(map(lambda item: item[0], sorted(subjectWeightList.items(), key=lambda x: x[1], reverse=True))) 
    
    for subject, weight in calculated_SBList.items(): #Handles: Zero blocks
        if remainingBlocks > 0 and weight == 0:
            calculated_SBList[subject] += 1
            remainingBlocks -= 1
    
    while remainingBlocks > 0: #Handles: From the highest weighted subject
        for subject in sortedImportanceSubjectList: 
            if remainingBlocks > 0:
                calculated_SBList[subject] += 1
                remainingBlocks -= 1
    
    #Re-distribute to Zero block subjects
    zeroSubjectList = list({ s: b for s, b in calculated_SBList.items() if b == 0 }.keys()) #Subjects with zero blocks
    no_distribution = False #Fail safe

    while len(zeroSubjectList) > 0 and no_distribution == False:
        no_distribution = True
        for subject in sortedImportanceSubjectList: 
            if len(zeroSubjectList) > 0 and calculated_SBList[subject] > 1:
                calculated_SBList[subject] -= 1 #Subtract
                calculated_SBList[zeroSubjectList.pop()] += 1 #Add to zero block subject
                no_distribution = False

    #DEBUG: Check Assigned slots
    checkTotalBlocks = 0
    for subject, blocks in calculated_SBList.items():
        print(f"{subject}: {blocks}")
        checkTotalBlocks += blocks
    print(f"Days: { noOfDays } | Success: { totalNoOfBlocks == checkTotalBlocks } | Total no of blocks: {totalNoOfBlocks} | Total assigned blocks: {checkTotalBlocks} | Subjects: { totalNoOfSubjects } | Total weight: {totalWeight}")
    
    print(calculated_SBList)
         
    revisionPeriod = []
    curr = recessStart
    while curr < recessEnd:
        revisionPeriod.append(curr)
        curr = curr + td(days=1)
        #print(curr)
    
    #print(revisionPeriod)
    
    schedule = {}
    for i in range(len(revisionPeriod)):
        schedule[revisionPeriod[i]] = []
        
    #print(schedule)
    dateKey = recessStart
    for subject, blocks in sorted(calculated_SBList.items(), key=lambda x: x[1], reverse=True):
        #print("Subject: " + subject + " | num: " + str(blocks))
        slotted = 0
        numblocks = blocks
        while slotted < blocks:
            for dateKey in schedule:
                #print(dateKey)
                space = len(schedule.get(dateKey))
                if space < 4 and slotted < numblocks:
                    schedule.get(dateKey).append(subject)
                    slotted += 1
                    #print("Subject: " + str(subject) + " | Sorted: " + str(slotted))
                    #print(schedule)
                dateKey = dateKey + td(days=1)
    
    print(schedule)
    return schedule, calculated_SBList #dictionary {key = datetime obj: values = modules to revise on that day}

#generate reply
slotMapTime = {1: "10am - 12pm: ", 2 : "1pm - 3pm: ", 3: "4pm - 6pm: ", 4: "7pm - 9pm: "}
def generateText(schedule, modBlocks):
    totalHours = "_Total Hours\n"
    for mod in modBlocks:
        hours = modBlocks.get(mod) * 2
        totalHours += mod + ":" + str(hours) + "\n"
    
    totalHours += "_"
  
    reply = "*Exam Revision Schedule* 🤓 \n" + totalHours + "\n"
    
    for date in schedule: #key = yyyy-mm-dd HH:MM:SS
        #dateOnly = key.split()[0]
        #date = dt.datetime.strptime(dateOnly, '%Y-%m-%d')
        dateStr = date.strftime("%d/%m/%y")
        reply+= "*" + dateStr + "*\n"
        modForDate = schedule.get(date)
        i = 1
        for mod in modForDate:
            reply += slotMapTime.get(i) + mod + "\n"
            if i != 4:
                reply += " _(1hr break)_ \n"
            i += 1
    print(reply) 
    return reply


