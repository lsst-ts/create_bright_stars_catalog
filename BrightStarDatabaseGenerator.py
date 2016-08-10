import gzip
import time
from os import listdir
from os.path import isfile, join

class BrightStarDatabaseGenerator:
    #  0 = dummy_htmid 
    #  1 = star_id 
    #  2 = ra 
    #  3 = dec 
    #  4 = mura 
    #  5 = mudec 
    #  6 = lon
    #  7 = lat 
    #  8 = sed 
    #  9 = magnorm 
    # 10 = flux_factor 
    # 11 = E(B-V) 
    # 12 = Teff 
    # 13 = [Fe/H] 
    # 14 = log(g) 
    # 15 = lsst_u_noatm 
    # 16 = lsst_g_noatm 
    # 17 = lsst_r_noatm 
    # 18 = lsst_i_noatm 
    # 19 = lsst_z_noatm 
    # 20 = lsst_y_noatm 
    # 21 = lsst_u_atm 
    # 22 = lsst_g_atm 
    # 23 = lsst_r_atm 
    # 24 = lsst_i_atm 
    # 25 = lsst_z_atm 
    # 26 = lsst_y_atm 
    # 27 = sdss_u(ext) 
    # 28 = sdss_g(ext) 
    # 29 = sdss_r(ext) 
    # 30 = sdss_i(ext) 
    # 31 = sdss_z(ext) 
    # 32 = sdss_u(raw) 
    # 33 = sdss_g(raw) 
    # 34 = sdss_r(raw) 
    # 35 = sdss_i(raw) 
    # 36 = sdss_z(raw) 
    # 37 = color_residual 
    # 38 = file_name
    columns = [1, 2, 3, 4, 5, 8, 11, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]

    directory = ""
    outputFile = ""
    lsstFile = ""

    def __init__(self, directory):
        self.directory = directory

    def generate(self, outputFile):
        self.createOutputFile(outputFile)
        ids = self.getIds()
        for id in ids:
            self.processId(id)
        self.closeOutputFile()

    def processId(self, id):
        print "%f Processing id %s" % (time.time(), id)
        self.openFiles(id)
        while True:
            lsstLine = self.readFiles()
            if self.idIsDone(id, lsstLine):
                break
            self.processLine(id, lsstLine)
        self.closeFiles()

    def processLine(self, id, lsstLine):
        text = id
        for column in self.columns:
            text = text + "," + self.getColumn(column, ",", lsstLine)
        self.outputFile.writelines(text + "\n")

    def getIds(self):
        return [self.getId(item) for item in listdir(self.directory) if self.fileIsCatalogFile(item)]

    def getId(self, item):
        return item[:5]

    def idIsDone(self, id, lsstLine):
        if not lsstLine:
            return True
        return False

    def fileIsCatalogFile(self, item):
        return isfile(join(self.directory, item)) and item.endswith(".txt.gz")

    def createOutputFile(self, outputFile):
        self.outputFile = open(outputFile, "w+")

    def closeOutputFile(self):
        self.outputFile.close()

    def openFiles(self, id):
        self.openLSSTFile(id)

    def readFiles(self):
        return self.readLSSTFile()

    def closeFiles(self):
        self.closeLSSTFile()

    def openLSSTFile(self, id):
        # Has header
        fileName = "%s.csv.gz_ebv_grid_fit.txt.gz" % id
        self.lsstFile = gzip.open(join(self.directory, fileName))
        self.lsstFile.readline()

    def readLSSTFile(self):
        # Turn space deliminated line into comma deliminated line
        return self.removeReturnNewLine(self.lsstFile.readline().replace(" ", ","))

    def closeLSSTFile(self):
        self.lsstFile.close()

    def getColumn(self, column, deliminator, text):
        return text.split(deliminator)[column]

    def removeReturnNewLine(self, text):
        return text.replace("\r", "").replace("\n", "")

if __name__ == "__main__":
    directory = "D:\\Temp\\RawDatabase2"
    outputFile = "D:\\Temp\\brightstarraw2.csv"
    BrightStarDatabaseGenerator(directory).generate(outputFile)