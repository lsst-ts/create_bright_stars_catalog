import time
import numpy as np

class BrightStarDatabaseStats:
    __lines = 0
    __idBits = np.zeros(16)
    __raMap = {}
    __decMap = {}
    __flagBits = np.zeros(32)
    __uMap = {}
    __gMap = {}
    __rMap = {}
    __iMap = {}
    __zMap = {}
    __yMap = {}
    __suspectGood = 0
    __suspectBad = 0
    __duplicateIds = {}
    __duplicatesInAPASS = 0
    __duplicatesInOther = 0

    def run(self, file):
        with open(file) as f:
            for line in f:
                gatherMoreStatus = False
                gatherMoreSourceStatus = False

                startIndex = 0
                self.__lines += 1
                if self.__lines % 1000000 == 0:
                    print self.__lines
                #if self.__lines == 10000000:
                #    break
                # source
                # ignored
                text, startIndex = self.getColumn(line, startIndex)
                # starId
                text, startIndex = self.getColumn(line, startIndex)
                value = long(text)
                starId = value
                mask = (value & 0xF00000000000) >> 44
                self.__idBits[mask] += 1
                if mask == 2:
                    gatherMoreStatus = True
                #current = self.__duplicateIds.get(starId, 0)
                #current += 1
                #self.__duplicateIds[starId] = current
                #if current > 1:
                #    gatherMoreSourceStatus = True
                # ra, dec
                for map in [self.__raMap, self.__decMap]:
                    text, startIndex = self.getColumn(line, startIndex)
                    value = round(float(text), 1)
                    current = map.get(value, 0)
                    map[value] = current + 1
                # muRA, muDecl
                # magB, magV, magU, magG, magR, magI, magZ, magY, magJ, magH
                # magK,   w1,   w2,   w3,   w4, magSST
                # ignored
                for i in range(18):
                    text, startIndex = self.getColumn(line, startIndex)
                # flag
                text, startIndex = self.getColumn(line, startIndex)
                value = int(text)
                for i in range(32):
                    mask = value & (2**i)
                    if (mask) != 0:
                        self.__flagBits[i] += 1
                    if i == 20 or 22 or 24 or 25 or 26 or 30:
                        gatherMoreStatus = True
                if gatherMoreStatus:
                    if value & (0x260) > 0:
                        self.__suspectGood += 1
                    elif (starId & 0xF00000000000) ==  0x600000000000 or 0x700000000000:
                        self.__suspectGood += 1
                    else:
                        self.__suspectBad += 1
                if gatherMoreSourceStatus:
                    if value & 0x200:
                        self.__duplicatesInAPASS += 1
                    elif (starId & 0xF00000000000) == 0x700000000000:
                        self.__duplicatesInAPASS += 1
                    else:
                        self.__duplicatesInOther += 1
                # matched_sed
                # ignored
                text, startIndex = self.getColumn(line, startIndex)
                # lsst_obs_u, lsst_obs_g, lsst_obs_r, lsst_obs_i, lsst_obs_z, lsst_obs_y
                for map in [self.__uMap, self.__gMap, self.__rMap, self.__iMap, self.__zMap, self.__yMap]:
                    text, startIndex = self.getColumn(line, startIndex)
                    value = round(float(text), 1)
                    current = map.get(value, 0)
                    map[value] = current + 1
                # ebv
                # ignored

        return self.__lines, self.__idBits, self.__raMap, self.__decMap, self.__flagBits, self.__uMap, self.__gMap,\
               self.__rMap, self.__iMap, self.__zMap, self.__yMap, self.__suspectGood, self.__suspectBad, self.__duplicatesInAPASS, self.__duplicatesInOther

    def getColumn(self, line, startIndex):
        endIndex = line.index(",", startIndex)
        column = line[startIndex:endIndex]
        return column, endIndex + 1

if __name__ == "__main__":
    inputFile = "D:\\Temp\\brightstarraw.csv"
    startTime = time.time()
    lines, idBits, raMap, decMap, flagBits, uMap, gMap, rMap, iMap, zMap, yMap, suspectGood, suspectBad, duplicateInAPASS, duplicateInOther = BrightStarDatabaseStats().run(inputFile)
    stopTime = time.time()
    print "Duration: %f" % (stopTime - startTime)
    print "Lines: %d" % lines
    print "ID Bits:"
    for index in range(len(idBits)):
        print "\t%X: %d" % (index, idBits[index])
    print "Flag Bits:"
    for index in range(len(flagBits)):
        print "\t%X: %d" % (index, flagBits[index])
    print "Suspected but Good: %d" % suspectGood
    print "Suspected and Bad: %d" % suspectBad
    print "Duplicates in APASS: %d" % duplicateInAPASS
    print "Duplicates in Other: %d" % duplicateInOther
    print "Writing data to stats file"
    with open(inputFile + ".stats.csv", "w+") as f:
        f.write("Duration: %f\n" % (stopTime - startTime))
        f.write("Lines: %d\n" % lines)
        f.write("ID Bits:\n")
        for index in range(len(idBits)):
            f.write("\t%X: %d\n" % (index, idBits[index]))
        f.write("Flag Bits:\n")
        for index in range(len(flagBits)):
            f.write("\t%X: %d\n" % (index, flagBits[index]))
        f.write("Suspected but Good: %d\n" % suspectGood)
        f.write("Suspected and Bad: %d\n" % suspectBad)
        f.write("Duplicates in APASS: %d\n" % duplicateInAPASS)
        f.write("Duplicates in Other: %d\n" % duplicateInOther)
    for table in [["ra", raMap], ["dec", decMap], ["u", uMap], ["g", gMap], ["r", rMap], ["i", iMap], ["z", zMap], ["y", yMap]]:
        name = table[0]
        map = table[1]
        with open(inputFile + ".stats." + name + ".csv", "w+") as f:
            for key in map:
                f.write("%f,%d\n" % (key, map[key]))