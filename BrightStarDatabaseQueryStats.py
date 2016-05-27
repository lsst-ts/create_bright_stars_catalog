import pymysql
import time

class BrightStarDatabaseQueryStats:
    connection = 0
    cursor = 0
    
    def connect(self, host, port, user, password, database):
        self.connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=database)
        self.cursor = self.connection.cursor()
        
    def disconnect(self):
        self.cursor.close()
        self.connection.close()
   
    def getFilteredQueryTimes(self, iterations):
        CatalogUStats = self.getFilteredQueryTime(iterations, "U")
        CatalogGStats = self.getFilteredQueryTime(iterations, "G")
        CatalogRStats = self.getFilteredQueryTime(iterations, "R")
        CatalogIStats = self.getFilteredQueryTime(iterations, "I")
        CatalogZStats = self.getFilteredQueryTime(iterations, "Z")
        CatalogYStats = self.getFilteredQueryTime(iterations, "Y")
        return CatalogUStats, CatalogGStats, CatalogRStats, CatalogIStats, CatalogZStats, CatalogYStats
        
    def getFilteredQueryTime(self, iterations, filter):
        times = []
        for i in range(iterations):
            print "Iteration %d of %d for Filtered Catalog %s" % (i, iterations, filter)
            start = time.time()
            self.cursor.execute("SELECT `ra`, `decl`, `lsst%s` FROM `FilteredCatalog` WHERE `lsst%s` >= 7.32 AND `lsst%s` <= 15.68 AND `decl` <= -1 AND `decl` >= -2 AND `ra` >= 75 AND `ra` <= 75.23" % (filter, filter, filter))
            stop = time.time()
            times.append(stop - start)
        return times
        
    def getRawQueryTimes(self, iterations):
        CatalogUStats = self.getRawQueryTime(iterations, "U")
        CatalogGStats = self.getRawQueryTime(iterations, "G")
        CatalogRStats = self.getRawQueryTime(iterations, "R")
        CatalogIStats = self.getRawQueryTime(iterations, "I")
        CatalogZStats = self.getRawQueryTime(iterations, "Z")
        CatalogYStats = self.getRawQueryTime(iterations, "Y")
        return CatalogUStats, CatalogGStats, CatalogRStats, CatalogIStats, CatalogZStats, CatalogYStats
        
    def getRawQueryTime(self, iterations, filter):
        times = []
        for i in range(iterations):
            print "Iteration %d of %d for Raw Catalog %s" % (i, iterations, filter)
            start = time.time()
            self.cursor.execute("SELECT `ra`, `decl`, `lsst%s` FROM `Catalog` WHERE `lsst%s` >= 7.32 AND `lsst%s` <= 15.68 AND `decl` <= -1 AND `decl` >= -2 AND `ra` >= 75 AND `ra` <= 75.23" % (filter, filter, filter))
            stop = time.time()
            times.append(stop - start)
        return times

if __name__ == "__main__" :
    database = BrightStarDatabaseQueryStats()
    database.connect("140.252.32.27", 3306, "lsstwasadmin", "lsstwasadmin", "BrightStarCatalog")
    
    UStats, GStats, RStats, IStats, ZStats, YStats = database.getFilteredQueryTimes(100)
    for stat in [["U", UStats], ["G", GStats], ["R", RStats], ["I", IStats], ["Z", ZStats], ["Y", YStats]]:
        print "%s Filtered Catalog Stats:" % stat[0]
        print "\tMin: %f" % min(stat[1])
        print "\tMax: %f" % max(stat[1])
        print "\tAvg: %f" % (sum(stat[1]) / len(stat[1]))
        
    UStats, GStats, RStats, IStats, ZStats, YStats = database.getRawQueryTimes(100)
    for stat in [["U", UStats], ["G", GStats], ["R", RStats], ["I", IStats], ["Z", ZStats], ["Y", YStats]]:
        print "%s Raw Catalog Stats:" % stat[0]
        print "\tMin: %f" % min(stat[1])
        print "\tMax: %f" % max(stat[1])
        print "\tAvg: %f" % (sum(stat[1]) / len(stat[1]))

    database.disconnect()