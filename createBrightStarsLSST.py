import pymysql
import time

HOST = "rhea.lsst.org"
USER = "lsstwasadmin"
PASSWD = "lsstwasadmin"
DB = "BrightStarCatalog"
PORT = 3306

class BrightStarDatabaseQueryStats:
    connection = 0
    cursor = 0
    
    def connect(self, host, port, user, password, database):
        self.connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=database)
        self.cursor = self.connection.cursor()
        
    def disconnect(self):
        self.cursor.close()
        self.connection.close()
        
    def runIndividualTables(self, iterations):       
        UCatalogStats = self.runIndividualTable(iterations, "U")
        GCatalogStats = self.runIndividualTable(iterations, "G")
        RCatalogStats = self.runIndividualTable(iterations, "R")
        ICatalogStats = self.runIndividualTable(iterations, "I")
        ZCatalogStats = self.runIndividualTable(iterations, "Z")
        YCatalogStats = self.runIndividualTable(iterations, "Y")
        return UCatalogStats, GCatalogStats, RCatalogStats, ICatalogStats, ZCatalogStats, YCatalogStats        
    
    def runIndividualTable(self, iterations, table):
        times = []
        for i in range(iterations):
            print "Iteration %d of %d for %s" % (i, iterations, table)
            start = time.time()
            self.cursor.execute("SELECT * FROM `%sCatalog` WHERE `mag` >= 7.32 AND `mag` <= 15.68 AND `decl` <= -1 AND `decl` >= -2 AND `ra` >= 75 AND `ra` <= 75.23" % table)
            stop = time.time()
            times.append(stop - start)
        return times
        
    def runCatalogTable(self, iterations):
        CatalogUStats = self.runCatalogTableFilter(iterations, "U")
        CatalogGStats = self.runCatalogTableFilter(iterations, "G")
        CatalogRStats = self.runCatalogTableFilter(iterations, "R")
        CatalogIStats = self.runCatalogTableFilter(iterations, "I")
        CatalogZStats = self.runCatalogTableFilter(iterations, "Z")
        CatalogYStats = self.runCatalogTableFilter(iterations, "Y")
        return CatalogUStats, CatalogGStats, CatalogRStats, CatalogIStats, CatalogZStats, CatalogYStats
        
    def runCatalogTableFilter(self, iterations, filter):
        times = []
        for i in range(iterations):
            print "Iteration %d of %d for %s" % (i, iterations, filter)
            start = time.time()
            self.cursor.execute("SELECT * FROM `Catalog` WHERE `lsst%s` >= 7.32 AND `lsst%s` <= 15.68 AND `decl` <= -1 AND `decl` >= -2 AND `ra` >= 75 AND `ra` <= 75.23" % filter)
            stop = time.time()
            times.append(stop - start)
        return times
        
    def runFilteredCatalogTable(self, iterations):
        CatalogUStats = self.runFilteredCatalogTableFilter(iterations, "U")
        CatalogGStats = self.runFilteredCatalogTableFilter(iterations, "G")
        CatalogRStats = self.runFilteredCatalogTableFilter(iterations, "R")
        CatalogIStats = self.runFilteredCatalogTableFilter(iterations, "I")
        CatalogZStats = self.runFilteredCatalogTableFilter(iterations, "Z")
        CatalogYStats = self.runFilteredCatalogTableFilter(iterations, "Y")
        return CatalogUStats, CatalogGStats, CatalogRStats, CatalogIStats, CatalogZStats, CatalogYStats
        
    def runFilteredCatalogTableFilter(self, iterations, filter):
        times = []
        for i in range(iterations):
            print "Iteration %d of %d for %s" % (i, iterations, filter)
            start = time.time()
            self.cursor.execute("SELECT * FROM `FilteredCatalog` WHERE `lsst%s` >= 7.32 AND `lsst%s` <= 15.68 AND `decl` <= -1 AND `decl` >= -2 AND `ra` >= 75 AND `ra` <= 75.23" % filter)
            stop = time.time()
            times.append(stop - start)
        return times

if __name__ == "__main__" :
    database = BrightStarDatabaseQueryStats()
    database.connect(HOST, PORT, USER, PASSWD, DB)
    
    UStats, GStats, RStats, IStats, ZStats, YStats = database.runIndividualTables(100)
    for stat in [["U", UStats], ["G", GStats], ["R", RStats], ["I", IStats], ["Z", ZStats], ["Y", YStats]]:
        print "%s Individual Stats:" % stat[0]
        print "\tMin: %f" % min(stat[1])
        print "\tMax: %f" % max(stat[1])
        print "\tAvg: %f" % (sum(stat[1]) / len(stat[1]))
        
    UStats, GStats, RStats, IStats, ZStats, YStats = database.runCatalogTable(100)
    for stat in [["U", UStats], ["G", GStats], ["R", RStats], ["I", IStats], ["Z", ZStats], ["Y", YStats]]:
        print "%s Catalog Stats:" % stat[0]
        print "\tMin: %f" % min(stat[1])
        print "\tMax: %f" % max(stat[1])
        print "\tAvg: %f" % (sum(stat[1]) / len(stat[1]))
        
    UStats, GStats, RStats, IStats, ZStats, YStats = database.runFilteredCatalogTable(100)
    for stat in [["U", UStats], ["G", GStats], ["R", RStats], ["I", IStats], ["Z", ZStats], ["Y", YStats]]:
        print "%s Filtered Catalog Stats:" % stat[0]
        print "\tMin: %f" % min(stat[1])
        print "\tMax: %f" % max(stat[1])
        print "\tAvg: %f" % (sum(stat[1]) / len(stat[1]))

    database.disconnect()
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASSWD, db=DB)
    curr = conn.cursor()