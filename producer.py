from packet import Packet
import linecache
import random
from globals import logging, timeComparator, time, addTime, getTime
from decorators import debug

class Producer:

    name = ""

    memorySize = None

    totalPower = None
    residualPower = None
    processingPowerUnit = None
    transmissionPowerUnit = None

    ArchitectureLevel = None
    cacheHit = None
    cacheMiss = None

    currentdata = ""
    nextdata = ""
    nextdataline = 1
    lastUpdate = None
    datafile = None
    frequency = None

    facesFlags = None     # key is interest name and value is face flag
    inputFaces = None          # key is interest name and value is face queue
    outputFaces = None

    fib = None    # key is interest name and value is face name

    pit = None    # { interest name : { 'inface' : "1" , 'outface' : "3"  , 'freshness' : "400" }}

    cs = None    # { name : { 'packet' : "dklsfj" , 'freshness' : "ksdfi" , 'residuallifetime' : "kldsf" , 'size' : "kldf" , 'hit ratio' : "adlfk" ,'lastAccess' = "dskflj" , 'ref' = "points to memory"}}

    cacheMemory = None      # it may not work correctly

    # cache arch implementation

    def __init__(self, name, memorySize, totalPower, processingPowerUnit, transmissionPowerUnit, arch):
        self.name = name
        self.memorySize = int(memorySize)
        self.totalPower = int(totalPower)
        self.residualPower = int(totalPower)
        self.processingPowerUnit = int(processingPowerUnit)
        self.transmissionPowerUnit = int(transmissionPowerUnit)
        self.ArchitectureLevel = arch
        self.datafile = name + ".txt"
        self.cacheHit = 0
        self.cacheMiss = 0

        self.inputFaces= {}
        self.outputFaces = {}
        self.facesFlags = {}
        self.fib = {}
        self.pit = {}
        self.cs = {}
        self.cacheMemory = [ False] * self.memorySize


    def initialFib (self , *array):
        for i in range ( 1 , len(array) , 2):
            self.fib[array[i]] = array[i + 1]

    def run(self):
        self.processIncomingPackets()
        self.updateState()
        self.processOutgoingpackets()

    @debug
    def updateState (self):
        cd = self.currentdata
        if self.currentdata == "":
            file = open(self.datafile , 'r')
            self.currentdata = file.readline()
            self.nextdata = file.readline()
            self.nextdataline +=1
            file.close()
        else:
            result = timeComparator(self.nextdata.split(',')[1])
            if result == -1:
                self.currentdata = self.nextdata
                self.nextdata = linecache.getline(self.datafile , self.nextdataline)
                self.nextdataline+=1
        if cd != self.currentdata:
            logging.debug( self.name +" " + self.currentdata)

    @debug
    def updateStateByFrequency (self):
        cd = self.currentdata
        if self.currentdata == "":
            file = open(self.datafile, 'r')
            self.currentdata = file.readline()
            self.nextdata = file.readline()
            self.nextdataline += 1
            self.lastUpdate = time.timeInSeconds
            file.close()
        else:
            result = timeComparator( addTime(self.frequency , self.lastUpdate , 0))
            if result == -1:
                self.currentdata = linecache.getline(self.datafile, self.nextdataline)
                self.nextdataline += 1
                self.lastUpdate = time.timeInSeconds
        if cd != self.currentdata:
            logging.debug(self.name + " " + self.currentdata)

    @debug
    def processIncomingPackets (self):

        for faceName , face in self.inputFaces.items():
            self.facesFlags[faceName] = False
        for faceName, face in self.inputFaces.items():
            logging.debug( self.name +" -- "+ faceName + "  " + str(face))
            packet = face.popleft()
            if packet != "0":
                if not packet.isData:   # it is interest
                    if packet.name == self.name:
                        self.sendResponse( packet , faceName)
                    else:
                        self.forwardInterestPacket( packet , faceName)
                else:
                    self.forwardDataPacket(packet , faceName)

    @debug
    def processIncomingPacketsNoCache(self):

        for faceName, face in self.inputFaces.items():
            self.facesFlags[faceName] = False
        for faceName, face in self.inputFaces.items():
            logging.debug(self.name + " -- " + faceName + "  " + str(face))
            packet = face.popleft()
            if packet != "0":
                if not packet.isData:  # it is interest
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
            logging.debug(self.name + " -- " + faceName + "  " + str(face))
            packet = face.popleft()
            if packet != "0":
                if not packet.isData:  # it is interest
                    if packet.name == self.name:
                        self.sendResponse(packet, faceName)
                    else:
                        self.forwardInterestPacket(packet, faceName)
                else:
                    self.forwardDataPacketHalfCache(packet, faceName)

    @debug
    def sendResponse (self , packet , faceName):
        self.residualPower-=1
        #logging.debug( "packet " , packet.name , "send response"
        self.updateState()
        npacket = Packet ( packet.name , True , time.timeInSeconds , self.currentdata , packet.generatedTime )
        self.sendOut(npacket , faceName)


    @debug
    def forwardInterestPacket (self , packet , faceName):
        self.residualPower -= 1
        interestName = packet.name
        outgoingFaceName = self.fib[interestName]
        if self.cs.__contains__(interestName) and packet.freshness < self.cs[interestName]['freshness'] :
            logging.debug( self.name + ": sending interest packet "+ packet.name +  " back from cs (CACHE HIT!)")
            print ( self.name + ": sending interest packet "+ packet.name + " " + str(packet.freshness )+  " back from cs (CACHE HIT!)")
            self.sendOut(self.cs[interestName]['packet'], faceName)
            self.cs[interestName]['lastAccess'] = time.timeInSeconds
            self.cs[interestName]['hitRatio'] +=1
            self.cacheHit+=1

        # we must forward data
        elif self.pit.__contains__(interestName):
            containsEntryFlag = False
            table = self.pit[interestName]
            self.cacheMiss+=1
            for array in table:
                if array[0] == faceName and array[1] == outgoingFaceName:
                    containsEntryFlag = True
            if not containsEntryFlag:
                table.append ([ faceName , outgoingFaceName , packet.freshness])
                # it is forward
                logging.debug( self.name+ " : forward interest packet "+ packet.name+ " to "+ outgoingFaceName)
                print (self.name+ " : forward interest packet "+ packet.name+ " to "+ outgoingFaceName + " pit contains")
                self.sendOut(packet , outgoingFaceName)
        else:
            # it is forward
            self.cacheMiss+=1
            logging.debug( self.name+ " : forward interest packet "+ packet.name+ " to "+ outgoingFaceName)
            print ( self.name+ " : forward interest packet "+ packet.name+ " to "+ outgoingFaceName + " pit doesn't contains")
            self.sendOut(packet , outgoingFaceName)
            self.pit[interestName] = []
            self.pit[interestName].append([ faceName , outgoingFaceName , packet.freshness])

    @debug
    def forwardInterestPacketNoCache(self, packet, faceName):
        self.residualPower -= 1
        interestName = packet.name
        outgoingFaceName = self.fib[interestName]

        # we must forward data
        if self.pit.__contains__(interestName):
            containsEntryFlag = False
            table = self.pit[interestName]
            self.cacheMiss += 1
            for array in table:
                if array[0] == faceName and array[1] == outgoingFaceName:
                    containsEntryFlag = True
            if not containsEntryFlag:
                table.append([faceName, outgoingFaceName, packet.freshness])
                # it is forward
                logging.debug(self.name + " : forward interest packet " + packet.name + " to " + outgoingFaceName)
                print (
                            self.name + " : forward interest packet " + packet.name + " to " + outgoingFaceName + " pit contains")
                self.sendOut(packet, outgoingFaceName)
        else:
            # it is forward
            self.cacheMiss += 1
            logging.debug(self.name + " : forward interest packet " + packet.name + " to " + outgoingFaceName)
            print (
                        self.name + " : forward interest packet " + packet.name + " to " + outgoingFaceName + " pit doesn't contains")
            self.sendOut(packet, outgoingFaceName)
            self.pit[interestName] = []
            self.pit[interestName].append([faceName, outgoingFaceName, packet.freshness])

    @debug
    def forwardDataPacket (self , packet , faceName):
        self.residualPower -= 1

        interestName = packet.name
        if self.pit.__contains__(interestName):
            table = self.pit[interestName]
            ntable = []
            for array in table:
                if array [1] == faceName and packet.freshness > array [2]:
                    logging.debug( self.name+ ": data packet "+ packet.name+ " forwarded to "+ array[0])
                    self.sendOut(packet , array[0])
                else:
                    ntable.append(array)

            if ntable == []:
                self.pit.pop(interestName)
            else:
                self.pit[interestName] = ntable
        self.cacheManagement(packet)

    @debug
    def forwardDataPacketNoCache(self, packet, faceName):
        self.residualPower -= 1

        interestName = packet.name
        if self.pit.__contains__(interestName):
            table = self.pit[interestName]
            ntable = []
            for array in table:
                if array[1] == faceName and packet.freshness > array[2]:
                    logging.debug(self.name + ": data packet " + packet.name + " forwarded to " + array[0])
                    self.sendOut(packet, array[0])
                else:
                    ntable.append(array)

            if ntable == []:
                self.pit.pop(interestName)
            else:
                self.pit[interestName] = ntable

    @debug
    def forwardDataPacketHalfCache(self, packet, faceName):
        self.residualPower -= 1

        interestName = packet.name
        if self.pit.__contains__(interestName):
            table = self.pit[interestName]
            ntable = []
            for array in table:
                if array[1] == faceName and packet.freshness > array[2]:
                    logging.debug(self.name + ": data packet " + packet.name + " forwarded to " + array[0])
                    self.sendOut(packet, array[0])
                else:
                    ntable.append(array)

            if ntable == []:
                self.pit.pop(interestName)
            else:
                self.pit[interestName] = ntable

        rand = random.randint(0, 1)
        if rand == 1:
            self.cacheManagement(packet)

    @debug
    def sendOut (self , packet , faceName):             # forward functions use this function
        self.residualPower -= 1
        queue = self.outputFaces[faceName]
        queue.append(packet)
        self.facesFlags[faceName] = True
        logging.debug( self.name+ ": packet "+ packet.name+ " sent out to "+ faceName)

    @debug
    def processOutgoingpackets (self):

        for faceName , face in self.outputFaces.items():
            if not self.facesFlags[faceName]:
                face.append("0")
                self.facesFlags[faceName] = True
                logging.debug(self.name + " ++ " + faceName + "  " + str(face))


    @debug
    def cacheManagement (self , packet):
        self.residualPower -= 1
        interestName = packet.name
        if self.cs.__contains__(interestName):
            if self.cs[interestName]['freshness'] + 50 < packet.freshness:
                print self.name, " : data exists in cache but expired"
                self.cacheReplace(packet)

        else:
            neededSize = packet.size
            ref = self.findEmptySpace(neededSize)
            print "cache management " , ref , neededSize
            print self.cacheMemory
            if ref != -1:
                print self.name ,": have enough memory for data packet " , packet.name
                self.cs[interestName] = {}
                self.cs[interestName]['packet'] = packet
                self.cs[interestName]['freshness'] = packet.freshness
                self.cs[interestName]['size'] = packet.size
                self.cs[interestName]['hitRatio'] = 0
                self.cs[interestName]['lastAccess'] = 0
                self.cs[interestName]['ref'] = ref
                self.fillSpace(neededSize , ref)

            else:
                print self.name ,": not enough space for data packet " , packet.name , " so calling cache replace "
                self.cacheReplace(packet)

    @debug
    def cacheManagementByFrequency(self, packet):
        self.residualPower -= 1
        interestName = packet.name
        if self.cs.__contains__(interestName):
            csPacket = self.cs[interestName]['packet']
            if time.timeInSeconds - csPacket.generatedTime < csPacket.frequency or csPacket.generatedTime < packet.generatedTime:
                print self.name, " : data exists in cache but expired or old"
                self.cacheReplace(packet)

        else:
            neededSize = packet.size
            ref = self.findEmptySpace(neededSize)
            print "cache management ", ref, neededSize
            #print self.cacheMemory
            if ref != -1:
                print self.name, ": have enough memory for data packet ", packet.name
                self.cs[interestName] = {}
                self.cs[interestName]['packet'] = packet
                self.cs[interestName]['freshness'] = packet.freshness
                self.cs[interestName]['size'] = packet.size
                self.cs[interestName]['hitRatio'] = 0
                self.cs[interestName]['lastAccess'] = 0
                self.cs[interestName]['ref'] = ref
                self.fillSpace(neededSize, ref)

            else:
                print self.name, ": not enough space for data packet ", packet.name, " so calling cache replace "
                self.cacheReplace(packet)


    @debug
    def cacheReplace(self, packet):
        self.residualPower -= 1
        interestName = packet.name
        if self.cs.__contains__(interestName):
            self.cs[interestName]['packet'] = packet
            self.cs[interestName]['freshness'] = packet.freshness
            oldSize = self.cs[interestName]['size']
            self.cs[interestName]['size'] = packet.size
            self.cs[interestName]['hitRatio'] = 0
            self.cs[interestName]['lastAccess'] = 0
            oldRef = self.cs[interestName]['ref']
            print self.name, " : packet ", packet.name, " is renewing "
            self.emptySpace(oldSize, oldRef)
            newRef = self.findEmptySpace(self.cs[interestName]['size'])
            if newRef != -1:
                self.cs[interestName]['ref'] = newRef
                self.fillSpace(self.cs[interestName]['size'], newRef)
                print self.name, " : packet ", packet.name, " is new "
            else:
                print( self.name , " : packet " , packet.name , " couldn't find space :(")
        else:

            print self.name, " : finding space for new packet ", packet.name
            minLastAccess = time.timeInSeconds
            minInterest = None
            neededSize = packet.size
            newRef = -1
            while newRef == -1:
                for name, data in self.cs.items():
                    print (name + str(data['lastAccess']) + str(minLastAccess))
                    if data['lastAccess'] < minLastAccess:
                        minLastAccess = data['lastAccess']
                        minInterest = name
                if minInterest != None:
                    self.emptySpace(self.cs[minInterest]['size'], self.cs[minInterest]['ref'])
                    print self.name, " packet ", self.cs[minInterest]['packet'].name, " removed"
                    self.cs.pop(minInterest)
                    minLastAccess = time.timeInSeconds
                    newRef = self.findEmptySpace(neededSize)

            print self.name, " : new ref ", newRef, " found for ", packet.name

    def emptySpace(self, size, ref):
        for x in range(ref, ref + size/8):
            self.cacheMemory[x] = False

    def fillSpace(self, size, ref):
        for x in range(ref, ref + size/8):
            self.cacheMemory[x] = True


    def findEmptySpace(self, neededSize):
        self.residualPower -= 1
        neededSize/= 8
        maxSize = self.memorySize + 1
        maxRef = -1
        ref = 0
        acc = 0

        for x in range(0, self.memorySize):
            if not self.cacheMemory[x]:
                acc += 1
                if acc == 1:
                    ref = x

                if x == self.memorySize - 1 and acc < maxSize and acc >= neededSize:
                    maxRef = ref
                    maxSize = acc

            elif acc < maxSize and acc >= neededSize:
                maxRef = ref
                maxSize = acc
                acc = 0

        return maxRef