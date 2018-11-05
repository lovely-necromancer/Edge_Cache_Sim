class Packet:

    name = None
    isData = True
    frequency = None
    size = None
    payload = None
    generatedTime = None

    #freshness = 1 - dataAge/ frequency

    def __init__(self ,name , isData , frequency , payload , generatedTime):
            self.name = name
            self.isData = bool(isData)
            self.frequency = int(frequency)
            self.generatedTime = generatedTime

            if not isData:
                self.payload = 0
                self.size = 0
            else:
                self.payload = payload
                self.size = len(payload)
