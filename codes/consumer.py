from node import Node
import random
from decorators import debug
import random
from packet import DataPacket , InterestPacket
from globals import time , timeComparator, getTime , addTime , logging

class Consumer (Node):

    interestName = ""

    lastRequestTime = None
    lastRequestTimeInsec = None
    nextRequestTime = None

    totalWaitingTime = None
    numberOfresponses = None

    defaultFace = None

    def __init__(self ,name , memorySize, totalPower , processingPowerUnit , transmissionPowerUnit , arch ):

        Node.__init__(self ,name , memorySize, totalPower , processingPowerUnit , transmissionPowerUnit , arch)
        self.interestName = name.split(':')[1]

        self.totalWaitingTime = 0
        self.numberOfresponses = 0


    @debug
    def requestGenerator ( self ):      # this function needs to get time of the day!
        lr = self.lastRequestTime
        if self.lastRequestTime == None:
            rand = random.randint(5 , 50)

            if timeComparator("00:00:" + str(rand)) == -1:
                npacket = InterestPacket (self.interestName , 0.5 , time.timeInSeconds)
                self.sendRequest(npacket)
                self.lastRequestTime = getTime()
                self.lastRequestTimeInsec = time.timeInSeconds
                rand = random.randint( 20 , 60)
                self.nextRequestTime = addTime(rand , getTime(), 1)
        else:
            if timeComparator(self.nextRequestTime) == -1:
                npacket = InterestPacket(self.interestName, 0.5 , time.timeInSeconds)
                self.sendRequest(npacket)
                self.lastRequestTime = getTime()
                self.lastRequestTimeInsec = time.timeInSeconds
                rand = random.randint(20, 60)
                self.nextRequestTime = addTime(rand , getTime(), 1)
        if lr != self.lastRequestTime:
            logging.debug( self.name + "  " + self.lastRequestTime)

    @debug
    def sendRequest (self , interestPacket):
        self.residualPower -= 1
        outGoingFace = self.fib[interestPacket.name]
        if outGoingFace != None:
            self.sendOut(interestPacket , outGoingFace)
        else:
            #self.sendOut(packet , None)
            print ""

    @debug
    def processIncomingPackets(self):

        for faceName, face in self.inputFaces.items():
            self.facesFlags[faceName] = False
        for faceName, face in self.inputFaces.items():
            #logging.debug(self.name + " -- " + faceName + "  " + str(face))
            packet = face.popleft()
            if packet != "0":
                self.inputLoad += 1
                if packet.__class__ is DataPacket:  # it is data
                    if packet.name == self.interestName:
                        logging.debug(self.name + " : my data Recieved ****")  # it must be changed
                        now = time.timeInSeconds
                        self.totalWaitingTime += now - self.lastRequestTimeInsec
                        self.numberOfresponses += 1
                    else:
                        self.forwardDataPacket(packet, faceName)
                else:
                    self.forwardInterestPacket(packet, faceName)

    def processIncomingPacketsHalfCache(self):

        for faceName, face in self.inputFaces.items():
            self.facesFlags[faceName] = False
        for faceName, face in self.inputFaces.items():
            #logging.debug(self.name + " -- " + faceName + "  " + str(face))
            packet = face.popleft()
            if packet != "0":
                self.inputLoad += 1
                if packet.__class__ is DataPacket:  # it is data
                    if packet.name == self.interestName:
                        logging.debug(self.name + " : my data Recieved ****")  # it must be changed
                        now = time.timeInSeconds
                        self.totalWaitingTime += now - self.lastRequestTimeInsec
                        self.numberOfresponses += 1

                    else:
                        self.forwardDataPacketHalfCache(packet, faceName)
                else:
                    self.forwardInterestPacket(packet, faceName)


    @debug
    def processIncomingPacketsNoCache (self):

        for faceName , face in self.inputFaces.items():
            self.facesFlags[faceName] = False
        for faceName, face in self.inputFaces.items():
            #logging.debug( self.name +" -- " + faceName + "  " + str(face))
            packet = face.popleft()
            if packet != "0":
                self.inputLoad += 1
                if packet.__class__ is DataPacket:   # it is data
                    if packet.name == self.interestName:
                        logging.debug( self.name + " : my data Recieved ****" )          # it must be changed
                        now = time.timeInSeconds
                        self.totalWaitingTime += now - self.lastRequestTimeInsec
                        self.numberOfresponses +=1

                    else:
                        self.forwardDataPacketNoCache( packet , faceName)
                else:
                    self.forwardInterestPacketNoCache(packet , faceName)

    @debug
    def processIncomingPacketsPcasting(self):

        for faceName, face in self.inputFaces.items():
            self.facesFlags[faceName] = False
        for faceName, face in self.inputFaces.items():
            # logging.debug(self.name + " -- " + faceName + "  " + str(face))
            packet = face.popleft()
            if packet != "0":
                self.inputLoad += 1
                if packet.__class__ is DataPacket:  # it is data
                    if packet.name == self.interestName:
                        logging.debug(self.name + " : my data Recieved ****")  # it must be changed
                        now = time.timeInSeconds
                        self.totalWaitingTime += now - self.lastRequestTimeInsec
                        self.numberOfresponses += 1

                    else:
                        self.forwardDataPacketPcasting(packet, faceName)
                else:
                    self.forwardInterestPacket(packet, faceName)

    @debug
    def processIncomingPacketsPathCache(self):

        for faceName, face in self.inputFaces.items():
            self.facesFlags[faceName] = False
        for faceName, face in self.inputFaces.items():
            # logging.debug(self.name + " -- " + faceName + "  " + str(face))
            packet = face.popleft()
            if packet != "0":
                self.inputLoad += 1
                if packet.__class__ is DataPacket:  # it is data
                    if packet.name == self.interestName:
                        logging.debug(self.name + " : my data Recieved ****")  # it must be changed
                        now = time.timeInSeconds
                        self.totalWaitingTime += now - self.lastRequestTimeInsec
                        self.numberOfresponses += 1

                    else:
                        self.forwardDataPacketPathCache(packet, faceName)
                else:
                    self.forwardInterestPacketPathCache(packet, faceName)