from globals import logging , plusSimulationTime
from decorators import debug
from consumer import Consumer
from face import Face
from producer import Producer

# import logging
#
# logging.basicConfig(filename='example.log',level=logging.DEBUG)



class main:

    countLoop = 0

    producers = {}
    consumers = {}
    allNodes = {}
    faces = {}
    totalCache = 0
    totalCacheMiss = 0
    totalCacheHit = 0
    totalPackets = 0
    maxLoad = 0
    avgLoad = 0
    midLatency = 0

    @debug
    def makeNodes (self):

        self.makeProducers()

        self.makeConsumers()

        self.makeFaces()

        # for name , node in self.allNodes.items():
        #     print name , node.inputFaces , "***" , node.outputFaces

        self.initialFibs()

        # for name , node in self.allNodes.items():
        #     print name , node.fib

    @debug
    def makeProducers (self):
        with open('producers.txt') as file:
            str = ""
            for line in file:
                if "---" not in line:
                    str+= line
                else:
                    arr = str.split()
                    #print (arr)
                    name = arr[0]
                    memorySize = arr[1]
                    totalPower = arr[2]
                    processingPowerUnit = arr[3]
                    transmissionPowerUnit = arr[4]
                    frequency = arr[5]
                    arch = arr [6]
                    newProducer = Producer( name , memorySize , totalPower , processingPowerUnit , transmissionPowerUnit , frequency , arch )
                    self.producers [name ] = newProducer
                    self.allNodes [name] = newProducer
                    str = ""

    @debug
    def makeConsumers(self):
        with open('consumers.txt') as file:
            str = ""
            for line in file:
                if "---" not in line:
                    str+= line
                else:
                    arr = str.split()
                    #print ( arr)
                    name = arr[0]
                    memorySize = arr[1]
                    totalPower = arr[2]
                    processingPowerUnit = arr[3]
                    transmissionPowerUnit = arr[4]
                    arch = arr [5]
                    newConsumer = Consumer( name , memorySize , totalPower , processingPowerUnit , transmissionPowerUnit , arch )
                    self.consumers [name ] = newConsumer
                    self.allNodes [name] = newConsumer
                    str = ""


    @debug
    def makeFaces (self):
        with open ('faces.txt') as file:
            str= ""
            for line in file:
                if "---" not in line:
                    str+= line
                else:
                    arr = str.split()
                    #print(arr)
                    name = arr[0]
                    delay = arr[1]
                    node1str = arr[2]
                    if self.producers.__contains__(node1str):
                        node1 = self.producers[node1str]
                    else:
                        node1 = self.consumers[node1str]
                    node2str = arr[3]
                    if self.producers.__contains__(node2str):
                        node2 = self.producers[node2str]
                    else:
                        node2 = self.consumers[node2str]

                    #print "newFace -->" , name , node1.name , node2.name
                    newFace = Face (name , delay , node1 , node2)
                    self.faces[name] = newFace
                    str = ""


    @debug
    def initialFibs (self):
        with open ('fibs.txt') as file:
            str = ""
            for line in file:
                if "---" not in line:
                    str+= line
                else:
                    arr = str.split()
                    #print (arr)
                    name = arr[0]
                    if self.producers.__contains__(name):
                        node = self.producers[name]
                    else: node = self.consumers[name]
                    node.initialFib(*arr)
                    str = ""

    @debug
    def __init__(self):
        self.makeNodes()
        #print (self.producers)
        #print (self.consumers)
        #print(self.faces)


        self.simulationLoop()



    def simulationLoop(self):


        while True:
            logging.debug("------------------ countLoop: " + str(self.countLoop) + "-------------------------------" )
            print ("------------------ countLoop: " + str(self.countLoop) + "-------------------------------" )
            self.countLoop+=1
            plusSimulationTime()
            for name , node in self.allNodes.items():
                node.processIncomingPacketsPathCache()

            for name , node in self.allNodes.items():
                #print (node.__class__)
                if node.__class__ is Producer:
                    node.updateState()
                else:
                    node.requestGenerator()

            for name , node in self.allNodes.items():
                node.processOutgoingpackets()

            # for name , node in self.allNodes.items():
            #     print name ," residual power: ", node.residualPower

            terminate = False
            for name , node in self.allNodes.items():
                if node.residualPower <=0:
                    terminate = True
            if terminate :
                break

            if self.countLoop > 1000:
                break



        print "---------------------------------"
        print "final loop count :" , self.countLoop
        print "------Power------"
        sum = 0
        for name, node in self.allNodes.items():
            sum += node.residualPower
        mid = sum/self.allNodes.__len__()

        print "mid residual power :" , mid

        print "------Latancy------"

        for name , node in self.consumers.items():
            latancy = node.totalWaitingTime / node.numberOfresponses
            self.midLatency += latancy
            print name , " avg latancy: " , latancy
        self.midLatency/= self.consumers.__len__()
        print "mid latancy: " , self.midLatency

        print "------Cache Hit------"

        for name , node in self.allNodes.items():
            if node.cacheHit + node.cacheMiss != 0:
                cacheHit = float(node.cacheHit)/(node.cacheHit + node.cacheMiss)
            else:
                cacheHit = 0
            print name , " : cacheHit:" , node.cacheHit ," cacheMiss: ", node.cacheMiss ," Real cache hit: " , cacheHit
            self.totalCache +=node.cacheHit + node.cacheMiss
            self.totalCacheHit += node.cacheHit

        print "total Cache hit = " , (float(self.totalCacheHit) / self.totalCache)/ self.allNodes.__len__()

        print "------#Packets------"

        for name , node in self.allNodes.items():
            print name ," #interest: " , node.numberOfInterestPacket , "  #dataPacket: " , node.numberOfDataPacket
            self.totalPackets+= node.numberOfDataPacket + node.numberOfInterestPacket

        print "total #packets: " , self.totalPackets

        for name, node in self.allNodes.items():
            if node.inputLoad > self.maxLoad:
                self.maxLoad = node.inputLoad
            self.avgLoad+= node.inputLoad

        print "max Input load: " , self.maxLoad , "avg Input load: " , self.avgLoad/self.allNodes.__len__()


m = main()