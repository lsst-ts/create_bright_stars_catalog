import pymssql
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
        
    def query(self, corner1, corner2, corner3, corner4):
        """
        Queries the database for stars within an area.
        
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
            above0Set = self.queryInternal(top, bottom, 0, left)
            below0Set = self.queryInternal(top, bottom, right, 360)
            return StarData.StarData(above0Set.RA + below0Set.RA, above0Set.Decl + below0Set.Decl, above0Set.ObsMagU + below0Set.ObsMagU, above0Set.ObsMagUNew + below0Set.ObsMagUNew, above0Set.LSSTMagU + below0Set.LSSTMagU, above0Set.LSSTMagUNoATM + below0Set.LSSTMagUNoATM, above0Set.ObsMagG + below0Set.ObsMagG, above0Set.ObsMagGNew + below0Set.ObsMagGNew, above0Set.LSSTMagG + below0Set.LSSTMagG, above0Set.LSSTMagGNoATM + below0Set.LSSTMagGNoATM, above0Set.ObsMagR + below0Set.ObsMagR, above0Set.ObsMagRNew + below0Set.ObsMagRNew, above0Set.LSSTMagR + below0Set.LSSTMagR, above0Set.LSSTMagRNoATM + below0Set.LSSTMagRNoATM, above0Set.ObsMagI + below0Set.ObsMagI, above0Set.ObsMagINew + below0Set.ObsMagINew, above0Set.LSSTMagI + below0Set.LSSTMagI, above0Set.LSSTMagINoATM + below0Set.LSSTMagINoATM, above0Set.ObsMagZ + below0Set.ObsMagZ, above0Set.ObsMagZNew + below0Set.ObsMagZNew, above0Set.LSSTMagZ + below0Set.LSSTMagZ, above0Set.LSSTMagZNoATM + below0Set.LSSTMagZNoATM, above0Set.ObsMagY + below0Set.ObsMagY, above0Set.ObsMagYNew + below0Set.ObsMagYNew, above0Set.LSSTMagY + below0Set.LSSTMagY, above0Set.LSSTMagYNoATM + below0Set.LSSTMagYNoATM)
        else:
            return self.queryInternal(top, bottom, left, right)
        
    def queryInternal(self, top, bottom, left, right):
        """
        Queries the database for stars within an area.
        
        @param top [in] The top edge of the box (Decl).
        
        @param bottom [in] The bottom edge of the box (Decl).
        
        @param left [in] The left edge of the box (RA).
        
        @param right [in] The right edge of the box (RA).
        """
        
        query = "SELECT ra, decl, sdssu, newSDSSu, umag, umag_noatm, sdssg, newSDSSg, gmag, gmag_noatm, sdssr, newSDSSr, rmag, rmag_noatm, sdssi, newSDSSi, imag, imag_noatm, sdssz, newSDSSz, zmag, zmag_noatm, ymag, ymag_noatm FROM bright_stars WHERE decl <= %f AND decl >= %f AND ra >= %f AND ra <= %f" % (top, bottom, left, right)
        self.cursor.execute(query)
        ra = []
        decl = []
        obsMagU = []
        obsMagUNew = []
        lsstMagU = []
        lsstMagUNoATM = []
        obsMagG = []
        obsMagGNew = []
        lsstMagG = []
        lsstMagGNoATM = []
        obsMagR = []
        obsMagRNew = []
        lsstMagR = []
        lsstMagRNoATM = []
        obsMagI = []
        obsMagINew = []
        lsstMagI = []
        lsstMagINoATM = []
        obsMagZ = []
        obsMagZNew = []
        lsstMagZ = []
        lsstMagZNoATM = []
        obsMagY = []
        obsMagYNew = []
        lsstMagY = []
        lsstMagYNoATM = []
        for item in self.cursor.fetchall():
            ra.append(item[0])
            decl.append(item[1])
            obsMagU.append(item[2])
            obsMagUNew.append(item[3])
            lsstMagU.append(item[4])
            lsstMagUNoATM.append(item[5])
            obsMagG.append(item[6])
            obsMagGNew.append(item[7])
            lsstMagG.append(item[8])
            lsstMagGNoATM.append(item[9])
            obsMagR.append(item[10])
            obsMagRNew.append(item[11])
            lsstMagR.append(item[12])
            lsstMagRNoATM.append(item[13])
            obsMagI.append(item[14])
            obsMagINew.append(item[15])
            lsstMagI.append(item[16])
            lsstMagINoATM.append(item[17])
            obsMagZ.append(item[18])
            obsMagZNew.append(item[19])
            lsstMagZ.append(item[20])
            lsstMagZNoATM.append(item[21])
            obsMagY.append(-99)
            obsMagYNew.append(-99)
            lsstMagY.append(item[22])
            lsstMagYNoATM.append(item[23])
        return StarData.StarData(ra, decl, obsMagU, obsMagUNew, lsstMagU, lsstMagUNoATM, obsMagG, obsMagGNew, lsstMagG, lsstMagGNoATM, obsMagR, obsMagRNew, lsstMagR, lsstMagRNoATM, obsMagI, obsMagINew, lsstMagI, lsstMagINoATM, obsMagZ, obsMagZNew, lsstMagZ, lsstMagZNoATM, obsMagY, obsMagYNew, lsstMagY, lsstMagYNoATM)
        
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
        stars = self.database.query([0.01, -1], [359.99, -2], [0.01, -1], [359.99, -2])
        print(stars.ObsMagUNew)
        print(stars.ObsMagU)
        print(stars.LSSTMagU)
        print(stars.LSSTMagUNoATM)
        
    def testUQuery(self):
        stars = self.database.query([75.998622, -1], [75.998622, -2], [75.998985, -1], [75.998985, -2])
        self.assertEqual(len(stars.RA), 3)
        self.assertEqual(len(stars.Decl), 3)
        self.assertEqual(len(stars.ObsMagU), 3)
        self.assertEqual(len(stars.LSSTMagU), 3)
        self.assertEqual(stars.RA[0], 75.998623)
        self.assertEqual(stars.RA[1], 75.998787)
        self.assertEqual(stars.RA[2], 75.998985)
        self.assertEqual(stars.Decl[0], -1.526383)
        self.assertEqual(stars.Decl[1], -1.15006)
        self.assertEqual(stars.Decl[2], -1.007737)
        self.assertEqual(stars.ObsMagU[0], 17.67646026611328)
        self.assertEqual(stars.ObsMagU[1], 24.178739547729492)
        self.assertEqual(stars.ObsMagU[2], 15.319310188293457)
        self.assertEqual(stars.LSSTMagU[0], 17.4837)
        self.assertEqual(stars.LSSTMagU[1], 24.45101)
        self.assertEqual(stars.LSSTMagU[2], 15.53796)
        self.assertEqual(stars.LSSTMagUNoATM[0], 17.56115)
        self.assertEqual(stars.LSSTMagUNoATM[1], 24.53801)
        self.assertEqual(stars.LSSTMagUNoATM[2], 15.6118)
        self.assertEqual(stars.ObsMagUNew[0], 17.68098)
        self.assertEqual(stars.ObsMagUNew[1], 24.6176)
        self.assertEqual(stars.ObsMagUNew[2], 15.73102)
        
if __name__ == "__main__":
    unittest.main()