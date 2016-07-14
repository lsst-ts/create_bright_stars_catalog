import pymysql
import StarData
import unittest
import numpy

FilterU = "U"
FilterG = "G"
FilterR = "R"
FilterI = "I"
FilterZ = "Z"
FilterY = "Y"

stddevSplit = 20.0

class BrightStarDatabase(object):
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self, host, port, user, password, database):
        """
        Connects to the MariaDB database.
        
        @param host [in] The host name / ip of the database.
        
        @param port [in] The port to connect on.
        
        @param user [in] The user name to connect as.
        
        @param password [in] The password for the user.
        
        @param database [in] The database to use.
        """
        self.connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=database)
        self.cursor = self.connection.cursor()
        
    def query(self, filter, corner1, corner2, corner3, corner4):
        """
        Queries the database for stars within an area.
        
        @param filter [in] The filter to query.
        Valid values are (U, G, R, I, Z, Y).
        
        @param corner1 [in] The first corner of the sensor defined as (RA, Decl).
        
        @param corner2 [in] The second corner of the sensor defined as (RA, Decl).
        
        @param corner3 [in] The third corner of the sensor defined as (RA, Decl).
        
        @param corner4 [in] The fourth corner of the sensor defined as (RA, Decl).
        """
        
        ra = [corner1[0], corner2[0], corner3[0], corner4[0]]
        decl = [corner1[1], corner2[1], corner3[1], corner4[1]]
        top = max(decl)
        bottom = min(decl)
        left = min(ra)
        right = max(ra)
        
        raStddev = numpy.std(ra)
        if raStddev >= stddevSplit:
            left = max([x for x in ra if x < 180])
            right = min([x for x in ra if x >= 180])
            above0Set = self.queryInternal(filter, top, bottom, 0, left)
            below0Set = self.queryInternal(filter, top, bottom, right, 360)
            return StarData.StarData(above0Set.ID + below0Set.ID, above0Set.RA + below0Set.RA, above0Set.Decl + below0Set.Decl, above0Set.ObsMag + below0Set.ObsMag, above0Set.LSSTMag + below0Set.LSSTMag)
        else:
            return self.queryInternal(filter, top, bottom, left, right)
        
    def queryInternal(self, filter, top, bottom, left, right):
        """
        Queries the database for stars within an area.
        
        @param filter [in] The filter to query.
        Valid values are (U, G, R, I, Z, Y).
        
        @param top [in] The top edge of the box (Decl).
        
        @param bottom [in] The bottom edge of the box (Decl).
        
        @param left [in] The left edge of the box (RA).
        
        @param right [in] The right edge of the box (RA).
        """
        query = "SELECT `id`, `ra`, `decl`, `mag%s`, `lsst%s` FROM `FilteredCatalog` WHERE `decl` <= %f AND `decl` >= %f AND `ra` >= %f AND `ra` <= %f" % (filter, filter, top, bottom, left, right)
        self.cursor.execute(query)
        id = []
        ra = []
        decl = []
        obsMag = []
        lsstMag = []
        for item in self.cursor.fetchall():
            id.append(item[0])
            ra.append(item[1])
            decl.append(item[2])
            obsMag.append(item[3])
            lsstMag.append(item[4])
        return StarData.StarData(id, ra, decl, obsMag, lsstMag)
        
    def general(self, statement):
        self.cursor.execute(statement)
        return self.cursor.fetchall()
        
    def disconnect(self):
        """
        Disconnects from the database.
        """
        self.cursor.close()
        self.connection.close()
        
class BrightStarDatabaseTest(unittest.TestCase):
    brightStarDatabaseHost = "140.252.32.27"
    brightStarDatabasePort = 3306
    brightStarDatabaseUser = "lsstwasadmin"
    brightStarDatabasePassword = "lsstwasadmin"
    brightStarDatabaseDatabase = "BrightStarCatalog"
    database = None
    
    def setUp(self):
        self.database = BrightStarDatabase()
        self.database.connect(self.brightStarDatabaseHost, self.brightStarDatabasePort, self.brightStarDatabaseUser, self.brightStarDatabasePassword, self.brightStarDatabaseDatabase)
        
    def tearDown(self):
        self.database.disconnect()
        
    def testUQuery(self):
        stars = self.database.query(FilterU, [75.998622, -1], [75.998622, -2], [75.998985, -1], [75.998985, -2])
        self.assertEqual(len(stars.ID), 3)
        self.assertEqual(len(stars.RA), 3)
        self.assertEqual(len(stars.Decl), 3)
        self.assertEqual(len(stars.ObsMag), 3)
        self.assertEqual(len(stars.LSSTMag), 3)
        self.assertEqual(stars.ID[0], 363696272)
        self.assertEqual(stars.ID[1], 365637924)
        self.assertEqual(stars.ID[2], 366149386)
        self.assertEqual(stars.RA[0], 75.998623)
        self.assertEqual(stars.RA[1], 75.998787)
        self.assertEqual(stars.RA[2], 75.998985)
        self.assertEqual(stars.Decl[0], -1.526383)
        self.assertEqual(stars.Decl[1], -1.15006)
        self.assertEqual(stars.Decl[2], -1.007737)
        self.assertEqual(stars.ObsMag[0], -99)
        self.assertEqual(stars.ObsMag[1], -99)
        self.assertEqual(stars.ObsMag[2], 17.112)
        self.assertEqual(stars.LSSTMag[0], 28.7005)
        self.assertEqual(stars.LSSTMag[1], 34.5597)
        self.assertEqual(stars.LSSTMag[2], 28.8231)
        
if __name__ == "__main__":
    unittest.main()