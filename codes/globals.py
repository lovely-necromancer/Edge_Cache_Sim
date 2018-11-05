import logging

logging.basicConfig(filename='example.log',level=logging.DEBUG)

def getTime():
    return str(time.hours) + ":" + str(time.minutes) + ":" + str(time.seconds)

def timeComparator( ttime):  # ttime < time => -1 , ttime > time => 1 , ttime = time => 0

    arr = ttime.split(":")
    thour = int(arr[0])
    tminute = int(arr[1])
    tsecond = int(arr[2])

    if thour < time.hours:
        result = -1
    elif thour > time.hours:
        result = 1
    elif tminute < time.minutes:
        result = -1
    elif tminute > time.minutes:
        result = 1
    elif tsecond < time.seconds:
        result = -1
    elif tsecond > time.seconds:
        result = 1
    else:
        result = 0
    return result

def addTime( second , t , flag):
    if flag ==1 :
        arr = t.split(":")
        thour = int(arr[0])
        tminute = int(arr[1])
        tsecond = int(arr[2])
        minutes = ((second + tsecond) / 60) + tminute
        seconds = (second + tsecond) % 60
        hours = (minutes / 60) + thour
        minutes = minutes % 60
    else:
        t += second
        minutes = ((second + t) / 60)
        seconds = (second + t) % 60
        hours = (minutes / 60)
        minutes = minutes % 60

    return str(hours) + ":" + str(minutes) + ":" + str(seconds)

def plusSimulationTime():
    time.timeInSeconds += 1
    time.seconds += 1
    time.minutes += time.seconds / 60
    time.seconds = time.seconds % 60
    time.hours += time.minutes / 60
    time.minutes = time.minutes % 60


class time:

    timeInSeconds = 0
    seconds = 0
    minutes = 0
    hours = 0



