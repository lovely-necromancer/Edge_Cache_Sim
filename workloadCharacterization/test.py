
from packet import packet
import csv
import json

smp = open('/Users/user/Desktop/Sharif uni/part1', 'r')
smp2 = open('/Users/user/Desktop/Sharif uni/part2', 'r')
smp3 = open('/Users/user/Desktop/Sharif uni/part3', 'r')
smp4 = open('/Users/user/Desktop/Sharif uni/part4', 'r')
smp5 = open('/Users/user/Desktop/Sharif uni/part5', 'r')
smp6 = open('/Users/user/Desktop/Sharif uni/part6', 'r')

jj = json.load(smp)
jj += json.load(smp2)
jj += json.load(smp3)
jj += json.load(smp4)
jj += json.load(smp5)
jj += json.load(smp6)


# json.dump(jj)
#print(json.dump(jj))

listOfDevices = {}

informations = {}

datas = {}
tcps = {}
udps = {}
numberOfpackets = 0

macAddrs = {}

logfiletcp  = open("tcplog", 'w')
logfileudp = open ( "udplog" , "w")

with open('/Users/user/Desktop/Sharif uni/List_Of_Devices.txt') as file:
    for line in file:
        strs = line.split("\t")
        strs2 = strs[1].split("\n")
        if not macAddrs.__contains__(strs2[0]):
            macAddrs[strs2[0]] = strs[0]

for item in jj:

    x = item['_source']
    x = x['layers']
    layers = x
    x = x['eth']

    macadd = x['eth.src']

    nameOfDevice = macAddrs[macadd]

    if nameOfDevice != "TPLink Router Bridge LAN (Gateway)":

        newpacket = packet()
        numberOfpackets+=1
        newpacket.myDevice = nameOfDevice
        x = item['_source']
        x = x['layers']
        y = x
        x = x['frame']
        newpacket.number = x['frame.number']
        newpacket.size = x['frame.len']
        # if 'tcp' in layers:
        #     t = layers['tcp']
        #     len = t['tcp.len']
        #     if not len == "0":
        #         newpacket.size = x['frame.len']
        #     else:
        #         newpacket.size = "-1"
        #
        # else:
        #     newpacket.size = x['frame.len']

        newpacket.myDevice = nameOfDevice
        newpacket.protocol = x['frame.coloring_rule.name']

        if newpacket.protocol == "udp":
            y = y['udp']
            newpacket.size = y["udp.length"]


        x = "" + x['frame.time']
        x = x.split(" ")
        newpacket.timeStamp = x[3]


        if not listOfDevices.__contains__(nameOfDevice):
            listOfDevices[nameOfDevice] = [ 1 , 0]
            datas[nameOfDevice] = [newpacket]
            informations[nameOfDevice] = {}


        else:

            listOfDevices[nameOfDevice][0] += 1
            datas[nameOfDevice].append(newpacket)


        if not informations[nameOfDevice].__contains__(newpacket.protocol):
            informations[nameOfDevice][newpacket.protocol] = [ 1 , int ( newpacket.size) , 0 ]


        else:
            # if not newpacket.size == "-1":
                informations[nameOfDevice][newpacket.protocol][0] +=1
                informations[nameOfDevice][newpacket.protocol][1] += int (newpacket.size)
                informations[nameOfDevice]



        if 'tcp' in layers:
            frame = layers['frame']
            time = "" + frame['frame.time']
            time = time.split(" ")
            time = time [3]
            time = time.split(".")
            time = time[0]
            tcp = layers['tcp']
            size = tcp['tcp.len']
            seq = tcp ['tcp.seq']
            flag = tcp['tcp.flags_tree']
            flag = flag['tcp.flags.fin']
            if not tcps.__contains__(nameOfDevice):
                tcps[nameOfDevice] = []
            str = "--  " + time + "\t\tlen:\t" + size + "\t\tsequence\t" + seq + "\t\tflag\t" + flag +"\t\t" + newpacket.myDevice
            tcps[nameOfDevice].append(str)
            # if not size == "0" :
            #     logfiletcp.write(str + '\n')
            #     print(str)

        if 'udp' in layers:
            frame = layers['frame']
            time = "" + frame['frame.time']
            time = time.split(" ")
            time = time[3]
            time = time.split(".")
            time = time[0]
            udp = layers['udp']
            size = udp['udp.length']

            if not udps.__contains__(nameOfDevice):
                udps[nameOfDevice] = []
            str = "--  " + time + "\t\tlen:\t" + size + "\t\t" + newpacket.myDevice
            udps[nameOfDevice].append(str)
            #logfileudp.write(str + '\n')
            #print(str)

for device , data in udps.items():
    logfileudp.write("\n" + device + "\n")
    for str in data:
        logfileudp.write(str + '\n')



for device , data in tcps.items():
    logfiletcp.write("\n" + device + "\n")
    for str in data:
        logfiletcp.write(str + '\n')


logfiletcp.close()
logfileudp.close()

for device , arr in listOfDevices.items():
    arr[1] = (arr[0] / numberOfpackets) * 100

for device , protocols in informations.items():
   for protocol , listOfdata in protocols.items():
       listOfdata[1] = int (listOfdata[1] / listOfdata[0])
       listOfdata[2] = (listOfdata[0] / listOfDevices[device][0]) * 100


with open('eggs.csv', 'w') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|',  quoting=csv.QUOTE_MINIMAL)

    spamwriter.writerow(["device","protocol", "protocol_avg_size" , "number of packets" , " percent of packets" , " load of this device"])
    for device, protocols in informations.items():
        arr = listOfDevices[device]
        for protocol, listOfdata in protocols.items():
            spamwriter.writerow([ device , protocol , listOfdata[1] , listOfdata[0] , listOfdata[2] , arr[1]])

