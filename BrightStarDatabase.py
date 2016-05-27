import pymysql
import StarData

FilterU = "U"
FilterG = "G"
FilterR = "R"
FilterI = "I"
FilterZ = "Z"
FilterY = "Y"

class BrightStarDatabase:
    _connection = None
    _cursor = None
    
    def connect(self, host, port, user, password, database):
        self.connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=database)
        self.cursor = self.connection.cursor()
        
    def query(self, filter, corner1, corner2, corner3, corner4):
        ra = [corner1[0], corner2[0], corner3[0], corner4[0]]
        decl = [corner1[1], corner2[1], corner3[1], corner4[1]]
        top = max(decl)
        bottom = min(decl)
        left = min(ra)
        right = max(ra)
        
        query = "SELECT `ra`, `decl`, `lsst%s` as `mag` FROM `FilteredCatalog` WHERE `decl` <= %f AND `decl` >= %f AND `ra` >= %f AND `ra` <= %f" % (filter, top, bottom, left, right)
        self.cursor.execute(query)
        ra = []
        decl = []
        mag = []
        for item in self.cursor.fetchall():
            ra.append(item[0])
            decl.append(item[1])
            mag.append(item[2])
        return StarData.StarData(ra, decl, mag)
        
    def disconnect(self):
        self.cursor.close()
        self.connection.close()
        
if __name__ == "__main__":
    brightStarDatabaseHost = "140.252.32.27"
    brightStarDatabasePort = 3306
    brightStarDatabaseUser = "lsstwasadmin"
    brightStarDatabasePassword = "lsstwasadmin"
    brightStarDatabaseDatabase = "BrightStarCatalog"
    
    database = BrightStarDatabase()
    database.connect(brightStarDatabaseHost, brightStarDatabasePort, brightStarDatabaseUser, brightStarDatabasePassword, brightStarDatabaseDatabase)
    
    stars = database.query(FilterU, [75.998622, -1], [75.998622, -2], [75.998985, -1], [75.998985, -2])
    print "RA #    : %s" % (len(stars.RA) == 3)
    print "DEC #   : %s" % (len(stars.Decl) == 3)
    print "MAG #   : %s" % (len(stars.Mag) == 3)
    print "RA[0]   : %s" % (stars.RA[0] == 75.998623)
    print "RA[1]   : %s" % (stars.RA[1] == 75.998787)
    print "RA[2]   : %s" % (stars.RA[2] == 75.998985)
    print "Decl[0] : %s" % (stars.Decl[0] == -1.526383)
    print "Decl[1] : %s" % (stars.Decl[1] == -1.15006)
    print "Decl[2] : %s" % (stars.Decl[2] == -1.007737)
    print "Mag[0]  : %s" % (stars.Mag[0] == 28.7005)
    print "Mag[1]  : %s" % (stars.Mag[1] == 34.5597)
    print "Mag[2]  : %s" % (stars.Mag[2] == 28.8231)
    
    database.disconnect()