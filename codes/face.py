from collections import deque
from consumer import Consumer
from producer import Producer
from decorators import debug


class Face:

    name = None

    leftNode = None
    rightNode = None

    leftQueue = None
    rightQueue = None

    def __init__(self ,name , delay , node1 , node2 ):
        self.name = name
        self.leftNode = node1
        self.rightNode = node2

        self.leftQueue = deque([])
        self.rightQueue = deque([])
        for i in range (int(delay)):
            self.rightQueue.append( "0" )
            self.leftQueue.append( "0" )


        #print "leftNode" , name , self.leftNode.name
        #print "rightNode" , name , self.rightNode.name

        self.leftNode.inputFaces[name] = self.leftQueue
        self.leftNode.outputFaces[name] = self.rightQueue
        self.leftNode.facesFlags[name] = False

        self.rightNode.inputFaces[name] = self.rightQueue
        self.rightNode.outputFaces[name] =self.leftQueue
        self.rightNode.facesFlags[name] = False

