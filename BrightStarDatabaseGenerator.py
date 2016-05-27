import gzip
import time
from os import listdir
from os.path import isfile, join

class BrightStarDatabaseGenerator:
    startIDColumn = 1
    raColumn = 2
    decColumn = 3
    flagColumn = 22

    targetDecimalPlaces = 6

    directory = ""
    outputFile = ""
    catalogFile = ""
    sedFile = ""
    lsstFile = ""

    def __init__(self, directory):
        self.directory = directory

    def generate(self, outputFile):
        self.createOutputFile(outputFile)
        ids = self.getIds()
        for id in ids:
            self.processId(id)
            break
        self.closeOutputFile()

    def processId(self, id):
        print "%f Processing id %s" % (time.time(), id)
        self.openFiles(id)
        while True:
            catalogLine, sedLine, lsstLine = self.readFiles()
            if self.idIsDone(id, catalogLine, sedLine, lsstLine):
                break
            self.processLine(id, catalogLine, sedLine, lsstLine)
        self.closeFiles()

    def processLine(self, id, catalogLine, sedLine, lsstLine):
        if self.shouldWriteLine(id, catalogLine, sedLine, lsstLine):
            self.outputFile.writelines(id + "," + catalogLine + "," + sedLine + "," + lsstLine + "\n")

    def shouldWriteLine(self, id, catalogLine, sedLine, lsstLine):
        return self.checkStarID(catalogLine) and self.checkFlag(catalogLine)

    def checkStarID(self, catalogLine):
        starID = long(self.getColumn(self.startIDColumn, ",", catalogLine))
        return True

    def checkFlag(self, catalogLine):
        flag = int(self.getColumn(self.flagColumn, ",", catalogLine))
        return True

    def getUpdatedRa(self, catalogLine):
        ra = self.getColumn(self.raColumn, ",", catalogLine)
        return self.getUpdatedFloat(ra, self.targetDecimalPlaces)

    def getUpdatedDec(self, catalogLine):
        dec = self.getColumn(self.decColumn, ",", catalogLine)
        return self.getUpdatedFloat(dec, self.targetDecimalPlaces)

    def getUpdatedFloat(self, text, targetDecimalPlaces):
        decimalPlaces = self.getDecimalPlaces(text)
        missingPlaces = targetDecimalPlaces - decimalPlaces
        text = text.replace(".", "")
        if missingPlaces != 0:
            text = text + "".join(['0' for i in range(missingPlaces)])
        return text

    def getIds(self):
        return [self.getId(item) for item in listdir(self.directory) if self.fileIsCatalogFile(item)]

    def getId(self, item):
        return item[:5]

    def idIsDone(self, id, catalogLine, sedLine, lsstLine):
        doneCount = 0
        if not catalogLine:
            doneCount = doneCount + 1
        if not sedLine:
            doneCount = doneCount + 1
        if not lsstLine:
            doneCount = doneCount + 1
        if doneCount == 0:
            return False
        if doneCount != 3:
            print "ERROR with id %s" % id
            return True
        return True

    def fileIsCatalogFile(self, item):
        return isfile(join(self.directory, item)) and item.endswith(".csv.gz")

    def createOutputFile(self, outputFile):
        self.outputFile = open(outputFile, "w+")

    def closeOutputFile(self):
        self.outputFile.close()

    def openFiles(self, id):
        self.openCatalogFile(id)
        self.openSEDFile(id)
        self.openLSSTFile(id)

    def readFiles(self):
        return self.readCatalogFile(), self.readSEDFile(), self.readLSSTFile()

    def closeFiles(self):
        self.closeCatalogFile()
        self.closeSEDFile()
        self.closeLSSTFile()

    def openCatalogFile(self, id):
        # Header format
        # id,ra,dec,mu_ra,mu_dec,B?,V?,u?,g,r,i,z?,y?,J,H,K,w1,w2,w3,w4,?,?
        # Has no header
        fileName = "%s.csv.gz" % id
        self.catalogFile = gzip.open(join(self.directory, fileName))

    def readCatalogFile(self):
        return self.removeReturnNewLine(self.catalogFile.readline())

    def closeCatalogFile(self):
        self.catalogFile.close()

    def openSEDFile(self, id):
        # Header format
        # name
        # Has header
        fileName = "%s.csv.gz.sedNames_unext.dat" % id
        self.sedFile = open(join(self.directory, fileName))
        self.sedFile.readline()

    def readSEDFile(self):
        return self.removeReturnNewLine(self.sedFile.readline())

    def closeSEDFile(self):
        self.sedFile.close()

    def openLSSTFile(self, id):
        # Header format
        # u g r i z y ebv
        # Has header
        fileName = "%s.lsst_mags_dust.gz" % id
        self.lsstFile = gzip.open(join(self.directory, fileName))
        self.lsstFile.readline()

    def readLSSTFile(self):
        # Turn space deliminated line into comma deliminated line
        return self.removeReturnNewLine(self.lsstFile.readline().replace(" ", ","))

    def closeLSSTFile(self):
        self.lsstFile.close()

    def getColumn(self, column, deliminator, text):
        endIndex = -1
        startIndex = 0
        for i in range(column):
            startIndex = endIndex + 1
            try:
                endIndex = text.index(deliminator, startIndex)
            except:
                if (i + 1) == column:
                    return text[startIndex:]
                raise
        return text[startIndex:endIndex]

    def getDecimalPlaces(self, value):
        try:
            index = value.index(".")
            return len(value[(index + 1):])
        except:
            return 0

    def removeReturnNewLine(self, text):
        return text.replace("\r", "").replace("\n", "")

if __name__ == "__main__":
    directory = "D:\\BrightStarRaw"
    outputFile = "D:\\Temp\\brightstarraw-small.csv"
    BrightStarDatabaseGenerator(directory).generate(outputFile)