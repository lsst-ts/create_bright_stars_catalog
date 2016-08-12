import unittest

PixelSizeInMM = 0.01

class StarData(object):
    def __init__(self, ra, decl, obsMagU, obsMagUNew, lsstMagU, lsstMagUNoATM, obsMagG, obsMagGNew, lsstMagG, lsstMagGNoATM, obsMagR, obsMagRNew, lsstMagR, lsstMagRNoATM, obsMagI, obsMagINew, lsstMagI, lsstMagINoATM, obsMagZ, obsMagZNew, lsstMagZ, lsstMagZNoATM, obsMagY, obsMagYNew, lsstMagY, lsstMagYNoATM):
        self.Detector = "" 
        self.RA = ra
        self.RAInPixel = []
        self.RAInMM = []
        self.Decl = decl
        self.DeclInPixel = []
        self.DeclInMM = []
        self.ObsMagU = obsMagU
        self.ObsMagUNew = obsMagUNew
        self.LSSTMagU = lsstMagU
        self.LSSTMagUNoATM = lsstMagUNoATM
        self.ObsMagG = obsMagG
        self.ObsMagGNew = obsMagGNew
        self.LSSTMagG = lsstMagG
        self.LSSTMagGNoATM = lsstMagGNoATM
        self.ObsMagR = obsMagR
        self.ObsMagRNew = obsMagRNew
        self.LSSTMagR = lsstMagR
        self.LSSTMagRNoATM = lsstMagRNoATM
        self.ObsMagI = obsMagI
        self.ObsMagINew = obsMagINew
        self.LSSTMagI = lsstMagI
        self.LSSTMagINoATM = lsstMagINoATM
        self.ObsMagZ = obsMagZ
        self.ObsMagZNew = obsMagZNew
        self.LSSTMagZ = lsstMagZ
        self.LSSTMagZNoATM = lsstMagZNoATM
        self.ObsMagY = obsMagY
        self.ObsMagYNew = obsMagYNew
        self.LSSTMagY = lsstMagY
        self.LSSTMagYNoATM = lsstMagYNoATM
        
    def populateDetector(self, detector):
        """
        Populates the detector information for this set of stars.
        
        @param detector [in] The name of the detector.
        """
        self.Detector = detector
        
    def populateRAData(self, raInPixel):
        """
        Populates the RA pixel and mm data for this set of stars.
        
        @param raInPixel [in] The ra pixel coordinate each star falls on the detector.
        """
        self.RAInPixel = raInPixel
        self.RAInMM = [x * PixelSizeInMM for x in self.RAInPixel]
        
    def populateDeclData(self, declInPixel):
        """
        Populates the Decl pixel and mm data for this set of stars.
        
        @param declInPixel [in] The decl pixel coordinate each star falls on the detector.
        """
        self.DeclInPixel = declInPixel
        self.DeclInMM = [x * PixelSizeInMM for x in self.DeclInPixel]
        
class StarDataTest(unittest.TestCase):
    stars = None
    
    def setUp(self):
        self.stars = StarData([1, 2, 3], [4, 5, 6], [100, 101, 102], [110, 111, 112], [120, 121, 122], [130, 131, 132], [200, 201, 202], [210, 211, 212], [220, 221, 222], [230, 231, 232], [300, 301, 302], [310, 311, 312], [320, 321, 322], [330, 331, 332], [400, 401, 402], [410, 411, 412], [420, 421, 422], [430, 431, 432], [500, 501, 502], [510, 511, 512], [520, 521, 522], [530, 531, 532], [600, 601, 602], [610, 611, 612], [620, 621, 622], [630, 631, 632])

    def testConstructor(self):
        self.assertEqual(self.stars.RA[0], 1)
        self.assertEqual(self.stars.RA[1], 2)
        self.assertEqual(self.stars.RA[2], 3)
        self.assertEqual(self.stars.Decl[0], 4)
        self.assertEqual(self.stars.Decl[1], 5)
        self.assertEqual(self.stars.Decl[2], 6)
        self.assertEqual(self.stars.ObsMagU[0], 100)
        self.assertEqual(self.stars.ObsMagU[1], 101)
        self.assertEqual(self.stars.ObsMagU[2], 102)
        self.assertEqual(self.stars.ObsMagUNew[0], 110)
        self.assertEqual(self.stars.ObsMagUNew[1], 111)
        self.assertEqual(self.stars.ObsMagUNew[2], 112)
        self.assertEqual(self.stars.LSSTMagU[0], 120)
        self.assertEqual(self.stars.LSSTMagU[1], 121)
        self.assertEqual(self.stars.LSSTMagU[2], 122)
        self.assertEqual(self.stars.LSSTMagUNoATM[0], 130)
        self.assertEqual(self.stars.LSSTMagUNoATM[1], 131)
        self.assertEqual(self.stars.LSSTMagUNoATM[2], 132)
        self.assertEqual(self.stars.ObsMagG[0], 200)
        self.assertEqual(self.stars.ObsMagG[1], 201)
        self.assertEqual(self.stars.ObsMagG[2], 202)
        self.assertEqual(self.stars.ObsMagGNew[0], 210)
        self.assertEqual(self.stars.ObsMagGNew[1], 211)
        self.assertEqual(self.stars.ObsMagGNew[2], 212)
        self.assertEqual(self.stars.LSSTMagG[0], 220)
        self.assertEqual(self.stars.LSSTMagG[1], 221)
        self.assertEqual(self.stars.LSSTMagG[2], 222)
        self.assertEqual(self.stars.LSSTMagGNoATM[0], 230)
        self.assertEqual(self.stars.LSSTMagGNoATM[1], 231)
        self.assertEqual(self.stars.LSSTMagGNoATM[2], 232)
        self.assertEqual(self.stars.ObsMagR[0], 300)
        self.assertEqual(self.stars.ObsMagR[1], 301)
        self.assertEqual(self.stars.ObsMagR[2], 302)
        self.assertEqual(self.stars.ObsMagRNew[0], 310)
        self.assertEqual(self.stars.ObsMagRNew[1], 311)
        self.assertEqual(self.stars.ObsMagRNew[2], 312)
        self.assertEqual(self.stars.LSSTMagR[0], 320)
        self.assertEqual(self.stars.LSSTMagR[1], 321)
        self.assertEqual(self.stars.LSSTMagR[2], 322)
        self.assertEqual(self.stars.LSSTMagRNoATM[0], 330)
        self.assertEqual(self.stars.LSSTMagRNoATM[1], 331)
        self.assertEqual(self.stars.LSSTMagRNoATM[2], 332)
        self.assertEqual(self.stars.ObsMagI[0], 400)
        self.assertEqual(self.stars.ObsMagI[1], 401)
        self.assertEqual(self.stars.ObsMagI[2], 402)
        self.assertEqual(self.stars.ObsMagINew[0], 410)
        self.assertEqual(self.stars.ObsMagINew[1], 411)
        self.assertEqual(self.stars.ObsMagINew[2], 412)
        self.assertEqual(self.stars.LSSTMagI[0], 420)
        self.assertEqual(self.stars.LSSTMagI[1], 421)
        self.assertEqual(self.stars.LSSTMagI[2], 422)
        self.assertEqual(self.stars.LSSTMagINoATM[0], 430)
        self.assertEqual(self.stars.LSSTMagINoATM[1], 431)
        self.assertEqual(self.stars.LSSTMagINoATM[2], 432)
        self.assertEqual(self.stars.ObsMagZ[0], 500)
        self.assertEqual(self.stars.ObsMagZ[1], 501)
        self.assertEqual(self.stars.ObsMagZ[2], 502)
        self.assertEqual(self.stars.ObsMagZNew[0], 510)
        self.assertEqual(self.stars.ObsMagZNew[1], 511)
        self.assertEqual(self.stars.ObsMagZNew[2], 512)
        self.assertEqual(self.stars.LSSTMagZ[0], 520)
        self.assertEqual(self.stars.LSSTMagZ[1], 521)
        self.assertEqual(self.stars.LSSTMagZ[2], 522)
        self.assertEqual(self.stars.LSSTMagZNoATM[0], 530)
        self.assertEqual(self.stars.LSSTMagZNoATM[1], 531)
        self.assertEqual(self.stars.LSSTMagZNoATM[2], 532)
        self.assertEqual(self.stars.ObsMagY[0], 600)
        self.assertEqual(self.stars.ObsMagY[1], 601)
        self.assertEqual(self.stars.ObsMagY[2], 602)
        self.assertEqual(self.stars.ObsMagYNew[0], 610)
        self.assertEqual(self.stars.ObsMagYNew[1], 611)
        self.assertEqual(self.stars.ObsMagYNew[2], 612)
        self.assertEqual(self.stars.LSSTMagY[0], 620)
        self.assertEqual(self.stars.LSSTMagY[1], 621)
        self.assertEqual(self.stars.LSSTMagY[2], 622)
        self.assertEqual(self.stars.LSSTMagYNoATM[0], 630)
        self.assertEqual(self.stars.LSSTMagYNoATM[1], 631)
        self.assertEqual(self.stars.LSSTMagYNoATM[2], 632)
        
    def testDetector(self):
        self.stars.populateDetector("Foobar")
        self.assertEqual(self.stars.Detector, "Foobar")
    
    def testRAData(self):
        self.stars.populateRAData([10, 20, 30])
        self.assertEqual(self.stars.RAInPixel[0], 10)
        self.assertEqual(self.stars.RAInPixel[1], 20)
        self.assertEqual(self.stars.RAInPixel[2], 30)
        self.assertEqual(self.stars.RAInMM[0], 10 * PixelSizeInMM)
        self.assertEqual(self.stars.RAInMM[1], 20 * PixelSizeInMM)
        self.assertEqual(self.stars.RAInMM[2], 30 * PixelSizeInMM)
    
    def testDeclData(self):
        self.stars.populateDeclData([40, 50, 60])
        self.assertEqual(self.stars.DeclInPixel[0], 40)
        self.assertEqual(self.stars.DeclInPixel[1], 50)
        self.assertEqual(self.stars.DeclInPixel[2], 60)
        self.assertEqual(self.stars.DeclInMM[0], 40 * PixelSizeInMM)
        self.assertEqual(self.stars.DeclInMM[1], 50 * PixelSizeInMM)
        self.assertEqual(self.stars.DeclInMM[2], 60 * PixelSizeInMM)
        
if __name__ == "__main__":
    unittest.main()