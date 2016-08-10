import pymssql
import StarData
import unittest
import numpy

FilterU = "u"
FilterG = "g"
FilterR = "r"
FilterI = "i"
FilterZ = "z"
FilterY = "y"

stddevSplit = 20.0

class BrightStarDatabase(object):
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self, host, user, password, database):
        """
        Connects to the database.
        
        @param host [in] The host name / ip and port of the database.
                
        @param user [in] The user name to connect as.
        
        @param password [in] The password for the user.
        
        @param database [in] The database to use.
        """
        self.connection = pymssql.connect(host, user, password, database)
        self.cursor = self.connection.cursor()
        
    def query(self, filter, corner1, corner2, corner3, corner4):
        """
        Queries the database for stars within an area.
        
        @param filter [in] The filter to query.
        Valid values are (u, g, r, i, z, y).
        
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
            return StarData.StarData(above0Set.RA + below0Set.RA, above0Set.Decl + below0Set.Decl, above0Set.ObsMag + below0Set.ObsMag, above0Set.LSSTMag + below0Set.LSSTMag)
        else:
            return self.queryInternal(filter, top, bottom, left, right)
        
    def queryInternal(self, filter, top, bottom, left, right):
        """
        Queries the database for stars within an area.
        
        @param filter [in] The filter to query.
        Valid values are (u, g, r, i, z, y).
        
        @param top [in] The top edge of the box (Decl).
        
        @param bottom [in] The bottom edge of the box (Decl).
        
        @param left [in] The left edge of the box (RA).
        
        @param right [in] The right edge of the box (RA).
        """
        
        query = "SELECT ra, decl, sdss%s, newSDSS%s, %smag, %smag_noatm FROM bright_stars WHERE decl <= %f AND decl >= %f AND ra >= %f AND ra <= %f" % (filter, filter, filter, filter, top, bottom, left, right)
        if filter is FilterY:
            query = "SELECT ra, decl, %smag, %smag_noatm FROM bright_stars WHERE decl <= %f AND decl >= %f AND ra >= %f AND ra <= %f" % (filter, filter, top, bottom, left, right)
        self.cursor.execute(query)
        ra = []
        decl = []
        obsMag = []
        obsMagNew = []
        lsstMag = []
        lsstMagNoATM = []
        for item in self.cursor.fetchall():
            ra.append(item[0])
            decl.append(item[1])
            if filter is FilterY:
                obsMag.append(-99)
                obsMagNew.append(-99)
                lsstMag.append(item[2])
                lsstMagNoATM.append(item[3])
            else:
                obsMag.append(item[2])
                obsMagNew.append(item[3])
                lsstMag.append(item[4])
                lsstMagNoATM.append(item[5])
        return StarData.StarData(ra, decl, obsMag, obsMagNew, lsstMag, lsstMagNoATM)
        
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
    brightStarDatabaseHost = "localhost:51433"
    brightStarDatabaseUser = "LSST-2"
    brightStarDatabasePassword = "L$$TUser"
    brightStarDatabaseDatabase = "LSSTCATSIM"
    database = None
    
    def setUp(self):
        self.database = BrightStarDatabase()
        self.database.connect(self.brightStarDatabaseHost, self.brightStarDatabaseUser, self.brightStarDatabasePassword, self.brightStarDatabaseDatabase)
        
    def tearDown(self):
        self.database.disconnect()
        
    def testFoobar(self):
        stars = self.database.query(FilterY, [75.998622, -1], [75.998622, -2], [75.998985, -1], [75.998985, -2])
        print stars.ObsMagNew
        print stars.ObsMag
        print stars.LSSTMag
        print stars.LSSTMagNoATM
        
    def testUQuery(self):
        stars = self.database.query(FilterU, [75.998622, -1], [75.998622, -2], [75.998985, -1], [75.998985, -2])
        self.assertEqual(len(stars.RA), 3)
        self.assertEqual(len(stars.Decl), 3)
        self.assertEqual(len(stars.ObsMag), 3)
        self.assertEqual(len(stars.LSSTMag), 3)
        self.assertEqual(stars.RA[0], 75.998623)
        self.assertEqual(stars.RA[1], 75.998787)
        self.assertEqual(stars.RA[2], 75.998985)
        self.assertEqual(stars.Decl[0], -1.526383)
        self.assertEqual(stars.Decl[1], -1.15006)
        self.assertEqual(stars.Decl[2], -1.007737)
        self.assertEqual(stars.ObsMag[0], 17.67646026611328)
        self.assertEqual(stars.ObsMag[1], 24.178739547729492)
        self.assertEqual(stars.ObsMag[2], 15.319310188293457)
        self.assertEqual(stars.LSSTMag[0], 17.4837)
        self.assertEqual(stars.LSSTMag[1], 24.45101)
        self.assertEqual(stars.LSSTMag[2], 15.53796)
        self.assertEqual(stars.LSSTMagNoATM[0], 17.56115)
        self.assertEqual(stars.LSSTMagNoATM[1], 24.53801)
        self.assertEqual(stars.LSSTMagNoATM[2], 15.6118)
        self.assertEqual(stars.ObsMagNew[0], 17.68098)
        self.assertEqual(stars.ObsMagNew[1], 24.6176)
        self.assertEqual(stars.ObsMagNew[2], 15.73102)
        
if __name__ == "__main__":
    unittest.main()