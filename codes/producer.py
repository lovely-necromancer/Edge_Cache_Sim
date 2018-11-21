from node import Node
import linecache
from decorators import debug
import random
from packet import DataPacket , InterestPacket
from globals import time , timeComparator, getTime , addTime , logging

class Producer(Node):

    currentdata = ""
    nextdata = ""
    nextdataline = 1
    lastUpdate = None
    datafile = None
    frequency = None


    def __init__(self, name, memorySize, totalPower, processingPowerUnit, transmissionPowerUnit, frequency, arch):
        
        Node.__init__(self, name, memorySize, totalPower, processingPowerUnit, transmissionPowerUnit,arch)
        self.datafile = name + ".txt"
        self.residualCacheSize = self.memorySize
        self.frequency = frequency


    @debug
    def updateState(self):
        cd = self.currentdata
        if self.currentdata == "":
            file = open(self.datafile, 'r')
            self.currentdata = file.readline()
            self.nextdata = file.readline()
            self.nextdataline += 1
            file.close()
        else:
            result = timeComparator(self.nextdata.split(',')[1])
            if result == -1:
                self.currentdata = self.nextdata
                self.nextdata = linecache.getline(self.datafile, self.nextdataline)
                self.nextdataline += 1
        if cd != self.currentdata:
            logging.debug(self.name + " " + self.currentdata)

    @debug
    def updateStateByFrequency(self):
        cd = self.currentdata
        if self.currentdata == "":
            file = open(self.datafile, 'r')
            self.currentdata = file.readline()
            self.nextdata = file.readline()
            self.nextdataline += 1
            self.lastUpdate = time.timeInSeconds
            file.close()
        else:
            result = timeComparator(addTime(self.frequency, self.lastUpdate, 0))
            if result == -1:
                self.currentdata = linecache.getline(self.datafile, self.nextdataline)
                self.nextdataline += 1
                self.lastUpdate = time.timeInSeconds
        if cd != self.currentdata:
            logging.debug(self.name + " " + self.currentdata)

    @debug
    def processIncomingPackets(self):

        for faceName, face in self.inputFaces.items():
            self.facesFlags[faceName] = False
        for faceName, face in self.inputFaces.items():
            # logging.debug( self.name +" -- "+ faceName + "  " + str(face))
            packet = face.popleft()
            if packet != "0":
                self.inputLoad+=1
                if packet.__class__ is InterestPacket:  # it is interest
                    if packet.name == self.name:
                        self.sendResponse(packet, faceName)
                    else:
                        self.forwardInterestPacket(packet, faceName)
                else:
                    self.forwardDataPacket(packet, faceName)

    @debug
    def processIncomingPacketsNoCache(self):

        for faceName, face in self.inputFaces.items():
            self.facesFlags[faceName] = False
        for faceName, face in self.inputFaces.items():
            # logging.debug(self.name + " -- " + faceName + "  " + str(face))
            packet = face.popleft()
            if packet != "0":
                self.inputLoad += 1
                if packet.__class__ is InterestPacket:  # it is interest
                    if packet.name == self.name:
                        self.sendResponse(packet, faceName)
                    else:
                        self.forwardInterestPacketNoCache(packet, faceName)
                else:
                    self.forwardDataPacketNoCache(packet, faceName)

    @debug
    def processIncomingPacketsHalfCache(self):

        for faceName, face in self.inputFaces.items():
            self.facesFlags[faceName] = False
        for faceName, face in self.inputFaces.items():
            # logging.debug(self.name + " -- " + faceName + "  " + str(face))
            packet = face.popleft()
            if packet != "0":
                self.inputLoad += 1
                if packet.__class__ is InterestPacket:  # it is interest
                    if packet.name == self.name:
                        self.sendResponse(packet, faceName)
                    else:
                        self.forwardInterestPacket(packet, faceName)
                else:
                    self.forwardDataPacketHalfCache(packet, faceName)

    @debug
    def processIncomingPacketsPcasting(self):

        for faceName, face in self.inputFaces.items():
            self.facesFlags[faceName] = False
        for faceName, face in self.inputFaces.items():
            # logging.debug( self.name +" -- "+ faceName + "  " + str(face))
            packet = face.popleft()
            if packet != "0":
                self.inputLoad += 1
                if packet.__class__ is InterestPacket:  # it is interest
                    if packet.name == self.name:
                        self.sendResponse(packet, faceName)
                    else:
                        self.forwardInterestPacket(packet, faceName)
                else:
                    self.forwardDataPacketPcasting(packet, faceName)

    @debug
    def processIncomingPacketsPathCache(self):

        for faceName, face in self.inputFaces.items():
            self.facesFlags[faceName] = False
        for faceName, face in self.inputFaces.items():
            # logging.debug( self.name +" -- "+ faceName + "  " + str(face))
            packet = face.popleft()
            if packet != "0":
                self.inputLoad += 1
                if packet.__class__ is InterestPacket:  # it is interest
                    if packet.name == self.name:
                        self.sendResponse(packet, faceName)
                    else:
                        self.forwardInterestPacketPathCache(packet, faceName)
                else:
                    self.forwardDataPacketPathCache(packet, faceName)
                    

    @debug
    def sendResponse(self, interestpacket, faceName):
        self.residualPower -= 1
        # logging.debug( "packet " , packet.name , "send response"
        self.updateState()
        npacket = DataPacket(interestpacket.name, self.frequency, self.currentdata, time.timeInSeconds , interestpacket.pathCache)
        self.sendOut(npacket, faceName)

    

    