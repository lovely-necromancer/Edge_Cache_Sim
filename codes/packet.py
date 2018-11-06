# class Packet:
#
#     name = None
#     isData = True
#     frequency = None
#     size = None
#     payload = None
#     generatedTime = None
#
#     #freshness = 1 - dataAge/ frequency
#
#     def __init__(self ,name , isData , frequency , payload , generatedTime):
#             self.name = name
#             self.isData = bool(isData)
#             self.frequency = int(frequency)
#             self.generatedTime = generatedTime
#
#             if not isData:
#                 self.payload = 0
#                 self.size = 0
#             else:
#                 self.payload = payload
#                 self.size = len(payload)


class InterestPacket:

    name = None
    freshness = None
    generatedTime = None

    def __init__(self , interestName , freshness , generatedTime):
        self.name = interestName
        self.freshness = float(freshness)
        self.generatedTime = int(generatedTime)



class DataPacket:
    name = None
    frequency = None
    size = None
    payload = None
    generatedTime = None

    def __init__(self , name, frequency ,payload , generatedTime):
        self.name = name
        self.frequency = int(frequency)
        self.size = len(payload)
        self.payload = payload
        self.generatedTime = int(generatedTime)